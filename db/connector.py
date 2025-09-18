from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine(user: str, password: str, host: str, port: str, db: str) -> Engine:
    """
    Create and return a SQLAlchemy engine for PostgreSQL.
    """
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)
