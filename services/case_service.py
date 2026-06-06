from database import db
from model.case import Case
from model.status import Status
from model.notes import Notes
from model.log import Log

def get_case_detail_data(case_id=None, case_id_search=None, card_search=None, customer_search=None):
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
        notes = (
            Notes.query
            .filter_by(case_id=selected_case.case_id)
            .order_by(Notes.created_at.desc())
            .all()
        )
        logs = (
            Log.query
            .filter_by(case_id=selected_case.case_id)
            .order_by(Log.created_at.desc())
            .all()
        )
    return {
        "selected_case": selected_case,
        "search_results": search_results,
        "notes": notes,
        "logs": logs
    }

def create_new_case(form_data, current_user):
    status_name = form_data.get("status")
    note_text = form_data.get("note_text")
    selected_status = Status.query.filter_by(
        status_name=status_name
    ).first()
    if selected_status is None:
        return None
    new_case_record = Case(
        customer_name=form_data.get("customer_name"),
        card_number=form_data.get("card_number"),
        transaction_amount=form_data.get("transaction_amount"),
        transaction_date=form_data.get("transaction_date"),
        merchant_name=form_data.get("merchant_name"),
        deadline_date=form_data.get("deadline"),
        status_id=selected_status.status_id
    )
    db.session.add(new_case_record)
    db.session.flush()
    new_note = None
    if note_text and note_text.strip():
        new_note = Notes(
            case_id=new_case_record.case_id,
            user_id=current_user.user_id,
            note_text=note_text.strip()
        )
        db.session.add(new_note)
        db.session.flush()
    new_log = Log(
        case_id=new_case_record.case_id,
        user_id=current_user.user_id,
        status_id=selected_status.status_id,
        deadline_date=form_data.get("deadline"),
        notes_id=new_note.note_id if new_note else None
    )
    db.session.add(new_log)
    db.session.commit()
    return new_case_record

def add_case_note(case_id, note_text, current_user):
    selected_case = Case.query.get_or_404(case_id)
    if note_text and note_text.strip():
        new_note = Notes(
            case_id=selected_case.case_id,
            user_id=current_user.user_id,
            note_text=note_text.strip()
        )
        db.session.add(new_note)
        db.session.flush()
        new_log = Log(
            case_id=selected_case.case_id,
            user_id=current_user.user_id,
            status_id=selected_case.status_id,
            deadline_date=selected_case.deadline_date,
            notes_id=new_note.note_id
        )
        db.session.add(new_log)
        db.session.commit()
    return selected_case

def update_existing_case(case_id, form_data, current_user):
    selected_case = Case.query.get_or_404(case_id)
    status_name = form_data.get("status")
    deadline = form_data.get("deadline")
    note_text = form_data.get("note_text")
    selected_status = Status.query.filter_by(
        status_name=status_name
    ).first()
    if selected_status is None:
        return None
    selected_case.status_id = selected_status.status_id
    new_note = None
    if note_text and note_text.strip():
        new_note = Notes(
            case_id=selected_case.case_id,
            user_id=current_user.user_id,
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
        user_id=current_user.user_id,
        status_id=selected_status.status_id,
        deadline_date=deadline_for_log,
        notes_id=new_note.note_id if new_note else None
    )
    db.session.add(new_log)
    db.session.commit()
    return selected_case
