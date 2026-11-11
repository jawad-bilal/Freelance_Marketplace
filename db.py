"""Database connection for local Microsoft SQL Server (SSMS).

Pages pass SQL and a tuple of values. The %s marks are placeholders.
This file turns them into ? marks for pyodbc. User text is never joined
onto the SQL string.
"""

import os
from contextlib import contextmanager
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))


def _env(name, default=""):
    return os.environ.get(name, default).strip()


def is_configured():
    return bool(_env("DB_SERVER") and _env("DB_NAME"))


def connection_string(database=None):
    """Build an ODBC connection string for SQL Server."""
    server = _env("DB_SERVER", "localhost")
    db_name = database or _env("DB_NAME", "FreelanceMarketplace")
    driver = _env("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    trusted = _env("DB_TRUSTED", "yes").lower() in ("1", "true", "yes")

    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={db_name}",
    ]
    if trusted:
        parts.append("Trusted_Connection=yes")
    else:
        user = _env("DB_USER")
        password = _env("DB_PASSWORD")
        if not user:
            raise RuntimeError("Set DB_USER and DB_PASSWORD, or set DB_TRUSTED=yes.")
        parts.append(f"UID={user}")
        parts.append(f"PWD={password}")
    return ";".join(parts)


def prepare(sql):
    # Keep %s in app.py. pyodbc wants ?.
    return sql.replace("%s", "?")


def _rows_as_dicts(cursor):
    if cursor.description is None:
        return []
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _row_as_dict(cursor):
    if cursor.description is None:
        return None
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, row))


@contextmanager
def get_conn(database=None):
    connection = pyodbc.connect(connection_string(database=database), timeout=15)
    connection.autocommit = False
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def fetch_all(sql, params=()):
    with get_conn() as connection:
        cursor = connection.cursor()
        cursor.execute(prepare(sql), params)
        return _rows_as_dicts(cursor)


def fetch_one(sql, params=()):
    with get_conn() as connection:
        cursor = connection.cursor()
        cursor.execute(prepare(sql), params)
        return _row_as_dict(cursor)


def execute(sql, params=()):
    with get_conn() as connection:
        cursor = connection.cursor()
        cursor.execute(prepare(sql), params)


def integrity_kind(error):
    """Turn a SQL Server IntegrityError into unique / foreign / check."""
    message = str(error).lower()
    if "unique" in message or "duplicate" in message or "primary key" in message:
        return "unique"
    if "foreign key" in message:
        return "foreign"
    if "check" in message:
        return "check"
    return "other"
