import re
import pandas as pd


def standardize_columns(cols):
    """Convert column names to snake_case."""

    def to_snake(col: str) -> str:
        col = re.sub(r"\s+", "_", col.strip())
        col = re.sub(r"[^0-9a-zA-Z_]", "_", col)
        col = re.sub(r"_+", "_", col)
        return col.strip("_").lower()

    return [to_snake(c) for c in cols]


def apply_new_column_names(df: pd.DataFrame, new_cols):
    """Apply new column names safely."""
    df = df.copy()
    df.columns = new_cols
    return df
