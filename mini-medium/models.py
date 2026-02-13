from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email=db.Column(db.String(40), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    is_banned = db.Column(db.Boolean, nullable=False, default=False)
    is_muted = db.Column(db.Boolean, nullable=False, default=False)
    mute_date = db.Column(db.DateTime, nullable=True)

    def set_moderator(self):
        self.role = 'moderator'

    def unset_moderator(self):
        self.role = 'user'

    def set_banned(self):
        self.is_banned = True

    def unset_banned(self):
        self.is_banned = False

    def mute(self):
        self.is_muted = True
        self.mute_date = datetime.now()

    def unmute(self):
        self.is_muted = False
        self.mute_date = None

    def get_avatar(self, size=100):
        return f"https://api.dicebear.com/9.x/adventurer-neutral/svg?seed={self.username}&size={size}"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(80), nullable=False, default='draft')
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    likes = db.relationship('Like', backref='post', cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='post', cascade="all, delete-orphan")

    def edit_post(self, title, content):
        self.updated_at = func.now()
        self.title = title
        self.content = content
        if self.status != 'draft':
            self.status = 'on-review'

    def send_on_review(self):
        self.status = 'on-review'

    def confirm_publish(self):
        self.status = 'published'

    def reject_publish(self):
        self.status = 'rejected'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    author = db.relationship('User', backref='my_comments')


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Обов'язково
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    follower = db.relationship('User', foreign_keys=[follower_id], backref='following')
    followed = db.relationship('User', foreign_keys=[followed_id], backref='followers')
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message=db.Column(db.Text, nullable=False)
    is_read=db.Column(db.Boolean, nullable=False,default=False)
    sender_id=db.Column(db.Integer,  nullable=False)
    target_id=db.Column(db.Integer,  nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    type = db.Column(db.String(20))
    link = db.Column(db.String(255))
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

class Logs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message=db.Column(db.Text, nullable=False)
    target_id=db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    type = db.Column(db.String(20))