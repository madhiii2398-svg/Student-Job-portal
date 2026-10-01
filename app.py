import os
import json
import hashlib
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)

app = Flask(__name__)
app.secret_key = "student-job-portal-secret-key-2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_FILE = os.path.join(BASE_DIR, "students.json")
JOBS_FILE = os.path.join(BASE_DIR, "jobs.json")
APPLICATIONS_FILE = os.path.join(BASE_DIR, "applications.json")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

VALID_STATUSES = ["Applied", "Shortlisted", "Selected", "Rejected"]


# ---------------------------------------------------------------------------
# JSON helper functions
# ---------------------------------------------------------------------------

def load_json(filepath):
    """Load data from a JSON file. Returns an empty list if file is missing."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_json(filepath, data):
    """Save data to a JSON file with pretty formatting."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_students():
    return load_json(STUDENTS_FILE)


def save_students(students):
    save_json(STUDENTS_FILE, students)


def load_jobs():
    return load_json(JOBS_FILE)


def save_jobs(jobs):
    save_json(JOBS_FILE, jobs)


def load_applications():
    return load_json(APPLICATIONS_FILE)


def save_applications(applications):
    save_json(APPLICATIONS_FILE, applications)


def get_next_id(items):
    """Return the next integer ID for a list of dict items."""
    if not items:
        return 1
    max_id = max(item.get("id", 0) for item in items)
    return max_id + 1


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "student_id" not in session:
            flash("Please log in to access that page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            flash("Please log in as admin to access that page.", "error")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    jobs = load_jobs()
    featured_jobs = jobs[:6]
    return render_template("index.html", jobs=featured_jobs, job_count=len(jobs))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        skills = request.form.get("skills", "").strip()
        qualification = request.form.get("qualification", "").strip()

        if not name or not email or not password:
            flash("Name, email, and password are required.", "error")
            return render_template("register.html")

        students = load_students()

        # Check for duplicate email
        if any(s["email"] == email for s in students):
            flash("An account with that email already exists. Please log in.", "error")
            return render_template("register.html")

        new_student = {
            "id": get_next_id(students),
            "name": name,
            "email": email,
            "password": hash_password(password),
            "skills": skills,
            "qualification": qualification,
        }
        students.append(new_student)
        save_students(students)

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        students = load_students()
        hashed = hash_password(password)

        student = next((s for s in students if s["email"] == email and s["password"] == hashed), None)

        if student is None:
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session["student_id"] = student["id"]
        session["student_name"] = student["name"]
        flash("Welcome back, " + student["name"] + "!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("student_id", None)
    session.pop("student_name", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Job routes
# ---------------------------------------------------------------------------

@app.route("/jobs")
def jobs():
    all_jobs = load_jobs()
    query = request.args.get("q", "").strip().lower()

    if query:
        filtered = []
        for job in all_jobs:
            title = job.get("title", "").lower()
            company = job.get("company", "").lower()
            skills = job.get("skills", "").lower()
            if query in title or query in company or query in skills:
                filtered.append(job)
        all_jobs = filtered

    return render_template("jobs.html", jobs=all_jobs, query=request.args.get("q", ""))


@app.route("/apply/<int:job_id>")
@login_required
def apply_job(job_id):
    jobs = load_jobs()
    job = next((j for j in jobs if j["id"] == job_id), None)

    if job is None:
        flash("Job not found.", "error")
        return redirect(url_for("jobs"))

    applications = load_applications()
    student_id = session["student_id"]

    # Prevent duplicate applications
    already_applied = any(
        a["student_id"] == student_id and a["job_id"] == job_id
        for a in applications
    )
    if already_applied:
        flash("You have already applied for this job.", "error")
        return redirect(url_for("jobs"))

    new_application = {
        "id": get_next_id(applications),
        "student_id": student_id,
        "student_name": session.get("student_name", ""),
        "job_id": job_id,
        "job_title": job.get("title", ""),
        "company": job.get("company", ""),
        "status": "Applied",
    }
    applications.append(new_application)
    save_applications(applications)

    flash("You have successfully applied for " + job.get("title", "") + "!", "success")
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------------
# Student dashboard
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    student_id = session["student_id"]
    applications = load_applications()
    student_apps = [a for a in applications if a["student_id"] == student_id]

    # Status summary
    status_counts = {}
    for status in VALID_STATUSES:
        status_counts[status] = sum(1 for a in student_apps if a["status"] == status)

    students = load_students()
    student = next((s for s in students if s["id"] == student_id), None)

    return render_template(
        "dashboard.html",
        applications=student_apps,
        status_counts=status_counts,
        student=student,
        total_applications=len(student_apps),
    )


# ---------------------------------------------------------------------------
# Admin routes
# ---------------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            flash("Admin login successful.", "success")
            return redirect(url_for("admin"))
        else:
            flash("Invalid admin credentials.", "error")
            return render_template("admin_login.html")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    flash("Admin logged out.", "success")
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin():
    jobs = load_jobs()
    applications = load_applications()
    students = load_students()

    status_counts = {}
    for status in VALID_STATUSES:
        status_counts[status] = sum(1 for a in applications if a["status"] == status)

    return render_template(
        "admin.html",
        jobs=jobs,
        applications=applications,
        students=students,
        status_counts=status_counts,
        total_jobs=len(jobs),
        total_applications=len(applications),
        total_students=len(students),
    )


@app.route("/admin/add-job", methods=["GET", "POST"])
@admin_required
def add_job():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        company = request.form.get("company", "").strip()
        description = request.form.get("description", "").strip()
        skills = request.form.get("skills", "").strip()
        location = request.form.get("location", "").strip()
        salary = request.form.get("salary", "").strip()

        if not title or not company:
            flash("Job title and company are required.", "error")
            return render_template("add_job.html")

        jobs = load_jobs()
        new_job = {
            "id": get_next_id(jobs),
            "title": title,
            "company": company,
            "description": description,
            "skills": skills,
            "location": location,
            "salary": salary,
        }
        jobs.append(new_job)
        save_jobs(jobs)

        flash("Job '" + title + "' added successfully!", "success")
        return redirect(url_for("admin"))

    return render_template("add_job.html")


@app.route("/admin/update-status/<int:application_id>", methods=["POST"])
@admin_required
def update_status(application_id):
    new_status = request.form.get("status", "").strip()

    if new_status not in VALID_STATUSES:
        flash("Invalid status.", "error")
        return redirect(url_for("admin"))

    applications = load_applications()
    app_record = next((a for a in applications if a["id"] == application_id), None)

    if app_record is None:
        flash("Application not found.", "error")
        return redirect(url_for("admin"))

    app_record["status"] = new_status
    save_applications(applications)

    flash("Application status updated to '" + new_status + "'.", "success")
    return redirect(url_for("admin"))


@app.route("/admin/delete-job/<int:job_id>")
@admin_required
def delete_job(job_id):
    jobs = load_jobs()
    job = next((j for j in jobs if j["id"] == job_id), None)

    if job is None:
        flash("Job not found.", "error")
        return redirect(url_for("admin"))

    jobs = [j for j in jobs if j["id"] != job_id]
    save_jobs(jobs)

    # Also remove applications for this job
    applications = load_applications()
    applications = [a for a in applications if a["job_id"] != job_id]
    save_applications(applications)

    flash("Job '" + job.get("title", "") + "' deleted.", "success")
    return redirect(url_for("admin"))


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template("index.html", jobs=[], job_count=0), 404


@app.errorhandler(500)
def internal_error(e):
    flash("Something went wrong on our end. Please try again.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
