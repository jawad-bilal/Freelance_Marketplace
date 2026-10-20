"""Database connection for Neon (PostgreSQL).

Pages pass SQL and a tuple of values. The %s marks are placeholders.
psycopg fills them in. User text is never joined onto the SQL string.
"""

import os
from contextlib import contextmanager
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv(Path(__file__).with_name(".env"))


def database_url():
    url = os.environ.get("DATABASE_URL", "").strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    # Neon refuses a connection that does not use SSL.
    # A local PostgreSQL install does not need that setting.
    host_is_local = "localhost" in url or "127.0.0.1" in url
    if url and "sslmode=" not in url and not host_is_local:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}sslmode=require"
    return url


@contextmanager
def get_conn():
    # Neon can take a few seconds to wake a free-tier database.
    connection = psycopg.connect(database_url(), row_factory=dict_row, connect_timeout=30)
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
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()


def fetch_one(sql, params=()):
    with get_conn() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()


def execute(sql, params=()):
    with get_conn() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
