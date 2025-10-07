#!/usr/bin/env python
import pandas as pd
from gtts import gTTS
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[1]
enriched = ROOT/"out/enriched.csv"
media_dir = ROOT/"out/media"
media_dir.mkdir(parents=True, exist_ok=True)

tts_lang = os.getenv("TTS_LANG","en")

def safe(name: str) -> str:
    # keep it predictable for Windows/macOS/Anki
    return re.sub(r"[^a-zA-Z0-9_+-]+", "_", name.strip())[:80]

df = pd.read_csv(enriched)

# (1) word audio
for word in df["Word"].dropna().unique():
    mp3 = media_dir / f"{safe(word)}.mp3"
    if not mp3.exists():
        gTTS(text=word, lang=tts_lang).save(mp3.as_posix())
        print("Saved", mp3)

# (2) example audio per row (uses Example_EN)
changed = False
for i, r in df.iterrows():
    word = str(r.get("Word","")).strip()
    ex   = str(r.get("Example_EN","")).strip()
    if not word or not ex:
        continue
    ex_mp3 = media_dir / f"{safe(word)}__ex.mp3"
    if not ex_mp3.exists():
        gTTS(text=ex, lang=tts_lang).save(ex_mp3.as_posix())
        print("Saved", ex_mp3)
    ex_tag = f"[sound:{ex_mp3.name}]"
    if str(r.get("Example_Sound","")).strip() != ex_tag:
        df.at[i, "Example_Sound"] = ex_tag
        changed = True

if changed:
    df.to_csv(enriched, index=False, encoding="utf-8-sig")
    print("Updated CSV with Example_Sound tags.")
print("Done.")

