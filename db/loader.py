import pandas as pd
from sqlalchemy.engine import Engine


def read_file(file) -> pd.DataFrame:
    """
    Read and clean CSV/Excel file into a DataFrame.
    """
    if file.name.endswith(".csv"):
        try:
            df = pd.read_csv(file, delimiter=",", quotechar='"', skipinitialspace=True)
        except UnicodeDecodeError:
            file.seek(0)
            df = pd.read_csv(
                file,
                encoding="latin1",
                delimiter=",",
                quotechar='"',
                skipinitialspace=True,
            )
    else:
        df = pd.read_excel(file)

    # Clean column names & strings
    df.columns = df.columns.str.strip()
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def load_file_to_db(df: pd.DataFrame, engine: Engine, table_name: str) -> str:
    """
    Upload a DataFrame into PostgreSQL.
    """
    try:
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        return f"✅ Data uploaded to table `{table_name}`"
    except Exception as e:
        return f"❌ Error while uploading: {e}"
