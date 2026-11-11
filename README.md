# Student Freelance Marketplace

A small website for the database proposal. Students, clients, projects, proposals, contracts, payments, and reviews are stored in nine tables. The pages use HTML and CSS. Flask runs the SQL against **local Microsoft SQL Server**, which you manage in **SSMS**.

## Important: SSMS is not for MySQL

| Tool | Database it manages |
| --- | --- |
| **SSMS** (SQL Server Management Studio) | Microsoft SQL Server |
| MySQL Workbench | MySQL |
| Neon | PostgreSQL |

This project uses **SQL Server + SSMS**, not Neon and not MySQL.

Auto numbers look like this:

```sql
student_id INT IDENTITY(1,1) PRIMARY KEY
```

That is the SQL Server version of MySQL `AUTO_INCREMENT` / PostgreSQL `SERIAL`.

## Setup on the other laptop

### 1. Install software

1. [SQL Server 2022 Express or Developer](https://www.microsoft.com/sql-server/sql-server-downloads)
2. [SSMS](https://learn.microsoft.com/sql/ssms/download-sql-server-management-studio-ssms)
3. [ODBC Driver 17 or 18 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)
4. Python 3.11, 3.12, or 3.13 is the safest choice. Newer Python also works if `pip install pyodbc` finds a wheel for it.

During SQL Server setup, enable **Mixed Mode** if you want an `sa` password. Windows Authentication alone is enough for this project.

### 2. Find your server name in SSMS

Open SSMS → Connect. Common names:

- `localhost`
- `.`
- `.\SQLEXPRESS`
- `DESKTOP-XXXX\SQLEXPRESS`

Connect once so you know the exact name.

### 3. Configure the project

```powershell
cd path\to\Freelance_Marketplace
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`:

```env
DB_SERVER=localhost
DB_NAME=FreelanceMarketplace
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUSTED=yes
SECRET_KEY=any-long-random-text
```

If your instance is Express, try:

```env
DB_SERVER=.\SQLEXPRESS
```

If ODBC Driver 18 is installed instead:

```env
DB_DRIVER=ODBC Driver 18 for SQL Server
```

For SQL login instead of Windows Auth:

```env
DB_TRUSTED=no
DB_USER=sa
DB_PASSWORD=YourStrongPasswordHere
```

### 4. Create tables and sample data

```powershell
.\.venv\Scripts\python.exe init_db.py
```

This creates the `FreelanceMarketplace` database if needed, then runs `schema.sql` and `seed.sql`.

You can also do it in SSMS:

1. Connect to the server.
2. Create a database named `FreelanceMarketplace` (or let `init_db.py` create it).
3. Open `schema.sql`, choose that database, and execute.
4. Open `seed.sql`, execute.

### 5. Run the site

```powershell
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000.

## What to click in a demo

1. Home shows `COUNT(*)` for every table, and the open projects.
2. Students shows the many-to-many join through `StudentSkill`.
3. Open **Welcome article**, submit a proposal, then click **Accept**. That writes the accepted proposal, rejects the others, inserts a contract, and sets the project to in progress.
4. Record a payment. That is one-to-many: several payment rows, one contract.
5. Save a review. That completes the contract. A second review is refused because `Review.contract_id` is unique.

The SQL for each page is written above the matching function in `app.py`.
