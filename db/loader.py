import pandas as pd
from sqlalchemy.engine import Engine


def load_file_to_db(file, engine: Engine, table_name: str) -> str:
    """
    Load a CSV/Excel file into PostgreSQL.
    Returns success message.
    """
    try:
        if file.name.endswith(".csv"):
            try:
                df = pd.read_csv(
                    file, delimiter=",", quotechar='"', skipinitialspace=True
                )
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

        df.columns = df.columns.str.strip()
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        df.to_sql(table_name, engine, if_exists="replace", index=False)
        return f"✅ {file.name} uploaded as table `{table_name}`"

    except Exception as e:
        return f"❌ Error while uploading {file.name}: {e}"
