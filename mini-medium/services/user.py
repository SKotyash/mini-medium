import re
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from app import db


def is_valid(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

def update_user_settings(user_id,username, email, new_password, current_password):
    user = User.query.get(user_id)
    if not user:
        return False, "User not found"
    if not check_password_hash(user.password_hash, current_password):
        return False, "Wrong current password"
    if not is_valid(email):
        return False, "Invalid email"
    user.email = email
    user.username = username
    if new_password and len(new_password) > 0:
        user.password_hash = generate_password_hash(new_password)
    try:
        db.session.commit()
        return True, "User updated successfully"
    except Exception as e:
        print(e)
        db.session.rollback()
        return False, "Error updating user"

