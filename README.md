# Student Freelance Marketplace

A small website for the database proposal. Students, clients, projects, proposals, contracts, payments, and reviews are stored in nine tables. The pages use HTML and CSS. Flask runs the SQL. There is no login and no extra framework.

## Neon is PostgreSQL

Neon’s free tier is PostgreSQL, not MySQL. The keys and joins are the same ideas. Two syntax differences are worth knowing:

| Idea | This project (PostgreSQL) | MySQL |
| --- | --- | --- |
| Auto number | `student_id SERIAL PRIMARY KEY` | `student_id INT AUTO_INCREMENT PRIMARY KEY` |
| Combine text in a group | `STRING_AGG(skill_name, ', ')` | `GROUP_CONCAT(skill_name SEPARATOR ', ')` |

`%s` in the Python code is a placeholder. It is not MySQL-only. psycopg fills in the values.

## Setup

1. Create a free project at [neon.tech](https://neon.tech).
2. Open **Connect** and copy the connection string.
3. In this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

4. Paste the Neon string into `.env` as `DATABASE_URL`.
5. Create the tables. Either paste `schema.sql` and then `seed.sql` into the Neon SQL editor, or run:

```powershell
python init_db.py
```

`init_db.py` drops these nine tables and loads the sample rows again. It does not drop other tables.

6. Start the site:

```powershell
python app.py
```

Open http://127.0.0.1:5000.

If PowerShell blocks the virtual environment, run `.\.venv\Scripts\python.exe app.py` instead.

## What to click in a demo

1. Home shows `COUNT(*)` for every table, and the open projects.
2. Students shows the many-to-many join through `StudentSkill`.
3. Open **Welcome article**, submit a proposal, then click **Accept**. That writes the accepted proposal, rejects the others, inserts a contract, and sets the project to in progress. Those four statements are one transaction in `accept_proposal`.
4. Record a payment. That is one-to-many: several payment rows, one contract.
5. Save a review. That completes the contract. A second review is refused because `Review.contract_id` is unique.

The SQL for each page is written above the matching function in `app.py`.
