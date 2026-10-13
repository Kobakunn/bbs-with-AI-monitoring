# moderation_model.py
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = Path(__file__).resolve().parent / "models" / "toxic-bert"

# アプリ起動時に一度だけ読み込む
tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
model = AutoModelForSequenceClassification.from_pretrained(
    str(MODEL_DIR)
)

model.eval()


def predict_toxicity(text: str) -> dict:
    """投稿文を分類し、有害クラスの確率を返す。"""

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256,
        padding=True,
    )

    with torch.inference_mode():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=-1)[0]

    toxic_probability = float(probabilities[1].item())

    return {
        "toxic_probability": toxic_probability,
        "is_toxic": toxic_probability >= 0.5,
    }