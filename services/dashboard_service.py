from datetime import date
from sqlalchemy import func

from database import db
from model.case import Case
from model.status import Status
from model.user import User
from model.log import Log
from model.notes import Notes

def get_dashboard_data():
    today = date.today()

    open_cases = (
        Case.query
        .join(Status)
        .filter(Status.status_name != "closed")
        .count()
    )
    closed_cases = (
        Case.query
        .join(Status)
        .filter(Status.status_name == "closed")
        .count()
    )
    overdue_cases = (
        Case.query
        .join(Status)
        .filter(Status.status_name != "closed")
        .filter(Case.deadline_date < today)
        .count()
    )
    due_today_cases = (
        Case.query
        .join(Status)
        .filter(Status.status_name != "closed")
        .filter(Case.deadline_date == today)
        .count()
    )
    users = User.query.all()

    first_logs_subquery = (
        db.session.query(func.min(Log.log_id).label("first_log_id"))
        .group_by(Log.case_id)
        .subquery()
    )
    user_summary = []

    for user in users:
        total_log_actions = (
            Log.query
            .filter(Log.user_id == user.user_id)
            .count()
        )
        notes_added = (
            Notes.query
            .filter(Notes.user_id == user.user_id)
            .count()
        )
        new_cases = (
            Log.query
            .filter(Log.user_id == user.user_id)
            .filter(Log.log_id.in_(first_logs_subquery))
            .count()
        )
        letter_actions = (
            Log.query
            .join(Status)
            .filter(Log.user_id == user.user_id)
            .filter(Status.status_name == "letter")
            .count()
        )
        chaser_actions = (
            Log.query
            .join(Status)
            .filter(Log.user_id == user.user_id)
            .filter(Status.status_name == "chaser")
            .count()
        )
        chargeback_actions = (
            Log.query
            .join(Status)
            .filter(Log.user_id == user.user_id)
            .filter(Status.status_name == "chargeback")
            .count()
        )
        representment_actions = (
            Log.query
            .join(Status)
            .filter(Log.user_id == user.user_id)
            .filter(Status.status_name == "representment")
            .count()
        )
        closed_actions = (
            Log.query
            .join(Status)
            .filter(Log.user_id == user.user_id)
            .filter(Status.status_name == "closed")
            .count()
        )

        user_summary.append({
            "username": user.username,
            "actions": total_log_actions,
            "notes_added": notes_added,
            "new_cases": new_cases,
            "letter_actions": letter_actions,
            "chaser_actions": chaser_actions,
            "chargeback_actions": chargeback_actions,
            "representment_actions": representment_actions,
            "closed_actions": closed_actions,
            "points": (
                (new_cases * 2)
                + letter_actions
                + chaser_actions
                + chargeback_actions
                + representment_actions
                + closed_actions
            )
        })

    queue_names = ["letter", "chaser", "chargeback", "representment"]
    queue_statistics = []
    for queue_name in queue_names:
        total = (
            Case.query
            .join(Status)
            .filter(Status.status_name == queue_name)
            .count()
        )
        overdue = (
            Case.query
            .join(Status)
            .filter(Status.status_name == queue_name)
            .filter(Case.deadline_date < today)
            .count()
        )
        due_today = (
            Case.query
            .join(Status)
            .filter(Status.status_name == queue_name)
            .filter(Case.deadline_date == today)
            .count()
        )
        queue_statistics.append({
            "queue_name": queue_name,
            "total": total,
            "overdue": overdue,
            "due_today": due_today
        })

    return {
        "open_cases": open_cases,
        "closed_cases": closed_cases,
        "overdue_cases": overdue_cases,
        "due_today_cases": due_today_cases,
        "queue_statistics": queue_statistics,
        "user_summary": user_summary
    }
