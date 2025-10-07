#!/usr/bin/env python
import pandas as pd
from pathlib import Path
import genanki, time

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT/"out/enriched.csv")

deck_name = "Vocab EN-AR"
deck_id = 2087654321  # change if you like
model_id = 1607392319 + int(time.time()) % 100000  # avoid collisions

my_model = genanki.Model(
  model_id,
  'Vocab EN-AR Model',
  fields=[
    {'name': 'Word'},
    {'name': 'Meaning_EN'},
    {'name': 'Meaning_AR'},
    {'name': 'IPA'},
    {'name': 'Part_of_Speech'},
    {'name': 'Example_EN'},
    {'name': 'Example_AR'},
    {'name': 'Collocations'},
    {'name': 'Synonyms'},
    {'name': 'Antonyms'},
    {'name': 'Notes'},
    {'name': 'Tags'},
    {'name': 'Sound'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Word}} {{#IPA}}<div style="font-size:0.9em;color:#777">{{IPA}}</div>{{/IPA}}<br>{{Sound}}',
      'afmt': '{{FrontSide}}<hr id="answer">\n'
              '<div><b>{{Meaning_EN}}</b></div>\n'
              '<div dir="rtl">{{Meaning_AR}}</div>\n'
              '<hr>\n'
              '<div><b>{{Part_of_Speech}}</b></div>\n'
              '<div><b>Example:</b> {{Example_EN}}</div>\n'
              '<div dir="rtl"><b>مثال:</b> {{Example_AR}}</div>\n'
              '{{#Collocations}}<div><b>Collocations:</b> {{Collocations}}</div>{{/Collocations}}\n'
              '{{#Synonyms}}<div><b>Synonyms:</b> {{Synonyms}}</div>{{/Synonyms}}\n'
              '{{#Antonyms}}<div><b>Antonyms:</b> {{Antonyms}}</div>{{/Antonyms}}\n'
              '{{#Notes}}<div><b>Notes:</b> {{Notes}}</div>{{/Notes}}',
    },
    {
      'name': 'Reverse',
      'qfmt': '{{Meaning_EN}}<br><div dir="rtl">{{Meaning_AR}}</div>',
      'afmt': '{{FrontSide}}<hr id="answer">{{Word}} {{#IPA}}<div style="font-size:0.9em;color:#777">{{IPA}}</div>{{/IPA}}<br>{{Sound}}',
    },
  ],
  css='.card { font-family: ui-sans-serif, Arial; font-size: 18px; text-align: left; }\n'
      '.card[dir="rtl"] { text-align: right; }\n'
      'hr { margin: 10px 0; }'
)

deck = genanki.Deck(deck_id, deck_name)
pkg = genanki.Package(deck)
pkg.media_files = []

media_dir = ROOT/"out/media"
for _, r in df.iterrows():
    note = genanki.Note(
        model=my_model,
        fields=[
            str(r.get('Word','')),
            str(r.get('Meaning_EN','')),
            str(r.get('Meaning_AR','')),
            str(r.get('IPA','')),
            str(r.get('Part_of_Speech','')),
            str(r.get('Example_EN','')),
            str(r.get('Example_AR','')),
            str(r.get('Collocations','')),
            str(r.get('Synonyms','')),
            str(r.get('Antonyms','')),
            str(r.get('Notes','')),
            str(r.get('Tags','')),
            str(r.get('Sound','')),
        ]
    )
    deck.add_note(note)

    word = str(r.get('Word','')).strip()
    mp3 = media_dir / f"{word}.mp3"
    if mp3.exists():
        pkg.media_files.append(mp3.as_posix())

out_apkg = ROOT/"out/deck.apkg"
pkg.write_to_file(out_apkg.as_posix())
print("Wrote", out_apkg)
