#!/usr/bin/env python
import os, json, pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

# Accept either DeepSeek_* or OPENAI_* names (GH Actions secrets friendly)
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL") or "https://api.deepseek.com"
MODEL = "deepseek-chat"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

system = (ROOT / "prompts/system.txt").read_text(encoding="utf-8")
in_path = ROOT / "data/words.csv"
out_path = ROOT / "out/enriched.csv"
out_path.parent.mkdir(parents=True, exist_ok=True)

cols = [
    "Word","Meaning_EN","Meaning_AR","IPA","Part_of_Speech","Example_EN","Example_AR",
    "Collocations","Synonyms","Antonyms","Notes","Tags","Sound"
]

def _ensure_fields(d: dict) -> dict:
    for k in ["Meaning_EN","IPA","Part_of_Speech","Example_EN","Example_AR","Collocations","Synonyms","Antonyms","Notes","Tags"]:
        d.setdefault(k, "")
    return d

def ask_ai(word_en: str, word_ar: str, existing: dict) -> dict:
    existing_fields = json.dumps(existing, ensure_ascii=False, indent=2)
    user = (ROOT / "prompts/user_template.txt").read_text(encoding="utf-8").format(
        word_en=word_en, word_ar=word_ar, existing_fields=existing_fields
    )

    # Use RESPONSES API for deepseek-reasoner; CHAT COMPLETIONS otherwise
    if MODEL.startswith("deepseek-reasoner"):
        # Responses API
        resp = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            reasoning={"effort": "medium"},
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        # Pull the text output (SDK puts final text in output_text)
        content_text = resp.output_text
    else:
        # Chat Completions API (deepseek-chat, gpt-* etc.)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        content_text = resp.choices[0].message.content

    data = json.loads(content_text)
    return _ensure_fields(data)

def main():
    df_in = pd.read_csv(in_path)
    rows = []
    for _, r in df_in.iterrows():
        word = str(r.get("word_en","")).strip()
        ar = str(r.get("word_ar","")).strip()
        if not word:
            continue

        data = ask_ai(word, ar, existing={})
        rows.append({
            "Word": word,
            "Meaning_EN": data.get("Meaning_EN",""),
            "Meaning_AR": ar or data.get("Meaning_AR",""),
            "IPA": data.get("IPA",""),
            "Part_of_Speech": data.get("Part_of_Speech",""),
            "Example_EN": data.get("Example_EN",""),
            "Example_AR": data.get("Example_AR",""),
            "Collocations": data.get("Collocations",""),
            "Synonyms": data.get("Synonyms",""),
            "Antonyms": data.get("Antonyms",""),
            "Notes": data.get("Notes",""),
            "Tags": data.get("Tags",""),
            "Sound": f"[sound:{word}.mp3]",
        })

    pd.DataFrame(rows, columns=cols).to_csv(out_path, index=False, encoding="utf-8-sig")
    print("Wrote", out_path)

if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit("Missing API key: set DEEPSEEK_API_KEY or OPENAI_API_KEY")
    main()

