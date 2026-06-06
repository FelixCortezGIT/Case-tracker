import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from datetime import date

from database import db
from model.case import Case
from model.status import Status
from model.user import User
from model.log import Log
from model.notes import Notes

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

# temporary user until login is ready
SYSTEM_USER_ID = 1

db.init_app(app)

def add_deadline_status(cases):
    today = date.today()
    for case in cases:
        if case.deadline_date is None:
            case.deadline_status = "normal"
        elif case.deadline_date < today:
            case.deadline_status = "overdue"
        elif case.deadline_date == today:
            case.deadline_status = "due-today"
        else:
            case.deadline_status = "normal"
    return cases

def get_system_user():
    """Temporary fallback user until real login exists."""
    user = User.query.get(SYSTEM_USER_ID)
    if user is None:
        user = User(
            user_id=SYSTEM_USER_ID,
            username="system",
            password_hash="temporary",
            role="admin"
        )
        db.session.add(user)
        db.session.flush()
    return user

@app.route("/")
def home():
    return "home page"

@app.route("/new_case", methods=["GET", "POST"])
def new_case():
    if request.method == "POST":
        status_name = request.form.get("status")
        note_text = request.form.get("note_text")

        selected_status = Status.query.filter_by(
            status_name=status_name
        ).first()

        if selected_status is None:
            return "Error: selected status does not exist in database", 400

        system_user = get_system_user()

        new_case_record = Case(
            customer_name=request.form.get("customer_name"),
            card_number=request.form.get("card_number"),
            transaction_amount=request.form.get("transaction_amount"),
            transaction_date=request.form.get("transaction_date"),
            merchant_name=request.form.get("merchant_name"),
            deadline_date=request.form.get("deadline"),
            status_id=selected_status.status_id
        )
        db.session.add(new_case_record)
        db.session.flush()

        new_note = None
        if note_text and note_text.strip():
            new_note = Notes(
                case_id=new_case_record.case_id,
                user_id=system_user.user_id,
                note_text=note_text.strip()
            )
            db.session.add(new_note)
            db.session.flush()

        new_log = Log(
            case_id=new_case_record.case_id,
            user_id=system_user.user_id,
            status_id=selected_status.status_id,
            deadline_date=request.form.get("deadline"),
            notes_id=new_note.note_id if new_note else None
        )
        db.session.add(new_log)
        db.session.commit()

        return redirect(url_for("case_detail", case_id=new_case_record.case_id))

    return render_template("new_case.html")

@app.route("/case_detail")
def case_detail():
    case_id = request.args.get("case_id")
    case_id_search = request.args.get("case_id_search")
    card_search = request.args.get("card_search")
    customer_search = request.args.get("customer_search")

    selected_case = None
    search_results = []
    notes = []
    logs = []

    if case_id:
        selected_case = Case.query.get(case_id)

    elif case_id_search:
        search_results = (
            Case.query
            .filter(Case.case_id == case_id_search)
            .order_by(Case.case_id.desc())
            .all()
        )

    elif card_search:
        search_results = (
            Case.query
            .filter(Case.card_number.ilike(f"%{card_search}%"))
            .order_by(Case.case_id.desc())
            .all()
        )

    elif customer_search:
        search_results = (
            Case.query
            .filter(Case.customer_name.ilike(f"%{customer_search}%"))
            .order_by(Case.case_id.desc())
            .all()
        )

    if selected_case:
        notes = Notes.query.filter_by(case_id=selected_case.case_id).order_by(Notes.created_at.desc()).all()
        logs = Log.query.filter_by(case_id=selected_case.case_id).order_by(Log.created_at.desc()).all()

    return render_template(
        "case_detail.html",
        selected_case=selected_case,
        search_results=search_results,
        notes=notes,
        logs=logs
    )

@app.route("/case/<int:case_id>/add_note", methods=["POST"])
def add_note(case_id):
    selected_case = Case.query.get_or_404(case_id)
    note_text = request.form.get("note_text")

    if note_text and note_text.strip():
        system_user = get_system_user()

        new_note = Notes(
            case_id=selected_case.case_id,
            user_id=system_user.user_id,
            note_text=note_text.strip()
        )
        db.session.add(new_note)
        db.session.flush()

        new_log = Log(
            case_id=selected_case.case_id,
            user_id=system_user.user_id,
            status_id=selected_case.status_id,
            deadline_date=selected_case.deadline_date,
            notes_id=new_note.note_id
        )
        db.session.add(new_log)
        db.session.commit()

    return redirect(url_for("case_detail", case_id=selected_case.case_id))

@app.route("/letter_ques")
def letter_queue():
    cases = Case.query.join(Status).filter(Status.status_name == "letter").order_by(Case.deadline_date.asc()).all()
    cases = add_deadline_status(cases)
    return render_template("letter_ques.html", cases=cases)

@app.route("/chaser_ques")
def chaser_queue():
    cases = Case.query.join(Status).filter(Status.status_name == "chaser").order_by(Case.deadline_date.asc()).all()
    cases = add_deadline_status(cases)
    return render_template("chaser_ques.html", cases=cases)

@app.route("/chargeback_ques")
def chargeback_queue():
    cases = Case.query.join(Status).filter(Status.status_name == "chargeback").order_by(Case.deadline_date.asc()).all()
    cases = add_deadline_status(cases)
    return render_template("chargeback_ques.html", cases=cases)

@app.route("/representment_ques")
def representment_queue():
    cases = Case.query.join(Status).filter(Status.status_name == "representment").order_by(Case.deadline_date.asc()).all()
    cases = add_deadline_status(cases)
    return render_template("representment_ques.html", cases=cases)

@app.route("/case/<int:case_id>/update_case", methods=["POST"])
def update_case(case_id):
    selected_case = Case.query.get_or_404(case_id)

    status_name = request.form.get("status")
    deadline = request.form.get("deadline")
    note_text = request.form.get("note_text")

    selected_status = Status.query.filter_by(
        status_name=status_name
    ).first()

    if selected_status is None:
        return "Error: selected status does not exist in database", 400

    system_user = get_system_user()

    selected_case.status_id = selected_status.status_id
    new_note = None

    if note_text and note_text.strip():
        new_note = Notes(
            case_id=selected_case.case_id,
            user_id=system_user.user_id,
            note_text=note_text.strip()
        )
        db.session.add(new_note)
        db.session.flush()

    if status_name == "closed":
        selected_case.deadline_date = None
        deadline_for_log = None
    else:
        selected_case.deadline_date = deadline
        deadline_for_log = deadline

    new_log = Log(
        case_id=selected_case.case_id,
        user_id=system_user.user_id,
        status_id=selected_status.status_id,
        deadline_date=deadline_for_log,
        notes_id=new_note.note_id if new_note else None
    )

    db.session.add(new_log)
    db.session.commit()

    return redirect(url_for("case_detail", case_id=selected_case.case_id))

# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
