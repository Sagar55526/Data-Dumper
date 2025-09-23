def validate_db_fields(db_host, db_port, db_name, db_user, db_pass):
    """Check if all DB fields are filled."""
    missing = []
    if not db_host:
        missing.append("Host")
    if not db_port:
        missing.append("Port")
    if not db_name:
        missing.append("Database Name")
    if not db_user:
        missing.append("Username")
    if not db_pass:
        missing.append("Password")
    return missing
