import flask
from flask import request, render_template, session, Blueprint, redirect, url_for, flash

from models import User, db, Post, Follow
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, template_folder='templates')


@auth_bp.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None:
            return redirect(url_for('posts.index', _anchor='loginModal', error='User not found'))
        if not check_password_hash(user.password_hash, password):
            return redirect(url_for('posts.index', _anchor='loginModal', error='Password incorrect'))
        if user.is_banned:
            return redirect(url_for('posts.index', _anchor='loginModal', error='User is banned'))
        session['user_id'] = user.id
        session['role'] = user.role
        session['username'] = user.username
        return redirect(url_for('posts.index'))


@auth_bp.route('/register', methods=['POST'])
def register():
    from services.user import is_valid
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        if not is_valid(email):
            return redirect(url_for('posts.index', _anchor="registerModal", error="Email address invalid"))
        password = request.form['password']
        role = "user"
        user = User(username=username, password_hash=generate_password_hash(password), email=email, role=role)
        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username
            return redirect(url_for('posts.index'))
        except Exception as e:
            print(e)
            return redirect(url_for('posts.index', _anchor="registerModal", error="Username already exists"))


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.clear()
    return redirect(url_for('posts.index'))


@auth_bp.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    current_user_id = session.get('user_id')
    is_following = False
    if current_user_id:
        is_following = (Follow.query.filter_by(follower_id=current_user_id,
                                               followed_id=user_id)
                        .first() is not None)
    page = request.args.get('page', 1, type=int)
    pagination = (Post.query
                  .filter_by(author_id=user_id, status="published")
                  .order_by(Post.created_at.desc())
                  .paginate(page=page, per_page=5, error_out=False))
    posts = pagination.items
    return render_template('profile.html', user=user, posts=posts, is_following=is_following, pagination=pagination)

@auth_bp.route('/update_settings', methods=['POST'])
def update_settings():
    if request.method=='POST':

        from services.user import update_user_settings
        username=request.form['username']
        email=request.form['email']
        new_password=request.form['new_password']
        current_password=request.form['current_password']
        user_id=session.get('user_id')
        print(user_id)
        success, message = update_user_settings(user_id, username, email, new_password, current_password)

        if success:
            session['username'] = username
            flask.flash(message, 'success')
        else:
            flask.flash(message, 'danger')

        return redirect(url_for('posts.myaccount'))