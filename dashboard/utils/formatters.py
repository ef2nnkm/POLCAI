import pandas as pd

def format_number(value) -> str:
    return "0" if pd.isna(value) else f"{float(value):,.0f}"

def percentage(numerator, denominator) -> float:
    if pd.isna(numerator) or pd.isna(denominator) or float(denominator) == 0:
        return 0.0
    return float(numerator) / float(denominator) * 100

def total(data: pd.DataFrame, column: str) -> float:
    if column not in data.columns:
        return 0.0
    return float(pd.to_numeric(data[column], errors="coerce").fillna(0).sum())
