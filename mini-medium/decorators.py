from functools import wraps

from flask import session, flash, redirect, url_for, request

from models import User


def moderator_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('role') in ['moderator', 'admin']:
            return f(*args, **kwargs)
        else:
            flash('You do not have access to this page.', 'danger')
            return redirect(url_for('posts.index'))

    return wrap


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('role') == 'admin':
            return f(*args, **kwargs)
        else:
            flash('You do not have access to this page.', 'danger')
            return redirect(url_for('posts.index'))

    return wrap


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('posts.index', _anchor='loginModal'))
        user = User.query.get(user_id)
        if user and user.is_banned:
            flash('You have been banned.', 'danger')
            session.clear()
            return redirect(url_for('posts.index'))
        return f(*args, **kwargs)

    return wrap
