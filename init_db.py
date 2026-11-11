"""Create the database, the nine tables, and the sample rows.

Running this again drops those tables first, then loads the sample data.
Other databases on the same SQL Server are left alone.
"""

from pathlib import Path
import re

import pyodbc

from db import _env, connection_string, get_conn, is_configured


def statements(script):
    lines = []
    for line in script.splitlines():
        comment_at = line.find("--")
        if comment_at != -1:
            line = line[:comment_at]
        lines.append(line)
    return [part.strip() for part in "\n".join(lines).split(";") if part.strip()]


def run_script(cursor, filename):
    script = (Path(__file__).parent / filename).read_text(encoding="utf-8")
    for statement in statements(script):
        cursor.execute(statement)
        while True:
            try:
                if cursor.description is not None:
                    cursor.fetchall()
            except pyodbc.ProgrammingError:
                pass
            if not cursor.nextset():
                break


def ensure_database():
    db_name = _env("DB_NAME", "FreelanceMarketplace")
    if not re.fullmatch(r"[A-Za-z0-9_]+", db_name):
        raise SystemExit("DB_NAME may only contain letters, numbers, and underscores.")

    # CREATE DATABASE cannot run inside a normal transaction.
    connection = pyodbc.connect(connection_string(database="master"), timeout=15, autocommit=True)
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"""
            IF DB_ID(N'{db_name}') IS NULL
                CREATE DATABASE [{db_name}];
            """
        )
    finally:
        connection.close()
    print(f"Database ready: {db_name}")


def main():
    if not is_configured():
        raise SystemExit(
            "Set DB_SERVER and DB_NAME in the .env file, then run this again."
        )

    ensure_database()
    with get_conn() as connection:
        cursor = connection.cursor()
        run_script(cursor, "schema.sql")
        run_script(cursor, "seed.sql")
    print("Tables created and sample rows inserted.")


if __name__ == "__main__":
    main()
