from flask import Blueprint, request, session, render_template, redirect, url_for

from models import Notification, db

notes_bp= Blueprint('notes', __name__)

@notes_bp.route('/mark_read',methods=['POST'])
def mark_read():
    user_id=session.get('user_id')
    if request.method=='POST':
        Notification.query.filter_by(user_id=user_id, is_read=False).update({Notification.is_read: True})
        db.session.commit()

        return redirect(request.referrer or url_for('posts.index'))


@notes_bp.route('/mark_single_read/<noteId>',methods=['POST'])
def mark_single_read(noteId):
    user_id=session.get('user_id')
    if request.method=='POST':
        Notification.query.filter_by(id=noteId,user_id=user_id, is_read=False).update({Notification.is_read: True})
        db.session.commit()
        return '', 204


