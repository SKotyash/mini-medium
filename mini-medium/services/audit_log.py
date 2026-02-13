import io
from datetime import datetime

from flask import has_request_context

from models import Logs, db


def log_user_banned(admin_id,user_id):
    log_type="USER_BANNED"
    sender_id=admin_id
    target_id=user_id
    message=f"admin {admin_id} has banned {user_id}"
    log_constructor(log_type,sender_id,target_id,message)

def log_user_unbanned(admin_id,user_id):
    log_type = "USER_UNBANNED"
    sender_id = admin_id
    target_id = user_id
    message = f"admin {admin_id} unbanned {user_id}"
    log_constructor(log_type, sender_id, target_id, message)

def log_user_muted(admin_id,user_id):
    log_type = "USER_MUTED"
    sender_id = admin_id
    target_id = user_id
    message = f"admin {admin_id} has muted {user_id}"
    log_constructor(log_type, sender_id, target_id, message)

def log_user_unmuted(admin_id,user_id):
    log_type = "USER_UNMUTED"
    sender_id = admin_id if has_request_context() else 3
    target_id = user_id
    message = f"admin {admin_id} has muted {user_id}"
    log_constructor(log_type, sender_id, target_id, message)

def log_post_deleted(user_id,post_id):
    log_type = "POST_DELETED"
    sender_id = user_id
    target_id = post_id
    message = f"admin {user_id} has deleted {post_id}"
    log_constructor(log_type, sender_id, target_id, message)

def log_post_approved(admin_id,post_id):
    log_type = "POST_APPROVED"
    sender_id = admin_id
    target_id = post_id
    message = f"admin {admin_id} has approved {post_id}"
    log_constructor(log_type, sender_id, target_id, message)

def log_post_rejected(admin_id,post_id):
    log_type = "POST_REJECTED"
    sender_id = admin_id
    target_id = post_id
    message = f"admin {admin_id} has approved {post_id}"
    log_constructor(log_type, sender_id, target_id, message)

def log_moderator_promoted(admin_id,user_id):
    log_type = "MODERATOR_PROMOTED"
    sender_id = admin_id
    target_id = user_id
    message = f"admin {admin_id} give role \"Moderator\" to {user_id}"
    log_constructor(log_type, sender_id, target_id, message)

def log_moderator_unpromoted(admin_id,user_id):
    log_type = "MODERATOR_DEMOTED"
    sender_id = admin_id
    target_id = user_id
    message=f"admin {admin_id} cancel role \"Moderator\" to {user_id}"
    log_constructor(log_type, sender_id, target_id, message)


def log_constructor(log_type,sender_id,target_id,message):
    new_log=Logs(type=log_type,
                 sender_id=sender_id,
                 target_id=target_id,
                 message=message,
                 created_at=datetime.now())
    db.session.add(new_log)
    db.session.commit()


def export_logs():
    logs = Logs.query.order_by(Logs.created_at).all()
    proxy=io.StringIO()
    for log in logs:

        proxy.write(f"{log.message} {log.created_at.strftime('%Y-%m-%d_%H:%M:%S')} {log.type}\n")
    mem = io.BytesIO()
    mem.write(proxy.getvalue().encode('utf-8'))
    mem.seek(0)
    proxy.close()
    return mem