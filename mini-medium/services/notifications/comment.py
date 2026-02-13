from flask import url_for
from models import db, Notification


def notify_user_about_new_comment(user, post, comment):
    if user.id == post.author_id:
        return

    notification = Notification(
        user_id=post.author_id,
        message=f'User {user.username} commented "{comment.content}" on "{post.title}"',
        sender_id=user.id,
        target_id=comment.id,
        type="comment",
        link=url_for('posts.index', _anchor=f'readMoreModal{post.id}')
    )
    db.session.add(notification)
    db.session.commit()


def remove_comment_notification(user, comment):
    notification = Notification.query.filter_by(
        sender_id=user.id,
        target_id=comment.id,
        type="comment"
    ).first()

    if notification:
        db.session.delete(notification)
        db.session.commit()
