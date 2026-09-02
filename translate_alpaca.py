import json
import random
from deep_translator import GoogleTranslator

# ---------- CONFIG ----------
NUM_EXAMPLES = 1000          # translate 1000 examples (adjust if you hit rate limit)
INPUT_FILE = "train.jsonl"   # your existing train set (we'll keep it)
OUTPUT_FILE = "augmented_train.jsonl"

# Download a small Alpaca sample (we'll use the dataset from Hugging Face)
# If you don't have datasets installed, install: pip install datasets
try:
    from datasets import load_dataset
except ImportError:
    print("Please install datasets: pip install datasets")
    exit()

print("📥 Loading Alpaca dataset...")
alpaca = load_dataset("tatsu-lab/alpaca", split="train")
# Shuffle and pick a subset
selected = alpaca.shuffle(seed=42).select(range(NUM_EXAMPLES))

translator = GoogleTranslator(source='en', target='ha')

def translate_text(text):
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"  ⚠️ Translation error: {e}")
        return text  # fallback to English (better than failing)

augmented = []

# Load your existing train.jsonl
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    existing = [json.loads(line) for line in f]
augmented.extend(existing)

print(f"📚 Existing: {len(existing)} pairs")

# Translate each Alpaca example
for i, example in enumerate(selected):
    # Alpaca fields: instruction, input, output
    instr = example["instruction"]
    inp = example["input"]
    out = example["output"]
    
    # Combine instruction and input if input exists
    if inp:
        full_instr = f"{instr} {inp}"
    else:
        full_instr = instr
    
    # Translate
    hausa_instr = translate_text(full_instr)
    hausa_out = translate_text(out)
    
    if hausa_instr and hausa_out:
        augmented.append({
            "instruction": hausa_instr,
            "input": "",
            "output": hausa_out,
            "source": "translated_alpaca"
        })
    
    if (i+1) % 50 == 0:
        print(f"  Translated {i+1} examples...")
        # sleep a bit to avoid rate limiting
        import time
        time.sleep(1)

print(f"✅ Total augmented pairs: {len(augmented)}")

# Shuffle and save
random.shuffle(augmented)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for item in augmented:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"💾 Saved to {OUTPUT_FILE}")