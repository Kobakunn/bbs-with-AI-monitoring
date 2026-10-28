# moderation_model.py
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = (
    Path(__file__).resolve().parent
    / "models"
    / "toxic-bert-multilabel"
)

# 学習時と同じカテゴリ順にする
CATEGORIES = [
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
    """投稿文を分類し、有害カテゴリと各カテゴリの予測確率を返す。"""

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256,
        padding=True,
    )

    with torch.inference_mode():
        outputs = model(**inputs)

        # マルチラベル分類ではカテゴリごとにsigmoidを適用
        probabilities = torch.sigmoid(outputs.logits)[0]

    category_probabilities = {
        category: float(probability)
        for category, probability in zip(
            CATEGORIES,
            probabilities.tolist(),
        )
    }

    # 閾値以上のカテゴリを検出結果とする
    detected_categories = [
        category
        for category, probability in category_probabilities.items()
        if probability >= THRESHOLD
    ]

    return {
        "is_toxic": len(detected_categories) > 0,
        "categories": detected_categories,
        "category_probabilities": category_probabilities,
        # 従来の確率表示を一時的に残す場合の互換用。
        # 7カテゴリのうち最大の予測確率であり、
        # 「有害である確率」そのものではない。
        "toxic_probability": max(category_probabilities.values()),
    }
