# utils/types.py
import pandas as pd
import numpy as np
from sqlalchemy.types import Integer, BigInteger, Float, String, Boolean, Date, DateTime


# Supported PostgreSQL types
PG_TYPES = {
    "INTEGER": Integer(),
    "BIGINT": BigInteger(),
    "FLOAT": Float(),
    "TEXT": String(),
    "BOOLEAN": Boolean(),
    "DATE": Date(),
    "TIMESTAMP": DateTime(),
}


def suggest_pg_type(series: pd.Series) -> str:
    """
    Suggest a PostgreSQL datatype based on a pandas Series.
    """

    # If it's already datetime dtype
    if pd.api.types.is_datetime64_any_dtype(series):
        # If no time component -> DATE, else TIMESTAMP
        if series.dt.time.nunique() <= 1:  # mostly midnight values
            return "DATE"
        return "TIMESTAMP"

    # Try to parse to datetime (if object/string type)
    if series.dtype == "object":
        try:
            parsed = pd.to_datetime(
                series.dropna().sample(min(50, len(series))), errors="raise"
            )
            if parsed.dt.time.nunique() <= 1:
                return "DATE"
            return "TIMESTAMP"
        except Exception:
            pass  # not a date

    # Numeric detection
    if pd.api.types.is_integer_dtype(series):
        # If values fit in int32, use INTEGER else BIGINT
        if series.dropna().between(-(2**31), 2**31 - 1).all():
            return "INTEGER"
        return "BIGINT"

    if pd.api.types.is_float_dtype(series):
        return "FLOAT"

    if pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"

    # Default fallback
    return "TEXT"
