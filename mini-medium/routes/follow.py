from flask import Blueprint, request, session, render_template, redirect, url_for, flash

from decorators import login_required
from models import User, Follow, db
from services import add_follow_notification, delete_follow_notification
follow_bp = Blueprint('follow', __name__)


@follow_bp.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    followed_id = user_id
    follower_id = int(session.get('user_id'))
    if follower_id == followed_id:
        flash('You cannot follow yourself', category='error')
        return redirect(request.referrer or url_for('posts.index'))

    user = User.query.get_or_404(followed_id)
    follower=User.query.get_or_404(follower_id)

    follow = Follow.query.filter_by(followed_id=user_id, follower_id=follower_id).first()
    if follow:
        db.session.delete(follow)
        delete_follow_notification(user,follower)
    else:
        new_follow = Follow(followed_id=user_id, follower_id=follower_id)
        add_follow_notification(user,follower)
        db.session.add(new_follow)

    db.session.commit()
    return redirect(request.referrer or url_for('posts.index'))
