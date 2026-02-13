from datetime import datetime, timedelta
from flask import url_for, session, has_request_context
from models import db, Notification


def get_mute_status(user):
    if not user.is_muted:
        return False

    deadline = user.mute_date + timedelta(hours=24)
    now = datetime.now()

    if now >= deadline:
        return False

    time_left = deadline - now
    total_seconds = int(time_left.total_seconds())

    return {
        "hours": total_seconds // 3600,
        "minutes": (total_seconds % 3600) // 60
    }


def add_mute_notification(user_id):
    notification = Notification(
        user_id=user_id,
        message="You have been muted by administration for 24h",
        sender_id=session.get('user_id'),
        target_id=user_id,
        type="mute",
        link=url_for('posts.index')
    )
    db.session.add(notification)
    db.session.commit()


def add_unmute_notification(user_id):
    admin_id = session.get('user_id') if has_request_context() else 3

    notification = Notification(
        user_id=user_id,
        message="You have been unmuted",
        sender_id=admin_id,
        target_id=user_id,
        type="unmute",
        link=url_for('posts.index')
    )
    db.session.add(notification)
    db.session.commit()
