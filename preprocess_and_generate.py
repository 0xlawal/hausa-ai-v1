import json
import re
import random
from datetime import datetime
from collections import Counter

# ---------- CLEANING ----------
def clean_hausa_text(text):
    """Remove HTML, extra spaces, normalise diacritics."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Replace multiple spaces/newlines with single space
    text = re.sub(r'\s+', ' ', text).strip()
    # Normalise Hausa special chars (ensure ɓ, ɗ, ƙ, ʼy are consistent)
    # (most sites use these, but we keep them as-is)
    return text

# ---------- TEMPLATES ----------
# Each template: (instruction, response_generator)
# response_generator takes the article dict and returns a string
TEMPLATES = [
    {
        "instruction": "Taƙaita wannan labarin a cikin jimloli ɗaya ko biyu.",
        "response": lambda art: clean_hausa_text(art["title"])  # title is a decent summary
    },
    {
        "instruction": "Menene babban jigon wannan labarin?",
        "response": lambda art: clean_hausa_text(art["text"][:300])  # first 300 chars
    },
    {
        "instruction": "Me ya faru a wannan labarin? Ka ba da taƙaitaccen bayani.",
        "response": lambda art: clean_hausa_text(art["text"][:500])
    },
    {
        "instruction": "Ka ba ni taken da ya dace da wannan labarin.",
        "response": lambda art: clean_hausa_text(art["title"])
    },
    {
        "instruction": "Ka sake rubuta wannan labarin cikin sauƙi, don yara su fahimta.",
        "response": lambda art: clean_hausa_text(art["text"][:400])  # simplified = shorter
    }
]

# ---------- MAIN ----------
def generate_instruction_pairs(articles):
    pairs = []
    for art in articles:
        text = art.get("text", "")
        if len(text) < 100:  # skip very short entries
            continue
        for template in TEMPLATES:
            instr = template["instruction"]
            resp = template["response"](art)
            if len(resp) < 20:
                continue
            pairs.append({
                "instruction": instr,
                "input": "",  # we don't use separate input for news summarisation
                "output": resp,
                "source": art.get("source", "unknown")
            })
    return pairs

def split_data(pairs, train_ratio=0.8, val_ratio=0.1):
    random.shuffle(pairs)
    n = len(pairs)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    return {
        "train": pairs[:train_end],
        "val": pairs[train_end:val_end],
        "test": pairs[val_end:]
    }

if __name__ == "__main__":
    # Load raw articles
    with open("hausa_news_raw.json", "r", encoding="utf-8") as f:
        articles = json.load(f)
    
    print(f"📰 Loaded {len(articles)} articles")
    
    # Clean each article text
    for art in articles:
        art["text"] = clean_hausa_text(art["text"])
    
    # Generate instruction pairs
    pairs = generate_instruction_pairs(articles)
    print(f"📝 Generated {len(pairs)} instruction-response pairs")
    
    # Split
    splits = split_data(pairs)
    for name, data in splits.items():
        out_file = f"{name}.jsonl"
        with open(out_file, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"💾 {name}: {len(data)} pairs → {out_file}")
    
    print("✅ Preprocessing complete!")