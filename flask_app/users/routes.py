# 3rd-party packages
from flask import render_template, request, redirect, url_for, flash, Response, send_file, Blueprint
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
from flask_app import bcrypt, client, mongo_lock, session, messaging, client2
from flask_app.forms import (SearchForm, GameCommentForm, RegistrationForm, LoginForm,
                             UpdateUsernameForm, UpdateProfilePicForm)
from flask_app.models import User, Comment, load_user
from flask_app.utils import current_time

users = Blueprint("users", __name__)

@users.route('/user/<username>')
def user_detail(username):
    mongo_lock.acquire()
    user = User.objects(username=username).first()
    comments = Comment.objects(commenter=user)

    mongo_lock.release()

    return render_template('user_detail.html', username=username, comments=comments, client=client2)


""" ************ User Management views ************ """
@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        user = User(username=form.username.data, email=form.email.data, password=hashed)
        mongo_lock.acquire()
        user.save()
        mongo_lock.release()

        session['new_username'] = user.username
        return redirect(url_for('users.tfa'))

    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        mongo_lock.acquire()
        user = User.objects(username=form.username.data).first()
        mongo_lock.release()

        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('users.account'))
        else:
            flash('Login failed. Check your username and/or password')
            return redirect(url_for('users.login'))

    return render_template('login.html', title='Login', form=form)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for('users.account'))

    return render_template("account.html", title="Account", username_form=username_form, profile_pic_form=profile_pic_form)

@users.route("/tfa")
def tfa():
    if 'new_username' not in session:
        return redirect(url_for('main.home'))

    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return render_template('tfa.html'), headers

@users.route("/qr_code")
def qr_code():
    if 'new_username' not in session:
        return redirect(url_for('main.home'))

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