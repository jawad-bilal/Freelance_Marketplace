"""Student Freelance Marketplace.

Each page runs a short SQL statement. There is no ORM.
The nine tables are created by schema.sql.
"""

import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import psycopg
from flask import Flask, flash, redirect, render_template, request, url_for
from psycopg.errors import CheckViolation, ForeignKeyViolation, UniqueViolation

from db import database_url, execute, fetch_all, fetch_one, get_conn

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

LABELS = {
    "open": "Open",
    "in_progress": "In progress",
    "completed": "Completed",
    "pending": "Pending",
    "accepted": "Accepted",
    "rejected": "Rejected",
    "active": "Active",
}


@app.template_filter("label")
def label(value):
    return LABELS.get(value, value)


@app.template_filter("money")
def money(value):
    if value is None:
        return "$0.00"
    return f"${value:,.2f}"


@app.before_request
def require_database():
    if request.endpoint in ("static", "tables"):
        return None
    if not database_url():
        return render_template("setup.html")
    return None


def form_text(name):
    return request.form.get(name, "").strip()


def parse_int(raw):
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    if value < 1:
        return None
    return value


def parse_money(raw):
    try:
        value = Decimal(str(raw).strip())
    except (InvalidOperation, AttributeError):
        return None
    if value <= 0 or value > Decimal("99999999.99"):
        return None
    return value.quantize(Decimal("0.01"))


def parse_date(raw):
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def valid_email(value):
    parts = value.split("@")
    return len(parts) == 2 and parts[0] and "." in parts[1]


@app.route("/")
def home():
    # One row of totals. Each subquery counts one table.
    counts = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM Student) AS students,
            (SELECT COUNT(*) FROM Client) AS clients,
            (SELECT COUNT(*) FROM Skill) AS skills,
            (SELECT COUNT(*) FROM StudentSkill) AS student_skills,
            (SELECT COUNT(*) FROM Project) AS projects,
            (SELECT COUNT(*) FROM Proposal) AS proposals,
            (SELECT COUNT(*) FROM Contract) AS contracts,
            (SELECT COUNT(*) FROM Payment) AS payments,
            (SELECT COUNT(*) FROM Review) AS reviews
        """
    )
    cards = [
        ("Students", counts["students"]),
        ("Clients", counts["clients"]),
        ("Skills", counts["skills"]),
        ("Student skills", counts["student_skills"]),
        ("Projects", counts["projects"]),
        ("Proposals", counts["proposals"]),
        ("Contracts", counts["contracts"]),
        ("Payments", counts["payments"]),
        ("Reviews", counts["reviews"]),
    ]
    # One-to-many join: a project row includes the client who posted it.
    open_projects = fetch_all(
        """
        SELECT p.project_id, p.title, p.budget, cl.full_name AS client_name
        FROM Project p
        JOIN Client cl ON cl.client_id = p.client_id
        WHERE p.status = 'open'
        ORDER BY p.project_id
        """
    )
    return render_template("index.html", cards=cards, open_projects=open_projects)


@app.route("/students", methods=["GET", "POST"])
def students():
    if request.method == "POST":
        error = create_student()
        if error:
            flash(error)
        else:
            flash("Student saved.")
            return redirect(url_for("students"))

    # Many-to-many: StudentSkill sits between Student and Skill.
    # LEFT JOIN keeps a student who does not have a skill yet.
    # STRING_AGG is the PostgreSQL form of MySQL GROUP_CONCAT.
    rows = fetch_all(
        """
        SELECT st.student_id, st.full_name, st.email, st.university,
               COALESCE(STRING_AGG(sk.skill_name, ', ' ORDER BY sk.skill_name), '') AS skills
        FROM Student st
        LEFT JOIN StudentSkill ss ON ss.student_id = st.student_id
        LEFT JOIN Skill sk ON sk.skill_id = ss.skill_id
        GROUP BY st.student_id, st.full_name, st.email, st.university
        ORDER BY st.full_name
        """
    )
    skills = fetch_all("SELECT skill_id, skill_name FROM Skill ORDER BY skill_name")
    return render_template("students.html", students=rows, skills=skills)


def create_student():
    name = form_text("full_name")
    email = form_text("email")
    university = form_text("university")
    bio = form_text("bio")
    if not name or not email or not university:
        return "Name, email, and university are required."
    if not valid_email(email):
        return "Enter an email like name@university.edu."

    skill_ids = []
    for raw in request.form.getlist("skill_id"):
        skill_id = parse_int(raw)
        if skill_id is None:
            return "Choose skills from the list."
        skill_ids.append(skill_id)

    # The student row and the skill links share one transaction.
    # If a skill insert fails, the student row is not kept either.
    try:
        with get_conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Student (full_name, email, university, bio)
                    VALUES (%s, %s, %s, %s)
                    RETURNING student_id
                    """,
                    (name, email, university, bio or None),
                )
                student_id = cursor.fetchone()["student_id"]
                for skill_id in skill_ids:
                    cursor.execute(
                        """
                        INSERT INTO StudentSkill (student_id, skill_id)
                        VALUES (%s, %s)
                        """,
                        (student_id, skill_id),
                    )
    except UniqueViolation:
        return "That email is already used."
    except ForeignKeyViolation:
        return "Choose skills from the list."
    return None


@app.route("/students/<int:student_id>")
def student_detail(student_id):
    student = fetch_one(
        """
        SELECT student_id, full_name, email, university, bio
        FROM Student
        WHERE student_id = %s
        """,
        (student_id,),
    )
    if student is None:
        flash("Student not found.")
        return redirect(url_for("students"))

    skills = fetch_all(
        """
        SELECT sk.skill_name
        FROM Skill sk
        JOIN StudentSkill ss ON ss.skill_id = sk.skill_id
        WHERE ss.student_id = %s
        ORDER BY sk.skill_name
        """,
        (student_id,),
    )
    proposals = fetch_all(
        """
        SELECT pr.proposal_id, pr.bid_amount, pr.status, p.project_id, p.title
        FROM Proposal pr
        JOIN Project p ON p.project_id = pr.project_id
        WHERE pr.student_id = %s
        ORDER BY pr.proposal_id
        """,
        (student_id,),
    )
    contracts = fetch_all(
        """
        SELECT c.contract_id, c.agreed_amount, c.status, p.project_id, p.title
        FROM Contract c
        JOIN Project p ON p.project_id = c.project_id
        WHERE c.student_id = %s
        ORDER BY c.contract_id
        """,
        (student_id,),
    )
    reviews = fetch_all(
        """
        SELECT r.rating, r.comment, cl.full_name AS client_name, p.title
        FROM Review r
        JOIN Client cl ON cl.client_id = r.client_id
        JOIN Contract c ON c.contract_id = r.contract_id
        JOIN Project p ON p.project_id = c.project_id
        WHERE r.student_id = %s
        ORDER BY r.review_id
        """,
        (student_id,),
    )
    rating = fetch_one(
        """
        SELECT ROUND(AVG(rating), 1) AS avg_rating, COUNT(*) AS review_count
        FROM Review
        WHERE student_id = %s
        """,
        (student_id,),
    )
    return render_template(
        "student_detail.html",
        student=student,
        skills=skills,
        proposals=proposals,
        contracts=contracts,
        reviews=reviews,
        rating=rating,
    )


@app.route("/clients", methods=["GET", "POST"])
def clients():
    if request.method == "POST":
        error = create_client()
        if error:
            flash(error)
        else:
            flash("Client saved.")
            return redirect(url_for("clients"))

    # COUNT(p.project_id) ignores the empty left join, so a new client shows 0.
    # COUNT(*) would show 1 for that same client.
    rows = fetch_all(
        """
        SELECT cl.client_id, cl.full_name, cl.email, cl.company,
               COUNT(p.project_id) AS project_count
        FROM Client cl
        LEFT JOIN Project p ON p.client_id = cl.client_id
        GROUP BY cl.client_id, cl.full_name, cl.email, cl.company
        ORDER BY cl.full_name
        """
    )
    return render_template("clients.html", clients=rows)


def create_client():
    name = form_text("full_name")
    email = form_text("email")
    company = form_text("company")
    if not name or not email:
        return "Name and email are required."
    if not valid_email(email):
        return "Enter an email like name@company.com."
    try:
        execute(
            """
            INSERT INTO Client (full_name, email, company)
            VALUES (%s, %s, %s)
            """,
            (name, email, company or None),
        )
    except UniqueViolation:
        return "That email is already used."
    return None


@app.route("/skills", methods=["GET", "POST"])
def skills():
    if request.method == "POST":
        error = create_skill()
        if error:
            flash(error)
        else:
            flash("Skill saved.")
            return redirect(url_for("skills"))

    rows = fetch_all(
        """
        SELECT sk.skill_id, sk.skill_name, COUNT(ss.student_id) AS student_count
        FROM Skill sk
        LEFT JOIN StudentSkill ss ON ss.skill_id = sk.skill_id
        GROUP BY sk.skill_id, sk.skill_name
        ORDER BY sk.skill_name
        """
    )
    return render_template("skills.html", skills=rows)


def create_skill():
    name = form_text("skill_name")
    if not name:
        return "Skill name is required."
    try:
        execute("INSERT INTO Skill (skill_name) VALUES (%s)", (name,))
    except UniqueViolation:
        return "That skill already exists."
    return None


@app.route("/projects", methods=["GET", "POST"])
def projects():
    if request.method == "POST":
        error = create_project()
        if error:
            flash(error)
        else:
            flash("Project posted.")
            return redirect(url_for("projects"))

    rows = fetch_all(
        """
        SELECT p.project_id, p.title, p.budget, p.status,
               cl.full_name AS client_name,
               COUNT(pr.proposal_id) AS proposal_count
        FROM Project p
        JOIN Client cl ON cl.client_id = p.client_id
        LEFT JOIN Proposal pr ON pr.project_id = p.project_id
        GROUP BY p.project_id, p.title, p.budget, p.status, cl.full_name
        ORDER BY p.project_id DESC
        """
    )
    client_rows = fetch_all(
        "SELECT client_id, full_name, company FROM Client ORDER BY full_name"
    )
    return render_template("projects.html", projects=rows, clients=client_rows)


def create_project():
    client_id = parse_int(request.form.get("client_id"))
    title = form_text("title")
    description = form_text("description")
    budget = parse_money(request.form.get("budget"))
    if client_id is None or not title or not description or budget is None:
        return "Client, title, description, and a budget greater than 0 are required."
    # status is omitted, so the column default 'open' is stored.
    try:
        execute(
            """
            INSERT INTO Project (client_id, title, description, budget)
            VALUES (%s, %s, %s, %s)
            """,
            (client_id, title, description, budget),
        )
    except ForeignKeyViolation:
        return "Choose a client from the list."
    except CheckViolation:
        return "Budget must be greater than 0."
    return None


@app.route("/projects/<int:project_id>")
def project_detail(project_id):
    project = fetch_one(
        """
        SELECT p.project_id, p.title, p.description, p.budget, p.status,
               cl.full_name AS client_name, cl.company
        FROM Project p
        JOIN Client cl ON cl.client_id = p.client_id
        WHERE p.project_id = %s
        """,
        (project_id,),
    )
    if project is None:
        flash("Project not found.")
        return redirect(url_for("projects"))

    proposals = fetch_all(
        """
        SELECT pr.proposal_id, pr.cover_letter, pr.bid_amount, pr.status,
               s.student_id, s.full_name AS student_name
        FROM Proposal pr
        JOIN Student s ON s.student_id = pr.student_id
        WHERE pr.project_id = %s
        ORDER BY pr.proposal_id
        """,
        (project_id,),
    )
    contract = fetch_one(
        """
        SELECT c.contract_id, c.agreed_amount, c.start_date, c.status,
               s.full_name AS student_name
        FROM Contract c
        JOIN Student s ON s.student_id = c.student_id
        WHERE c.project_id = %s
        """,
        (project_id,),
    )
    payments = []
    total_paid = Decimal("0.00")
    review = None
    if contract is not None:
        payments = fetch_all(
            """
            SELECT payment_id, amount, payment_date
            FROM Payment
            WHERE contract_id = %s
            ORDER BY payment_date, payment_id
            """,
            (contract["contract_id"],),
        )
        total = fetch_one(
            """
            SELECT COALESCE(SUM(amount), 0) AS total_paid
            FROM Payment
            WHERE contract_id = %s
            """,
            (contract["contract_id"],),
        )
        total_paid = total["total_paid"]
        review = fetch_one(
            """
            SELECT r.rating, r.comment, cl.full_name AS client_name
            FROM Review r
            JOIN Client cl ON cl.client_id = r.client_id
            WHERE r.contract_id = %s
            """,
            (contract["contract_id"],),
        )

    student_rows = fetch_all(
        "SELECT student_id, full_name FROM Student ORDER BY full_name"
    )
    return render_template(
        "project_detail.html",
        project=project,
        proposals=proposals,
        contract=contract,
        payments=payments,
        total_paid=total_paid,
        review=review,
        students=student_rows,
        today=date.today().isoformat(),
    )


@app.route("/projects/<int:project_id>/proposals", methods=["POST"])
def add_proposal(project_id):
    project = fetch_one(
        "SELECT project_id, status FROM Project WHERE project_id = %s",
        (project_id,),
    )
    if project is None:
        flash("Project not found.")
        return redirect(url_for("projects"))
    if project["status"] != "open":
        flash("Proposals are only accepted while the project is open.")
        return redirect(url_for("project_detail", project_id=project_id))

    student_id = parse_int(request.form.get("student_id"))
    cover_letter = form_text("cover_letter")
    bid_amount = parse_money(request.form.get("bid_amount"))
    if student_id is None or not cover_letter or bid_amount is None:
        flash("Student, cover letter, and a bid greater than 0 are required.")
        return redirect(url_for("project_detail", project_id=project_id))

    try:
        execute(
            """
            INSERT INTO Proposal (project_id, student_id, cover_letter, bid_amount)
            VALUES (%s, %s, %s, %s)
            """,
            (project_id, student_id, cover_letter, bid_amount),
        )
    except UniqueViolation:
        flash("That student already sent a proposal for this project.")
        return redirect(url_for("project_detail", project_id=project_id))
    except ForeignKeyViolation:
        flash("Choose a student from the list.")
        return redirect(url_for("project_detail", project_id=project_id))

    flash("Proposal submitted.")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/proposals/<int:proposal_id>/accept", methods=["POST"])
def accept_proposal(proposal_id):
    """Accept one proposal and create the contract in a single transaction."""
    project_id = None
    try:
        with get_conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT pr.proposal_id, pr.project_id, pr.student_id,
                           pr.bid_amount, pr.status,
                           p.client_id, p.status AS project_status
                    FROM Proposal pr
                    JOIN Project p ON p.project_id = pr.project_id
                    WHERE pr.proposal_id = %s
                    """,
                    (proposal_id,),
                )
                proposal = cursor.fetchone()
                if proposal is None:
                    flash("Proposal not found.")
                    return redirect(url_for("projects"))

                project_id = proposal["project_id"]
                if proposal["status"] != "pending" or proposal["project_status"] != "open":
                    flash("Only a pending proposal on an open project can be accepted.")
                    return redirect(url_for("project_detail", project_id=project_id))

                cursor.execute(
                    """
                    UPDATE Proposal
                    SET status = 'rejected'
                    WHERE project_id = %s AND proposal_id <> %s
                    """,
                    (project_id, proposal_id),
                )
                cursor.execute(
                    """
                    UPDATE Proposal
                    SET status = 'accepted'
                    WHERE proposal_id = %s
                    """,
                    (proposal_id,),
                )
                cursor.execute(
                    """
                    INSERT INTO Contract (
                        project_id, proposal_id, student_id, client_id,
                        agreed_amount, start_date, status
                    )
                    VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, 'active')
                    """,
                    (
                        project_id,
                        proposal_id,
                        proposal["student_id"],
                        proposal["client_id"],
                        proposal["bid_amount"],
                    ),
                )
                cursor.execute(
                    """
                    UPDATE Project
                    SET status = 'in_progress'
                    WHERE project_id = %s
                    """,
                    (project_id,),
                )
    except UniqueViolation:
        flash("This project already has a contract.")
        if project_id is None:
            return redirect(url_for("projects"))
        return redirect(url_for("project_detail", project_id=project_id))

    flash("Proposal accepted. A contract was created, and the other proposals were rejected.")
    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/contracts/<int:contract_id>/payments", methods=["POST"])
def add_payment(contract_id):
    contract = fetch_one(
        "SELECT contract_id, project_id FROM Contract WHERE contract_id = %s",
        (contract_id,),
    )
    if contract is None:
        flash("Contract not found.")
        return redirect(url_for("projects"))

    amount = parse_money(request.form.get("amount"))
    payment_date = parse_date(request.form.get("payment_date"))
    if amount is None or payment_date is None:
        flash("Enter an amount greater than 0 and a valid date.")
        return redirect(url_for("project_detail", project_id=contract["project_id"]))

    execute(
        """
        INSERT INTO Payment (contract_id, amount, payment_date)
        VALUES (%s, %s, %s)
        """,
        (contract_id, amount, payment_date),
    )
    flash("Payment recorded.")
    return redirect(url_for("project_detail", project_id=contract["project_id"]))


@app.route("/contracts/<int:contract_id>/review", methods=["POST"])
def add_review(contract_id):
    contract = fetch_one(
        """
        SELECT contract_id, project_id, student_id, client_id
        FROM Contract
        WHERE contract_id = %s
        """,
        (contract_id,),
    )
    if contract is None:
        flash("Contract not found.")
        return redirect(url_for("projects"))

    rating = parse_int(request.form.get("rating"))
    comment = form_text("comment")
    if rating is None or rating > 5:
        flash("Choose a rating from 1 to 5.")
        return redirect(url_for("project_detail", project_id=contract["project_id"]))

    # The review, the contract status, and the project status are saved together.
    # student_id and client_id are copied from the contract.
    try:
        with get_conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Review (contract_id, student_id, client_id, rating, comment)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        contract_id,
                        contract["student_id"],
                        contract["client_id"],
                        rating,
                        comment or None,
                    ),
                )
                cursor.execute(
                    "UPDATE Contract SET status = 'completed' WHERE contract_id = %s",
                    (contract_id,),
                )
                cursor.execute(
                    "UPDATE Project SET status = 'completed' WHERE project_id = %s",
                    (contract["project_id"],),
                )
    except UniqueViolation:
        flash("This contract already has a review.")
        return redirect(url_for("project_detail", project_id=contract["project_id"]))

    flash("Review saved. The project is marked completed.")
    return redirect(url_for("project_detail", project_id=contract["project_id"]))


@app.route("/tables")
def tables():
    return render_template("tables.html")


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("not_found.html"), 404


@app.errorhandler(psycopg.Error)
def database_error(error):
    return render_template(
        "db_error.html",
        message=str(error).strip(),
        hint="Check DATABASE_URL in .env, then run: python init_db.py",
    ), 500


if __name__ == "__main__":
    app.run(debug=True)
