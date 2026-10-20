"""Create the nine tables and load the sample rows.

Running this again drops those tables first, then loads the sample data.
Other tables in the same Neon database are left alone.
"""

from pathlib import Path

from db import database_url, get_conn


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
        if cursor.description is not None:
            cursor.fetchall()


def main():
    if not database_url():
        raise SystemExit("Set DATABASE_URL in the .env file, then run this again.")

    with get_conn() as connection:
        with connection.cursor() as cursor:
            run_script(cursor, "schema.sql")
            run_script(cursor, "seed.sql")
    print("Tables created and sample rows inserted.")


if __name__ == "__main__":
    main()
