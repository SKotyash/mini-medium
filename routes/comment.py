from datetime import datetime

from flask import Blueprint, request, session, render_template, redirect, url_for, flash
from services import notify_user_about_new_comment, remove_comment_notification, get_mute_status
from decorators import moderator_required, login_required
from models import Comment, db, User, Post


coment_bp = Blueprint('comment', __name__)


@coment_bp.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    if request.method == 'POST':
        content = request.form['comment']
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        mute_status=get_mute_status(user)
        if mute_status:
            flash(f'You are muted try in {mute_status['hours']} hours {mute_status['minutes']} minutes.', 'danger')
            clean_url = request.referrer.split('#')[0]
            return redirect(f"{clean_url}#readMoreModal{post_id}")
        post = Post.query.get_or_404(post_id)
        comment = Comment(post_id=post_id, user_id=user_id, content=content)
        try:
            db.session.add(comment)
            db.session.commit()
            notify_user_about_new_comment(user, post, comment)
            clean_url = request.referrer.split('#')[0]
            return redirect(f"{clean_url}#readMoreModal{post_id}")

        except Exception as e:
            print(e)
            return render_template('index.html', error=e)


@coment_bp.route('/delete/<int:comment_id>', methods=['POST'])
@login_required
@moderator_required
def delete_comment(comment_id):
    if request.method == 'POST':
        comment_to_delete = Comment.query.filter_by(id=comment_id).first_or_404()
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        remove_comment_notification(user, comment_to_delete)

        db.session.delete(comment_to_delete)
        db.session.commit()
        return redirect(request.referrer or url_for('posts.index'))
