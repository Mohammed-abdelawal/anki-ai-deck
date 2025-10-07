#!/usr/bin/env python
import pandas as pd
from pathlib import Path
import genanki, time, html

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "out/enriched.csv"
MEDIA_DIR = ROOT / "out/media"
OUT_APKG = ROOT / "out/deck.apkg"

df = pd.read_csv(CSV)

# ---------- helpers ----------
def chips_html(s: str) -> str:
    """Turn 'a, b, c' into '<span class="chip">a</span> <span class="chip">b</span> ...'"""
    if not isinstance(s, str) or not s.strip():
        return ""
    items = [x.strip() for x in s.split(",") if x.strip()]
    # escape content to avoid breaking HTML, then wrap
    return " ".join(f'<span class="chip">{html.escape(x)}</span>' for x in items)

def safe_str(v) -> str:
    return "" if v is None else str(v)

# ---------- model (CSS + templates) ----------
css = r"""
:root {
  --bg: #ffffff;
  --fg: #0f172a;
  --muted: #475569;
  --divider: #e2e8f0;
  --card: #f8fafc;
  --accent: #2563eb;
  --accent-weak: #dbeafe;
  --chip-bg: #eef2ff;
  --chip-fg: #4338ca;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0b0f17;
    --fg: #e5e7eb;
    --muted: #94a3b8;
    --divider: #1f2937;
    --card: #0f172a;
    --accent: #60a5fa;
    --accent-weak: #1e293b;
    --chip-bg: #111827;
    --chip-fg: #93c5fd;
  }
}
.card { background: var(--bg); color: var(--fg); font-family: ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial; font-size: 18px; line-height: 1.45; padding: 16px 18px; }
.word { font-size: 1.6rem; font-weight: 700; letter-spacing: .2px; }
.ipa { color: var(--muted); font-size: .95rem; margin-left: .5rem; }
.cardbox { background: var(--card); border: 1px solid var(--divider); border-radius: 12px; padding: 12px 14px; margin: 12px 0; }
.section-title { color: var(--muted); font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 6px; }
.kv { margin: 6px 0; }
.kv b { color: var(--fg); }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.chip { background: var(--chip-bg); color: var(--chip-fg); border: 1px solid var(--divider); border-radius: 999px; padding: 4px 10px; font-size: .85rem; }
.rule { height: 1px; background: linear-gradient(90deg,transparent,var(--divider),transparent); margin: 10px 0; }
.accent { height: 3px; background: var(--accent); opacity: .25; border-radius: 999px; margin: 8px 0 12px; }
.rtl { direction: rtl; text-align: right; }
.muted { color: var(--muted); }
.audio { margin-top: 6px; }
"""

qfmt = r"""<div class="word">{{Word}}</div>
{{#IPA}}<span class="ipa">/{{IPA}}/</span>{{/IPA}}
<div class="accent"></div>
{{Sound}}"""

afmt = r"""{{FrontSide}}
<div class="rule"></div>

<div class="cardbox">
  <div class="section-title">Meaning</div>
  <div class="kv"><b>{{Meaning_EN}}</b></div>
  <div class="kv rtl">{{Meaning_AR}}</div>
</div>

<div class="cardbox">
  <div class="section-title">Details</div>
  {{#Part_of_Speech}}<div class="kv"><b>Part of speech:</b> {{Part_of_Speech}}</div>{{/Part_of_Speech}}
  {{#IPA}}<div class="kv"><b>IPA:</b> /{{IPA}}/</div>{{/IPA}}
</div>

<div class="cardbox">
  <div class="section-title">Example</div>
  {{#Example_EN}}<div class="kv"><b>Example:</b> {{Example_EN}}</div>{{/Example_EN}}
  {{#Example_AR}}<div class="kv rtl"><b>مثال:</b> {{Example_AR}}</div>{{/Example_AR}}
  {{Example_Sound}}
</div>

{{#Collocations}}
<div class="cardbox">
  <div class="section-title">Collocations</div>
  <div class="chips">{{Collocations}}</div>
</div>
{{/Collocations}}

{{#Synonyms}}
<div class="cardbox">
  <div class="section-title">Synonyms</div>
  <div class="chips">{{Synonyms}}</div>
</div>
{{/Synonyms}}

{{#Antonyms}}
<div class="cardbox">
  <div class="section-title">Antonyms</div>
  <div class="chips">{{Antonyms}}</div>
</div>
{{/Antonyms}}

{{#Notes}}
<div class="cardbox">
  <div class="section-title">Notes</div>
  <div class="kv">{{Notes}}</div>
</div>
{{/Notes}}

{{#Tags}}
<div class="muted" style="margin-top:8px;"><b>Tags:</b> {{Tags}}</div>
{{/Tags}}"""

model_id = 1607392319 + int(time.time()) % 100000
my_model = genanki.Model(
    model_id,
    "Vocab EN-AR Model",
    fields=[
        {"name": "Word"},
        {"name": "Meaning_EN"},
        {"name": "Meaning_AR"},
        {"name": "IPA"},
        {"name": "Part_of_Speech"},
        {"name": "Example_EN"},
        {"name": "Example_AR"},
        {"name": "Collocations"},   # will contain HTML chips
        {"name": "Synonyms"},       # will contain HTML chips
        {"name": "Antonyms"},       # will contain HTML chips
        {"name": "Notes"},
        {"name": "Tags"},
        {"name": "Sound"},
        {"name": "Example_Sound"},
    ],
    templates=[
        {"name": "Card 1", "qfmt": qfmt, "afmt": afmt},
        # You can add a Reverse card type here if you like
    ],
    css=css,
)

deck_name = "Vocab EN-AR"
deck_id = 2087654321
deck = genanki.Deck(deck_id, deck_name)

pkg = genanki.Package(deck)
pkg.media_files = []

# ---------- build notes ----------
for _, r in df.iterrows():
    word = safe_str(r.get("Word"))
    note = genanki.Note(
        model=my_model,
        fields=[
            word,
            safe_str(r.get("Meaning_EN")),
            safe_str(r.get("Meaning_AR")),
            safe_str(r.get("IPA")),
            safe_str(r.get("Part_of_Speech")),
            safe_str(r.get("Example_EN")),
            safe_str(r.get("Example_AR")),
            chips_html(safe_str(r.get("Collocations"))),  # chips!
            chips_html(safe_str(r.get("Synonyms"))),      # chips!
            chips_html(safe_str(r.get("Antonyms"))),      # chips!
            safe_str(r.get("Notes")),
            safe_str(r.get("Tags")),
            safe_str(r.get("Sound")),            # e.g. [sound:word.mp3]
            safe_str(r.get("Example_Sound")),    # e.g. [sound:word__ex.mp3]
        ],
    )
    deck.add_note(note)

    # collect media if present
    # (Anki will embed whatever files we list in media_files)
    mp3_word = MEDIA_DIR / f"{word}.mp3"
    mp3_ex   = MEDIA_DIR / f"{word}__ex.mp3"
    if mp3_word.exists():
        pkg.media_files.append(mp3_word.as_posix())
    if mp3_ex.exists():
        pkg.media_files.append(mp3_ex.as_posix())

# ---------- write package ----------
OUT_APKG.parent.mkdir(parents=True, exist_ok=True)
pkg.write_to_file(OUT_APKG.as_posix())
print("Wrote", OUT_APKG)

