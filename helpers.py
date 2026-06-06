from datetime import date
from model.case import Case
from model.status import Status

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

def get_cases_by_status(status_name):
    cases = (
        Case.query
        .join(Status)
        .filter(Status.status_name == status_name)
        .order_by(Case.deadline_date.asc())
        .all()
    )
    return add_deadline_status(cases)
