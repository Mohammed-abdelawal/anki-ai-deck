#!/usr/bin/env python
import os, json, pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT/".env")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))

system = (ROOT/"prompts/system.txt").read_text(encoding="utf-8")

in_path = ROOT/"data/words.csv"
out_path = ROOT/"out/enriched.csv"
out_path.parent.mkdir(parents=True, exist_ok=True)

cols = ["Word","Meaning_EN","Meaning_AR","IPA","Part_of_Speech","Example_EN","Example_AR",
        "Collocations","Synonyms","Antonyms","Notes","Tags","Sound"]

def ask_ai(word_en, word_ar, existing):
    existing_fields = json.dumps(existing, ensure_ascii=False, indent=2)
    user = (ROOT/"prompts/user_template.txt").read_text(encoding="utf-8").format(
        word_en=word_en, word_ar=word_ar, existing_fields=existing_fields
    )

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role":"system","content":system},
            {"role":"user","content":user}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    data = json.loads(resp.choices[0].message.content)
    for k in ["Meaning_EN","IPA","Part_of_Speech","Example_EN","Example_AR","Collocations","Synonyms","Antonyms","Notes","Tags"]:
        data.setdefault(k, "")
    return data

def main():
    df_in = pd.read_csv(in_path)
    rows = []
    for _, r in df_in.iterrows():
        word = str(r.get("word_en","")).strip()
        ar = str(r.get("word_ar","")).strip()
        if not word:
            continue

        existing = {}
        data = ask_ai(word, ar, existing)

        row = {
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
            "Sound": f"[sound:{word}.mp3]"
        }
        rows.append(row)

    df = pd.DataFrame(rows, columns=cols)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print("Wrote", out_path)

if __name__ == "__main__":
    main()
