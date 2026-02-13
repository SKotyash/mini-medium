from datetime import datetime, timedelta

from flask import Flask, session
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_apscheduler import APScheduler
import os

from models import db, Notification, User
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.comment import coment_bp
from routes.follow import follow_bp
from routes.notifications import notes_bp
from routes.posts import posts_bp
from services import add_unmute_notification

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db.init_app(app)
csrf = CSRFProtect(app)

migrate = Migrate(app, db)

app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(coment_bp)
app.register_blueprint(follow_bp)
app.register_blueprint(notes_bp)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
@scheduler.task('interval', id='remove_expired_mutes',minutes=5)
def remove_expired_mutes():
    with app.app_context():
        now = datetime.now()
        deadline = now - timedelta(hours=24)
        expired_mutes = User.query.filter(User.is_muted==True,User.mute_date <= deadline).all()
        for u in expired_mutes:
            u.is_muted = False
            u.mute_date = None
            add_unmute_notification(u.id)
        if expired_mutes:
            print(f'Removed expired mutes {len(expired_mutes)}')

@app.context_processor
def inject_notifications():
    if session.get('user_id'):
        notes=(Notification.query.filter_by(user_id=session['user_id'])
               .order_by(Notification.created_at.desc())
               .limit(5).all())
        unread_count=Notification.query.filter_by(user_id=session.get('user_id'),is_read=False).count()
        return dict(notifications=notes, unread_notifications=unread_count>0)
    return dict(notifications=[], unread_notifications=False)


if __name__ == '__main__':
    app.run(debug=True)
