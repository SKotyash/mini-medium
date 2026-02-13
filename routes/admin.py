from datetime import datetime

from decorators import moderator_required, admin_required, login_required
from flask import request, render_template, session, Blueprint, redirect, url_for, flash, send_file

from models import User, Post, db
from services.audit_log import log_user_banned, log_user_unbanned, log_user_muted, log_user_unmuted, log_post_approved, \
    log_post_rejected, log_moderator_promoted, log_moderator_unpromoted, export_logs

admin_bp = Blueprint('admin', __name__, template_folder='templates')


@admin_bp.route('/adminpanel')
@login_required
@moderator_required
def adminpanel():
    posts = Post.query.filter_by(status="on-review").all()
    return render_template('adminpanel.html', posts=posts)


@admin_bp.route('/confirm/<int:post_id>', methods=['POST'])
@login_required
@moderator_required
def confirm(post_id):
    post = Post.query.get_or_404(post_id)
    post.confirm_publish()
    db.session.commit()
    log_post_approved(session.get('user_id'),post_id)
    return redirect(url_for('admin.adminpanel'))


@admin_bp.route('/reject/<int:post_id>', methods=['POST'])
@login_required
@moderator_required
def reject(post_id):
    post = Post.query.get_or_404(post_id)
    post.reject_publish()
    db.session.commit()
    log_post_rejected(session.get('user_id'), post_id)
    return redirect(url_for('admin.adminpanel'))


@admin_bp.route('/promote/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def promote(user_id):
    user_to_promote = User.query.get_or_404(user_id)
    if user_to_promote.role == 'admin':
        flash("You can't promote admins.!", "danger")
        return redirect(url_for('posts.index'))
    user_to_promote.set_moderator()
    db.session.commit()
    log_moderator_promoted(session.get('user_id'), user_to_promote.id)
    return redirect(url_for('posts.index'))


@admin_bp.route('/demote/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def demote(user_id):
    user_to_demote = User.query.filter_by(id=user_id).first()
    if user_to_demote.role == 'moderator':
        user_to_demote.unset_moderator()
        db.session.commit()
        log_moderator_unpromoted(session.get('user_id'), user_to_demote.id)
        return redirect(request.referrer or url_for('posts.index'))
    else:
        flash("You cannot demote admin", "danger")
        return redirect(request.referrer or url_for('posts.index'))

@admin_bp.route('/ban/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def ban(user_id):
    user_to_ban=User.query.get_or_404(user_id)
    if user_to_ban.role == 'admin':
        flash("You cannot ban admin", "danger")
        return redirect(request.referrer or url_for('posts.index'))
    user_to_ban.set_banned()
    db.session.commit()
    log_user_banned(session.get('user_id'), user_to_ban.id)
    flash(f"User {user_to_ban.username} has been banned.", "success")
    return redirect(request.referrer or url_for('posts.index'))


@admin_bp.route('/unban/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def unban(user_id):
    user_to_unban=User.query.get_or_404(user_id)
    if user_to_unban.is_banned:
        user_to_unban.unset_banned()
        db.session.commit()
        log_user_unbanned(session.get('user_id'), user_to_unban.id)
    flash(f"User {user_to_unban.username} has been unbanned.", "success")
    return redirect(request.referrer or url_for('posts.index'))

@admin_bp.route('/mute/<int:user_id>', methods=['POST'])
@login_required
@moderator_required
def mute(user_id):
    user_to_mute=User.query.get_or_404(user_id)
    if user_to_mute.role in ('admin', 'moderator'):
        flash("You cannot mute admin", "danger")
        return redirect(request.referrer or url_for('posts.index'))
    user_to_mute.mute()
    db.session.commit()
    log_user_muted(session.get('user_id'), user_to_mute.id)
    return redirect(request.referrer or url_for('posts.index'))

@admin_bp.route('/unmute/<int:user_id>', methods=['POST'])
@login_required
@moderator_required
def unmute(user_id):
    user_to_unmute=User.query.get_or_404(user_id)
    user_to_unmute.unmute()
    db.session.commit()
    log_user_unmuted(session.get('user_id'), user_to_unmute.id)
    return redirect(request.referrer or url_for('posts.index'))

@admin_bp.route('/downloadlogs')
@login_required
@admin_required
def downloadlogs():
    buffer = export_logs()
    filename=f"log_export_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    return send_file(buffer,
                     as_attachment=True,
                     download_name=filename,
                     mimetype='text/plain')
