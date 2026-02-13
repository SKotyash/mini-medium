from flask import request, render_template, session, Blueprint, redirect, url_for, abort, flash


from services import *
from decorators import login_required
from models import User, db, Post, Like, Comment, Follow
from services.audit_log import log_post_deleted

posts_bp = Blueprint('posts', __name__, template_folder='templates')


@posts_bp.route('/')
@posts_bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    pagination=(Post.query.filter_by(status="published")
                .order_by(Post.created_at.desc())
                .paginate(page=page, per_page=10,error_out=False))
    posts = pagination.items
    return render_template('index.html',pagination=pagination, posts=posts)


@posts_bp.route('/myaccount')
@login_required
def myaccount():
    posts = Post.query.filter_by(author_id=session['user_id']).all()
    user=User.query.filter_by(id=session['user_id']).first()
    return render_template('myaccount.html', posts=posts,user=user)


@posts_bp.route('/create-post', methods=['POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author_id = session['user_id']
        post = Post(title=title, author_id=author_id, content=content)

        try:
            db.session.add(post)
            db.session.commit()
            add_post_notifications(post)
            return redirect(url_for('posts.myaccount'))
        except Exception as e:
            print(e)
            return render_template('myaccount.html', error="Something went wrong when creating post.")

    return redirect(url_for('posts.myaccount'))


@posts_bp.route('/delete-post/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    if request.method == 'POST':
        post_to_delete = Post.query.get_or_404(post_id)
        current_user_id = session['user_id']
        current_role = session['role']
        if not (post_to_delete.author_id == current_user_id or current_role in ['admin', 'moderator']):
            abort(403)
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            log_post_deleted(current_user_id,post_to_delete.id)
            return redirect(url_for('posts.myaccount'))
        except Exception as e:
            print(e)
            return render_template('myaccount.html', error="Something went wrong when deleting post.")


@posts_bp.route('/publish/<post_id>', methods=['POST'])
@login_required
def publish_post(post_id):
    if request.method == 'POST':
        user=User.query.get_or_404(session['user_id'])
        mute_status = get_mute_status(user)
        if mute_status:
            flash(f'You are muted try in {mute_status['hours']} hours {mute_status['minutes']} minutes.', 'danger')
            return redirect(url_for('posts.myaccount'))
        post_to_send_on_review = Post.query.get_or_404(post_id)
        if post_to_send_on_review.author_id != session['user_id']:
            abort(403)
        if post_to_send_on_review:
            post_to_send_on_review.send_on_review()
            db.session.commit()
            return redirect(url_for('posts.myaccount'))


@posts_bp.route('/edit-post/<post_id>', methods=['POST'])
@login_required
def edit_post(post_id):
    if request.method == 'POST':
        post_to_edit = Post.query.get_or_404(post_id)
        if post_to_edit.author_id != session['user_id']:
            abort(403)
        if post_to_edit:
            title = request.form['title']
            content = request.form['content']
            Post.edit_post(post_to_edit, title, content)
            db.session.commit()
            return redirect(url_for('posts.myaccount'))


@posts_bp.route('/like-post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    post = Post.query.get_or_404(post_id)

    like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()

    if like:
        db.session.delete(like)
        remove_like_notification(user, post)
    else:
        new_like = Like(post_id=post_id, user_id=user_id)
        db.session.add(new_like)
        add_like_notification(user, post)


    db.session.commit()
    target = request.referrer or url_for('posts.index')
    return redirect(f"{target}#readMoreModal{post_id}")


@posts_bp.route('/search')
def search():
    query = request.args.get('q', "")
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(Post.title.ilike(f"%{query}%")).filter_by(status="published").paginate(page=page, per_page=5,error_out=False)
    posts = pagination.items
    results_users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    current_user_id = session.get('user_id')
    if current_user_id:
        followed_users = Follow.query.filter_by(follower_id=current_user_id).all()
        followed_ids = [f.followed_id for f in followed_users]
    else:
        followed_ids = []
    return render_template('search.html',
                           users=results_users,
                           posts=posts,
                           query=query,
                           followed_ids=followed_ids,
                           pagination=pagination)





@posts_bp.route('/feed')
@login_required
def feed():
    user_id=session['user_id']
    followed_users = [f.followed_id for f in Follow.query.filter_by(follower_id=user_id).all()]
    page = request.args.get('page', 1, type=int)
    pagination=(Post.query
              .filter_by(status="published")
              .filter(Post.author_id.in_(followed_users))
              .order_by(Post.updated_at.desc())
              .paginate(page=page, per_page=5,error_out=False))
    posts = pagination.items
    return render_template('feed.html',posts=posts,pagination=pagination)


