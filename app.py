import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session

from database import db
from helpers import get_cases_by_status
from auth_helpers import get_current_user, login_required, manager_required
from services.dashboard_service import get_dashboard_data
from services.case_service import (
    get_case_detail_data,
    create_new_case,
    add_case_note,
    update_existing_case
)
from services.auth_service import authenticate_user, create_user

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

db.init_app(app)

@app.route("/")
def home():
    return "home page"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = authenticate_user(username, password)
        if user is None:
            return render_template("login.html", error="Invalid username or password")
        session["user_id"] = user.user_id
        session["username"] = user.username
        session["role"] = user.role
        return redirect(url_for("new_case"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    auth_check = manager_required()
    if auth_check:
        return auth_check
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")
        user_created = create_user(username, password, role)
        if not user_created:
            return render_template(
                "register.html",
                error="Username already exists"
            )
        return render_template(
            "register.html",
            success="User created successfully"
        )
    return render_template("register.html")

@app.route("/new_case", methods=["GET", "POST"])
def new_case():
    auth_check = login_required()
    if auth_check:
        return auth_check
    if request.method == "POST":
        current_user = get_current_user()
        new_case_record = create_new_case(
            form_data=request.form,
            current_user=current_user
        )
        if new_case_record is None:
            return "Error: selected status does not exist in database", 400
        return redirect(url_for("case_detail", case_id=new_case_record.case_id))
    return render_template("new_case.html")

@app.route("/case_detail")
def case_detail():
    auth_check = login_required()
    if auth_check:
        return auth_check
    case_data = get_case_detail_data(
        case_id=request.args.get("case_id"),
        case_id_search=request.args.get("case_id_search"),
        card_search=request.args.get("card_search"),
        customer_search=request.args.get("customer_search")
    )
    return render_template(
        "case_detail.html",
        **case_data
    )

@app.route("/case/<int:case_id>/add_note", methods=["POST"])
def add_note(case_id):
    auth_check = login_required()
    if auth_check:
        return auth_check
    current_user = get_current_user()
    selected_case = add_case_note(
        case_id=case_id,
        note_text=request.form.get("note_text"),
        current_user=current_user
    )
    return redirect(url_for("case_detail", case_id=selected_case.case_id))

@app.route("/letter_ques")
def letter_queue():
    auth_check = login_required()
    if auth_check:
        return auth_check
    cases = get_cases_by_status("letter")
    return render_template("letter_ques.html", cases=cases)

@app.route("/chaser_ques")
def chaser_queue():
    auth_check = login_required()
    if auth_check:
        return auth_check
    cases = get_cases_by_status("chaser")
    return render_template("chaser_ques.html", cases=cases)

@app.route("/chargeback_ques")
def chargeback_queue():
    auth_check = login_required()
    if auth_check:
        return auth_check
    cases = get_cases_by_status("chargeback")
    return render_template("chargeback_ques.html", cases=cases)

@app.route("/representment_ques")
def representment_queue():
    auth_check = login_required()
    if auth_check:
        return auth_check
    cases = get_cases_by_status("representment")
    return render_template("representment_ques.html", cases=cases)

@app.route("/manager_dashboard")
def manager_dashboard():
    auth_check = manager_required()
    if auth_check:
        return auth_check
    dashboard_data = get_dashboard_data()
    return render_template(
        "manager_dashboard.html",
        **dashboard_data
    )

@app.route("/case/<int:case_id>/update_case", methods=["POST"])
def update_case(case_id):
    auth_check = login_required()
    if auth_check:
        return auth_check
    current_user = get_current_user()
    selected_case = update_existing_case(
        case_id=case_id,
        form_data=request.form,
        current_user=current_user
    )
    if selected_case is None:
        return "Error: selected status does not exist in database", 400
    return redirect(url_for("case_detail", case_id=selected_case.case_id))

# with app.app_context():
#     db.create_all()

# with app.app_context():
#     print(generate_password_hash("manager123"))

if __name__ == "__main__":
    app.run(debug=True)
