# utils/transformers.py
import re
import pandas as pd


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert DataFrame column names to snake_case.
    """
    df = df.copy()
    df.columns = [
        re.sub(r"\W+", "_", col.strip().lower()).strip("_") for col in df.columns
    ]
    return df


def apply_new_column_names(df: pd.DataFrame, new_names: dict) -> pd.DataFrame:
    """
    Rename DataFrame columns based on a mapping dictionary.
    """
    df = df.copy()
    return df.rename(columns=new_names)
