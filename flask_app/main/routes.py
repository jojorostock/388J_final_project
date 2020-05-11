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
from flask_app import bcrypt, client, mongo_lock, session, messaging
from flask_app.forms import (SearchForm, GameCommentForm, RegistrationForm, LoginForm,
                             UpdateUsernameForm, UpdateProfilePicForm)
from flask_app.models import User, Comment, load_user
from flask_app.utils import current_time

main = Blueprint("main", __name__)

@main.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for('main.query_results', query=form.search_query.data))

    return render_template('home.html', form=form)

@main.route('/leagues')
def leagues():
    return render_template('leagues.html')

@main.route('/events')
def events():
    return render_template('events.html')

@main.route('/search-results/<query>', methods=['GET'])
def query_results(query):
    results = client.search(query)

    if type(results) == dict:
        return render_template('query.html', error_msg=results['Error'])
    
    return render_template('query.html', results=results)

@main.route('/games/<game_id>', methods=['GET', 'POST'])
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

@main.route('/project')
def project():
    return render_template('project.html')

# @main.route('/images/<username>.png')
def images(username):
    mongo_lock.acquire()
    user = User.objects(username=username).first()
    mongo_lock.release()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image