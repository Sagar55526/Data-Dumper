import pandas as pd
from sqlalchemy.types import Integer, BigInteger, Float, String, DateTime, Boolean, Date

PG_TYPES = {
    "INTEGER": Integer,
    "BIGINT": BigInteger,
    "FLOAT": Float,
    "TEXT": String,
    "BOOLEAN": Boolean,
    "DATE": Date,
    "TIMESTAMP": DateTime,
}


def suggest_pg_type(series: pd.Series):
    """Suggest a Postgres type based on pandas dtype and sample values."""
    if pd.api.types.is_integer_dtype(series):
        # decide INTEGER vs BIGINT
        if series.max() > 2_147_483_647:  # int32 max
            return "BIGINT"
        return "INTEGER"
    elif pd.api.types.is_float_dtype(series):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "TIMESTAMP"
    else:
        # Try heuristic for date strings
        try:
            pd.to_datetime(series.dropna().sample(min(5, len(series))), errors="raise")
            return "DATE"
        except Exception:
            return "TEXT"
