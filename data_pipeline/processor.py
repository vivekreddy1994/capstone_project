import re

import pandas as pd

try:
    from .config import CURRENCY_CONVERSION_RATE
except ImportError:
    from config import CURRENCY_CONVERSION_RATE

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def clean_and_process_data(raw_data):
    frame = pd.DataFrame(raw_data).copy()
    price_text = frame.get("price_gbp", frame.get("price", pd.Series(dtype="object"))).astype(str)
    frame["price_gbp"] = pd.to_numeric(price_text.str.extract(r"([0-9]+(?:\.[0-9]+)?)", expand=False), errors="coerce")
    frame["rating"] = frame.get("rating", frame.get("star_rating", pd.Series(dtype="object"))).map(RATING_MAP).fillna(
        pd.to_numeric(frame.get("rating", pd.Series(dtype="float64")), errors="coerce")
    )
    frame["rating"] = frame["rating"].fillna(frame["rating"].median()).round().clip(1, 5).astype(int)
    availability = frame.get("availability", pd.Series("", index=frame.index)).fillna("").astype(str)
    frame["in_stock"] = availability.str.contains(r"in\s*stock", case=False, regex=True)
    frame["price_gbp"] = frame["price_gbp"].fillna(frame["price_gbp"].median())
    frame["price_inr"] = (frame["price_gbp"] * CURRENCY_CONVERSION_RATE).round(2)
    frame["category"] = frame.get("category", "Unknown").fillna("Unknown").astype(str).str.strip()
    frame["title"] = frame.get("title", "").fillna("Unknown").astype(str).str.strip()
    frame["price"] = frame["price_gbp"]
    frame["star_rating"] = frame["rating"]
    frame["availability"] = availability
    return frame


def clean_data(raw_data):
    return clean_and_process_data(raw_data).to_dict(orient="records")


def process_books(raw_data):
    return clean_data(raw_data)


def validate_data(df):
    required = {"title", "price_gbp", "price_inr", "rating", "in_stock", "category"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if df["price_gbp"].isna().any() or (df["price_gbp"] < 0).any():
        raise ValueError("price_gbp must be non-negative and non-null")
    if not df["rating"].between(1, 5).all():
        raise ValueError("rating must be between 1 and 5")
    return True
