from datetime import date, datetime, timedelta
from sqlalchemy import func

from database import db
from model.case import Case
from model.status import Status
from model.user import User
from model.log import Log
from model.notes import Notes

def get_activity_date_range(activity_filter, date_range, today):
    if activity_filter == "yesterday":
        start_date = today - timedelta(days=1)
        end_date = today - timedelta(days=1)
    elif activity_filter == "last_7_days":
        start_date = today - timedelta(days=6)
        end_date = today
    elif activity_filter == "this_month":
        start_date = today.replace(day=1)
        end_date = today
    elif activity_filter == "custom" and date_range:
        selected_dates = date_range.split(" to ")
        if len(selected_dates) == 2:
            start_date = datetime.strptime(selected_dates[0], "%Y-%m-%d").date()
            end_date = datetime.strptime(selected_dates[1], "%Y-%m-%d").date()
        else:
            start_date = today
            end_date = today
    else:
        start_date = today
        end_date = today
    return start_date, end_date

def get_dashboard_data(activity_filter="today", date_range=None):
    today = date.today()
    activity_start, activity_end = get_activity_date_range(activity_filter, date_range, today)
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
    activity_summary = {
        "new_cases": (
            Log.query
            .filter(Log.log_id.in_(first_logs_subquery))
            .filter(func.date(Log.created_at) >= activity_start)
            .filter(func.date(Log.created_at) <= activity_end)
            .count()
        ),
        "letter": (
            Log.query
            .join(Status)
            .filter(Status.status_name == "letter")
            .filter(func.date(Log.created_at) >= activity_start)
            .filter(func.date(Log.created_at) <= activity_end)
            .count()
        ),
        "chaser": (
            Log.query
            .join(Status)
            .filter(Status.status_name == "chaser")
            .filter(func.date(Log.created_at) >= activity_start)
            .filter(func.date(Log.created_at) <= activity_end)
            .count()
        ),
        "chargeback": (
            Log.query
            .join(Status)
            .filter(Status.status_name == "chargeback")
            .filter(func.date(Log.created_at) >= activity_start)
            .filter(func.date(Log.created_at) <= activity_end)
            .count()
        ),
        "representment": (
            Log.query
            .join(Status)
            .filter(Status.status_name == "representment")
            .filter(func.date(Log.created_at) >= activity_start)
            .filter(func.date(Log.created_at) <= activity_end)
            .count()
        ),
        "closed": (
            Log.query
            .join(Status)
            .filter(Status.status_name == "closed")
            .filter(func.date(Log.created_at) >= activity_start)
            .filter(func.date(Log.created_at) <= activity_end)
            .count()
        ),

        "total_actions": (
            Log.query
            .join(Status)
            .filter(Status.status_name.in_(["letter", "chaser", "chargeback", "representment", "closed"]))
            .filter(func.date(Log.created_at) >= activity_start)
            .filter(func.date(Log.created_at) <= activity_end)
            .count()
        )
    }
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
        "user_summary": user_summary,
        "activity_summary": activity_summary,
        "activity_filter": activity_filter,
    }
