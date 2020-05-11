# 3rd-party packages
from flask import render_template, request, redirect, url_for, flash, Response, send_file
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from PIL import Image
import pyotp, qrcode
from qrcode.image import svg
# stdlib
from datetime import datetime
import io
import base64

# local
from . import app, bcrypt, client, mongo_lock, session
from .forms import (SearchForm, GameCommentForm, RegistrationForm, LoginForm,
                             UpdateUsernameForm, UpdateProfilePicForm)
from .models import User, Comment, load_user
from .utils import current_time
from . import messaging

""" ************ View functions ************ """
@app.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for('query_results', query=form.search_query.data))

    return render_template('home.html', form=form)

@app.route('/leagues')
def leagues():
    return render_template('leagues.html')

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/search-results/<query>', methods=['GET'])
def query_results(query):
    results = client.search(query)

    if type(results) == dict:
        return render_template('query.html', error_msg=results['Error'])
    
    return render_template('query.html', results=results)

@app.route('/games/<game_id>', methods=['GET', 'POST'])
def game_detail(game_id):
    result = client.retrieve_game_by_id(game_id)

    if type(result) == dict:
        return render_template('game_detail.html', error_msg=result['Error'])

    form = GameCommentForm()
    if form.validate_on_submit():
        comment = Comment(
            commenter=load_user(current_user.username), 
            content=form.text.data, 
            date=current_time(),
            imdb_id=movie_id,
            movie_title=result.title
        )

        mongo_lock.acquire()
        comment.save()
        mongo_lock.release()

        return redirect(request.path)

    mongo_lock.acquire()
    comments_m = Comment.objects(imdb_id=game_id)
    mongo_lock.release()

    comments = []
    for r in comments_m:
        comments.append({
            'date': r.date,
            'username': r.commenter.username,
            'content': r.content,
            'image': images(r.commenter.username)
        })


    return render_template('game_detail.html', form=form, movie=result, comments=comments)

@app.route('/project')
def project():
    return render_template('project.html')

@app.route('/user/<username>')
def user_detail(username):
    mongo_lock.acquire()
    user = User.objects(username=username).first()
    comments = Comment.objects(commenter=user)

    image = images(username)
    mongo_lock.release()

    return render_template('user_detail.html', username=username, comments=comments, image=image)

# @app.route('/images/<username>.png')
def images(username):
    mongo_lock.acquire()
    user = User.objects(username=username).first()
    mongo_lock.release()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image


""" ************ User Management views ************ """
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        user = User(username=form.username.data, email=form.email.data, password=hashed)
        mongo_lock.acquire()
        user.save()
        mongo_lock.release()

        session['new_username'] = user.username
        return redirect(url_for('tfa'))

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        mongo_lock.acquire()
        user = User.objects(username=form.username.data).first()
        mongo_lock.release()

        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('account'))
        else:
            flash('Login failed. Check your username and/or password')
            return redirect(url_for('login'))

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    username_form = UpdateUsernameForm()
    profile_pic_form = UpdateProfilePicForm()

    if username_form.validate_on_submit():
        # current_user.username = username_form.username.data
        mongo_lock.acquire()
        current_user.modify(username=username_form.username.data)
        current_user.save()
        mongo_lock.release()
        return redirect(url_for('account'))

    if profile_pic_form.validate_on_submit():
        img = profile_pic_form.propic.data
        filename = secure_filename(img.filename)

        if current_user.profile_pic.get() is None:
            current_user.profile_pic.put(img.stream, content_type='images/png')
        else:
            current_user.profile_pic.replace(img.stream, content_type='images/png')
        current_user.save()

        return redirect(url_for('account'))

    image = images(current_user.username)

    return render_template("account.html", title="Account", username_form=username_form, profile_pic_form=profile_pic_form, image=image)

@app.route("/tfa")
def tfa():
    if 'new_username' not in session:
        return redirect(url_for('home'))

    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return render_template('tfa.html'), headers

@app.route("/qr_code")
def qr_code():
    if 'new_username' not in session:
        return redirect(url_for('home'))

    user = User.objects(username=session['new_username']).first()
    session.pop('new_username')

    uri = pyotp.totp.TOTP(user.otp_secret).provisioning_uri(name=user.username, issuer_name='CMSC388J-2FA')
    img = qrcode.make(uri, image_factory=svg.SvgPathImage)
    stream = io.BytesIO()
    img.save(stream)

    headers = {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return stream.getvalue(), headers