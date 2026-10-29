# moderation_model.py
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = (
    Path(__file__).resolve().parent
    / "models"
    / "toxic-bert-multiclass"
)

# 学習時と同じカテゴリ順にする
CATEGORIES = [
    "適切",
    "卑語",
    "差別",
    "誹謗中傷",
    "猥褻",
    "出会い・プライバシー侵害",
    "違法行為",
    "偏向表現",
]

# まずは全カテゴリで閾値0.5を使用
THRESHOLD = 0.5

# アプリ起動時に一度だけ読み込む
tokenizer = AutoTokenizer.from_pretrained(
    str(MODEL_DIR),
    use_fast=False
)
model = AutoModelForSequenceClassification.from_pretrained(
    str(MODEL_DIR)
)

if model.config.num_labels != len(CATEGORIES):
    raise ValueError(
        f"モデルの出力数が不正です。"
        f"期待値={len(CATEGORIES)}, "
        f"実際={model.config.num_labels}"
    )

model.eval()


def predict_toxicity(text: str) -> dict:
    """投稿文を8クラス分類し、適切かどうかを判定する。"""

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256,
        padding=True,
    )

    with torch.inference_mode():
        outputs = model(**inputs)

        # 8クラス分類なのでsoftmaxで確率に変換
        probabilities = torch.softmax(outputs.logits, dim=-1)[0]

    category_probabilities = {
        category: float(probability)
        for category, probability in zip(
            CATEGORIES,
            probabilities.tolist(),
        )
    }

    # 最も確率が高いカテゴリを予測結果にする
    predicted_index = int(torch.argmax(probabilities).item())
    predicted_category = CATEGORIES[predicted_index]
    predicted_probability = float(probabilities[predicted_index])

    # 「適切」以外なら不適切と判定
    is_toxic = predicted_category != "適切"

    return {
        "is_toxic": is_toxic,
        "predicted_category": predicted_category,
        "categories": [predicted_category] if is_toxic else [],
        "category_probabilities": category_probabilities,
        "toxic_probability": predicted_probability if is_toxic else 0.0,
    }
