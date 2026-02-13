from flask import url_for
from models import db, Notification


def add_like_notification(user, post):
    if user.id == post.author_id:
        return

    notification = Notification(
        user_id=post.author_id,
        message=f'User {user.username} has just liked post "{post.title}"',
        sender_id=user.id,
        target_id=post.id,
        type="like",
        link=url_for('posts.index', _anchor=f'readMoreModal{post.id}')
    )
    db.session.add(notification)
    db.session.commit()


def remove_like_notification(user, post):
    notification = Notification.query.filter_by(
        sender_id=user.id,
        target_id=post.id,
        type="like"
    ).first()

    if notification:
        db.session.delete(notification)
        db.session.commit()
