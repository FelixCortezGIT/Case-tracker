from werkzeug.security import generate_password_hash, check_password_hash

from database import db
from model.user import User

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return None
    if not check_password_hash(user.password_hash, password):
        return None
    return user

def create_user(username, password, role):
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return False
    new_user = User(
        username=username,
        password_hash=generate_password_hash(password),
        role=role
    )
    db.session.add(new_user)
    db.session.commit()
    return True
