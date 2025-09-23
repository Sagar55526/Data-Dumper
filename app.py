import re
import streamlit as st
import pandas as pd

from db.connector import get_engine
from db.loader import read_file, load_file_to_db
from utils.transformers import standardize_columns, apply_new_column_names
from utils.validators import validate_db_fields
from utils.types import PG_TYPES, suggest_pg_type


# --- Page Config ---
st.set_page_config(
    page_title="Data Dumper",
    page_icon="📊",
    layout="wide",
)


def main():
    # --- Title ---
    st.markdown(
        "<h1 style='text-align: center;'>📊 Data Uploader: Excel/CSV → PostgreSQL</h1>",
        unsafe_allow_html=True,
    )
    st.divider()

    # --- Layout: Credentials (left) | Upload & Processing (right) ---
    col_left, col_right = st.columns([1, 2], gap="large")

    # --- DB Credentials ---
    with col_left:
        st.markdown("### 🔑 Database Connection")
        db_host = st.text_input("Host", placeholder="localhost")
        db_port = st.text_input("Port", "5432")
        db_name = st.text_input("Database Name", placeholder="e.g. mydb")
        db_user = st.text_input("Username", placeholder="e.g. postgres")
        db_pass = st.text_input("Password", type="password")

    # --- File Upload + Processing ---
    with col_right:
        st.markdown("### 📂 Upload Files")
        uploaded_files = st.file_uploader(
            "Upload one or more files", type=["csv", "xlsx"], accept_multiple_files=True
        )

        table_data = {}

        if uploaded_files:
            st.subheader("📝 Review & Configure Each File")

            for file in uploaded_files:
                with st.expander(f"📄 File: {file.name}", expanded=True):
                    # Read file
                    df = read_file(file)

                    # Preview data
                    st.markdown("**👀 Data Preview (first 8 rows):**")
                    st.dataframe(df.head(8), use_container_width=True)

                    # Column editing section
                    st.markdown("**✏️ Column Configuration**")

                    # Option: Keep as-is vs Standardize
                    col_opt = st.radio(
                        f"Column naming for `{file.name}`:",
                        ["Keep original", "Standardize (snake_case)"],
                        horizontal=True,
                        key=f"{file.name}_colopt",
                    )
                    if col_opt == "Standardize (snake_case)":
                        df = standardize_columns(df)

                    new_columns = {}
                    col_types = {}
                    date_formats = {}

                    for i, col in enumerate(df.columns):
                        col1, col2, col3 = st.columns([2, 2, 2])

                        with col1:
                            new_name = st.text_input(
                                f"Rename `{col}`",
                                value=col,
                                key=f"{file.name}_{i}_name",
                            )
                            new_columns[col] = new_name

                        with col2:
                            suggested = suggest_pg_type(df[col])
                            chosen = st.selectbox(
                                "Datatype",
                                options=list(PG_TYPES.keys()),
                                index=list(PG_TYPES.keys()).index(suggested),
                                key=f"{file.name}_{i}_dtype",
                            )
                            col_types[new_name] = PG_TYPES[chosen]

                        with col3:
                            if chosen in ("DATE", "TIMESTAMP"):
                                fmt = st.text_input(
                                    f"Custom format ({col})",
                                    placeholder="e.g. %d-%m-%Y",
                                    key=f"{col}_fmt",
                                )
                                date_formats[new_name] = fmt

                                try:
                                    if fmt:
                                        df[col] = pd.to_datetime(
                                            df[col], format=fmt, errors="coerce"
                                        )
                                    else:
                                        df[col] = pd.to_datetime(
                                            df[col], errors="coerce"
                                        )

                                    if chosen == "DATE":
                                        df[col] = df[col].dt.date
                                    st.caption(f"✅ Parsed {col} as {chosen}")
                                except Exception:
                                    st.warning(
                                        f"⚠️ Could not parse column `{col}`, kept as TEXT"
                                    )
                                    col_types[new_name] = "TEXT"

                    # Rename columns
                    df = apply_new_column_names(df, new_columns)

                    # Table name
                    default_table = (
                        file.name.rsplit(".", 1)[0].lower().replace(" ", "_")
                    )
                    table_name = st.text_input(
                        "Table Name", value=default_table, key=f"{file.name}_table"
                    )

                    # Save
                    table_data[file.name] = {
                        "df": df,
                        "table_name": table_name,
                        "col_types": col_types,
                    }

        # --- Upload to PostgreSQL ---
        if st.button("🚀 Upload to PostgreSQL", use_container_width=True):
            if not uploaded_files:
                st.warning("Please upload at least one file.")
            elif not validate_db_fields(db_host, db_port, db_name, db_user, db_pass):
                st.error("Please fill all DB credential fields.")
            else:
                engine = get_engine(db_user, db_pass, db_host, db_port, db_name)
                for file in uploaded_files:
                    df = table_data[file.name]["df"]
                    table_name = table_data[file.name]["table_name"]
                    col_types = table_data[file.name]["col_types"]

                    result_msg = load_file_to_db(df, engine, table_name, col_types)
                    if "✅" in result_msg:
                        st.success(result_msg)
                    else:
                        st.error(result_msg)


if __name__ == "__main__":
    main()
