# app.py
import re
import streamlit as st
from db.connector import get_engine
from db.loader import read_file, load_file_to_db
from utils.transformers import standardize_columns, apply_new_column_names
from utils.validators import validate_db_fields
from utils.types import PG_TYPES, suggest_pg_type

st.set_page_config(page_title="Data Uploader", layout="wide")
st.title("📊 Data Uploader: Excel/CSV → PostgreSQL")

# --- Two-column layout: left = DB creds, right = file operations ---
left_col, right_col = st.columns([1, 2])

# ----------------
# Left: DB inputs
# ----------------
with left_col:
    st.header("🔒 Database Credentials")
    db_host = st.text_input("Host", "localhost")
    db_port = st.text_input("Port", "5432")
    db_name = st.text_input("Database Name")
    db_user = st.text_input("Username")
    db_pass = st.text_input("Password", type="password")
    st.write("")  # spacing
    upload_to_db = st.button("🚀 Upload to PostgreSQL")

# -----------------------
# Right: Files and editors
# -----------------------
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

    # container to store prepared DataFrames and table names
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

            # try to read file
            try:
                df = read_file(file)
            except Exception as e:
                st.error(f"Could not read file `{file.name}`: {e}")
                continue

            # normalize original column names list
            orig_cols = [str(c).strip() for c in df.columns]

            # apply snake_case suggestion if requested
            if standardize:
                suggested = standardize_columns(orig_cols)
            else:
                suggested = orig_cols.copy()

            st.markdown("**📝 Rename Columns**")

            new_cols = []
            for idx, orig in enumerate(orig_cols):
                new_name = st.text_input(
                    f"Rename `{orig}`",
                    value=suggested[idx],
                    key=f"{file.name}_{fidx}_col_{idx}",
                )
                new_cols.append(new_name or orig)

            # apply renamed columns
            df = apply_new_column_names(df, new_cols)

            # --- Datatype selection step ---
            st.markdown("**📌 Choose column datatypes**")
            hdr1, hdr2, hdr3 = st.columns([2, 2, 2])
            hdr1.markdown("**Column**")
            hdr2.markdown("**Suggested**")
            hdr3.markdown("**Select Type**")

            col_types = {}
            for i, col in enumerate(df.columns):
                row1, row2, row3 = st.columns([2, 2, 2])
                row1.write(col)

                suggested_type = suggest_pg_type(df[col])
                row2.write(suggested_type)

                chosen_type = row3.selectbox(
                    "",
                    options=list(PG_TYPES.keys()),
                    index=list(PG_TYPES.keys()).index(suggested_type),
                    key=f"{file.name}_{fidx}_dtype_{i}",
                )
                col_types[col] = PG_TYPES[chosen_type]

            # show preview
            st.write("👀 Sample preview (first 10 rows):")
            st.dataframe(df.head(10))

            # save prepared DF, table name, and chosen datatypes
            table_data[file.name] = {
                "df": df,
                "table_name": table_name,
                "dtypes": col_types,
            }

# -------------------------
# Handle the actual upload
# -------------------------
if upload_to_db:
    if not uploaded_files:
        st.warning("Please upload at least one file before uploading.")
    else:
        missing = validate_db_fields(db_host, db_port, db_name, db_user, db_pass)
        if missing:
            st.error(f"Missing fields: {', '.join(missing)}")
        else:
            engine = get_engine(db_user, db_pass, db_host, db_port, db_name)

            for file in uploaded_files:
                df = table_data[file.name]["df"]
                table_name = table_data[file.name]["table_name"]
                dtypes = table_data[file.name]["dtypes"]

                msg = load_file_to_db(df, engine, table_name, dtypes)
                if msg.startswith("✅"):
                    st.success(msg)
                else:
                    st.error(msg)


# now as single file can have multiple date fomatted date like in single column have YYYY-MM-DD, DD-MM-YY, DD/MM/YYYY and many more possible formats and one more issue is that currently when code is passing dates as 'text' datatypes which supposed to be datetime or any other suitable format  so this is one of the greatest challenge that i want to resolve from my project so
# so firstly ask user in which format he want to keep dates ? and for selected format make all available dates on column in selected format along with suitable datatype which will be selected by user only
