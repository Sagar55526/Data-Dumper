# app.py
import re
import streamlit as st
from db.connector import get_engine
from db.loader import read_file, load_file_to_db

st.set_page_config(page_title="Data Uploader", layout="wide")
st.title("📊 Data Uploader: Excel/CSV → PostgreSQL")

left_col, right_col = st.columns([1, 2])

with left_col:
    st.header("🔒 Database Credentials")
    db_host = st.text_input("Host", "localhost")
    db_port = st.text_input("Port", "5432")
    db_name = st.text_input("Database Name")
    db_user = st.text_input("Username")
    db_pass = st.text_input("Password", type="password")
    st.write("")  # spacing
    upload_to_db = st.button("🚀 Upload to PostgreSQL")


with right_col:
    st.header("📁 Files & Column Mapping")
    uploaded_files = st.file_uploader(
        "Upload files", type=["csv", "xlsx"], accept_multiple_files=True
    )

    standardize = st.checkbox(
        "🔠 Standardize column names (snake_case)",
        value=True,
        help="If checked, suggested snake_case names will be filled for you — you can still edit them.",
    )

    table_data = {}

    if uploaded_files:
        for fidx, file in enumerate(uploaded_files):
            st.subheader(f"🔹 {file.name}")
            default_table = file.name.rsplit(".", 1)[0].lower().replace(" ", "_")
            table_name = st.text_input(
                "Table name:",
                value=default_table,
                key=f"{file.name}_{fidx}_table",
            )

            try:
                df = read_file(file)
            except Exception as e:
                st.error(f"Could not read file `{file.name}`: {e}")
                continue

            orig_cols = [str(c).strip() for c in df.columns]

            def to_snake(col: str) -> str:
                col = re.sub(r"\s+", "_", col.strip())
                col = re.sub(r"[^0-9a-zA-Z_]", "_", col)
                col = re.sub(r"_+", "_", col)
                return col.strip("_").lower()

            if standardize:
                suggested = [to_snake(c) for c in orig_cols]
            else:
                suggested = orig_cols.copy()

            st.markdown("**Column mapping (edit inline)**")

            hdr_a, hdr_b, hdr_c = st.columns([1, 3, 1])
            hdr_a.markdown("**Original**")
            hdr_b.markdown("**New / Rename**")
            hdr_c.markdown("**Example value**")

            new_cols = []
            for idx, orig in enumerate(orig_cols):
                row_a, row_b, row_c = st.columns([1, 3, 1])
                row_a.markdown(f"`{orig}`")

                key = f"{file.name}_{fidx}_col_{idx}"
                new_name = row_b.text_input("", value=suggested[idx], key=key)

                sample_val = ""
                try:
                    s = df[orig].dropna()
                    if not s.empty:
                        sample_val = str(s.iloc[0])
                except Exception:
                    sample_val = ""
                row_c.write(sample_val)

                new_cols.append(new_name or orig)

            df.columns = new_cols

            st.write("👀 Sample preview (first 10 rows):")
            st.dataframe(df.head(10))

            table_key = f"{file.name}_{fidx}"
            table_data[table_key] = {"df": df, "table_name": table_name}

if upload_to_db:
    if not uploaded_files:
        st.warning("Please upload at least one file before uploading.")
    elif not all([db_host, db_port, db_name, db_user, db_pass]):
        st.error("Please fill all DB credential fields.")
    else:
        engine = get_engine(db_user, db_pass, db_host, db_port, db_name)

        for key, payload in table_data.items():
            df = payload["df"]
            table_name = payload["table_name"]
            try:
                msg = load_file_to_db(df, engine, table_name)
                if msg.startswith("✅"):
                    st.success(msg)
                else:
                    st.error(msg)
            except Exception as err:
                st.error(f"❌ Unexpected error while uploading `{table_name}`: {err}")


# now as single file can have multiple date fomatted date like in single column have YYYY-MM-DD, DD-MM-YY, DD/MM/YYYY and many more possible formats and one more issue is that currently when code is passing dates as 'text' datatypes which supposed to be datetime or any other suitable format  so this is one of the greatest challenge that i want to resolve from my project so
# so firstly ask user in which format he want to keep dates ? and for selected format make all available dates on column in selected format along with suitable datatype which will be selected by user only
