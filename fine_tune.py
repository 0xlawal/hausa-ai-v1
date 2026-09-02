import json
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset

# ---------- CONFIG ----------
MODEL_NAME = "NousResearch/Nous-Hermes-2-7B"   # Hugging Face ID
OUTPUT_DIR = "./hausa_lora"
MAX_LENGTH = 512
BATCH_SIZE = 4
GRAD_ACCUM = 4   # effective batch = 16
EPOCHS = 3
LEARNING_RATE = 2e-4

# ---------- LOAD DATA ----------
def load_jsonl(file):
    data = []
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return data

train_data = load_jsonl("train.jsonl")
val_data = load_jsonl("val.jsonl")

# Format for chat model: "### Instruction: ... ### Response: ..."
def format_example(example):
    return f"### Instruction: {example['instruction']}\n### Response: {example['output']}"

train_texts = [format_example(x) for x in train_data]
val_texts = [format_example(x) for x in val_data]

# ---------- TOKENIZER ----------
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=MAX_LENGTH,
        padding="max_length",
        return_tensors="pt"
    )

train_dataset = Dataset.from_dict({"text": train_texts}).map(tokenize_function, batched=True)
val_dataset = Dataset.from_dict({"text": val_texts}).map(tokenize_function, batched=True)

# ---------- MODEL (4-bit) ----------
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)
model = prepare_model_for_kbit_training(model)

# ---------- LORA ----------
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # ~0.1% of parameters

# ---------- TRAINING ----------
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM,
    num_train_epochs=EPOCHS,
    learning_rate=LEARNING_RATE,
    fp16=True,
    logging_steps=10,
    save_steps=50,
    eval_steps=50,
    evaluation_strategy="steps",
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8)
)

trainer.train()

# Save adapter
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"✅ Model saved to {OUTPUT_DIR}")