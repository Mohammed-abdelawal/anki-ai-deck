#!/usr/bin/env python
import pandas as pd
from gtts import gTTS
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
enriched = ROOT/"out/enriched.csv"
media_dir = ROOT/"out/media"
media_dir.mkdir(parents=True, exist_ok=True)

tts_lang = os.getenv("TTS_LANG","en")

df = pd.read_csv(enriched)
for word in df["Word"].dropna().unique():
    mp3 = media_dir / f"{word}.mp3"
    if mp3.exists():
        continue
    tts = gTTS(text=word, lang=tts_lang)
    tts.save(mp3.as_posix())
    print("Saved", mp3)
print("Done.")
