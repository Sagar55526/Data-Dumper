import streamlit as st
from db.connector import get_engine
from db.loader import load_file_to_db

st.title("📊 Data Uploader: Excel/CSV → PostgreSQL")

# DB credentials input
db_host = st.text_input("Host", "localhost")
db_port = st.text_input("Port", "5432")
db_name = st.text_input("Database Name")
db_user = st.text_input("Username")
db_pass = st.text_input("Password", type="password")

# File uploader
uploaded_files = st.file_uploader(
    "Upload files", type=["csv", "xlsx"], accept_multiple_files=True
)

# Dictionary to hold editable table names
table_names = {}

if uploaded_files:
    st.subheader("✏️ Set Table Names")
    for file in uploaded_files:
        default_name = file.name.rsplit(".", 1)[0].lower().replace(" ", "_")
        # editable field for table name
        table_names[file.name] = st.text_input(
            f"Table name for **{file.name}**:", value=default_name, key=file.name
        )

if st.button("🚀 Upload to PostgreSQL"):
    if not uploaded_files:
        st.warning("Please upload at least one file.")
    elif not all([db_host, db_port, db_name, db_user, db_pass]):
        st.error("Please fill all DB credential fields.")
    else:
        engine = get_engine(db_user, db_pass, db_host, db_port, db_name)

        for file in uploaded_files:
            table_name = table_names[file.name]
            result_msg = load_file_to_db(file, engine, table_name)
            st.write(result_msg)
