from flask import url_for
from models import db, Notification, Follow


def add_post_notifications(post):
    followers = Follow.query.filter_by(followed_id=post.author.id).all()
    for follower in followers:
        notification = Notification(
            user_id=follower.follower_id,
            message=f'User {post.author.username} has just created a new post "{post.title}"',
            sender_id=post.author.id,
            target_id=post.id,
            type="post",
            link=url_for('posts.index', _anchor=f'readMoreModal{post.id}')
        )
        db.session.add(notification)
    db.session.commit()
