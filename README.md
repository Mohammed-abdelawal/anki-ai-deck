# anki-ai-deck
Generate Anki/AnkiDroid vocab decks from a simple EN/AR list using AI and TTS.

## What it does
1) You put words in `data/words.csv` (English/Arabic).
2) `scripts/ai_enrich.py` fills meanings, IPA, POS, examples, collocations, synonyms, antonyms, notes, tags using an OpenAI-compatible API.
3) `scripts/tts.py` generates MP3 pronunciations with gTTS (or skip/use your own).
4) `scripts/build_deck.py` assembles an `.apkg` with rich templates + audio.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1) add words
# edit data/words.csv

# 2) enrich using AI (set your API key)
export OPENAI_API_KEY=sk-...                         # Windows PowerShell: $env:OPENAI_API_KEY="sk-..."
# Optional: use an OpenAI-compatible endpoint/model
# export OPENAI_BASE_URL="https://api.openai.com/v1"
# export OPENAI_MODEL="gpt-4o-mini"

python scripts/ai_enrich.py

# 3) generate audio (optional)
python scripts/tts.py

# 4) build deck
python scripts/build_deck.py

# Output:
# out/deck.apkg  (import into Anki/AnkiDroid)
```

## CSV format
`data/words.csv`
```
word_en,word_ar
meticulous,دقيق جدًا
pragmatic,عملي
```

After enrichment, you’ll get `out/enriched.csv` with:
```
Word,Meaning_EN,Meaning_AR,IPA,Part_of_Speech,Example_EN,Example_AR,Collocations,Synonyms,Antonyms,Notes,Tags,Sound
...
```

## Notes
- The AI step respects any field you already filled; it only fills blanks.
- Audio uses **gTTS** (internet required). You can replace with other TTS or human recordings—just drop `word.mp3` files into `out/media/` and set the `Sound` field to `[sound:word.mp3]`.
- `build_deck.py` uses `genanki`, so no desktop UI is required to create the deck.
