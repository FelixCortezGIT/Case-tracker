from flask import session, redirect, url_for
from model.user import User

def get_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return User.query.get(user_id)

def login_required():
    if session.get("user_id") is None:
        return redirect(url_for("login"))
    return None

def manager_required():
    if session.get("user_id") is None:
        return redirect(url_for("login"))
    if session.get("role") != "manager":
        return redirect(url_for("new_case"))
    return None
