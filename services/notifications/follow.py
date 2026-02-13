from flask import url_for
from models import db, Notification


def add_follow_notification(user, follower):
    notification = Notification(
        user_id=user.id,
        message=f"You have been followed by {follower.username}",
        sender_id=follower.id,
        target_id=user.id,
        type="follow",
        link=url_for('auth.profile', user_id=follower.id)
    )
    db.session.add(notification)
    db.session.commit()


def delete_follow_notification(user, follower):
    notification = Notification.query.filter_by(
        user_id=user.id,
        sender_id=follower.id,
        type="follow"
    ).first()

    if notification:
        db.session.delete(notification)
        db.session.commit()
