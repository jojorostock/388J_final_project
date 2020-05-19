# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# stdlib
import os
import requests
from threading import Timer, Lock
from datetime import datetime

# local
from .client import SportClient

# Talisman
from flask_talisman import Talisman


# lock to ensure synchronization of mongodb access
mongo_lock = Lock()

app = Flask(__name__)
# app.config['MONGODB_HOST'] = 'mongodb://localhost:27017/sport_database'
app.config['MONGODB_HOST'] = 'mongodb://heroku_19g2tpxk:s6eiqvrsbqkemi9537gmlbk7qo@ds133104.mlab.com:33104/heroku_19g2tpxk?retryWrites=false'
app.config['SECRET_KEY'] = b'\x020;yr\x91\x11\xbe"\x9d\xc1\x14\x91\xadf\xec'

# Talisman

csp = {
    'default-src': '\'self\'',
    'img-src': '*',
    'style-src': [
        'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css',
        'http://127.0.0.1:5000/static/custom.css',
        'https://cmsc388j-final-project.herokuapp.com/static/custom.css'
    ],
    'script-src': [
        'https://code.jquery.com/jquery-3.4.1.slim.min.js',
        'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js',
        'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js'
    ]
}

Talisman(app, content_security_policy=csp)

# mongo = PyMongo(app)
db = MongoEngine(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
bcrypt = Bcrypt(app)

# Dummy User Data
from flask_app.models import User, Comment, load_user

# Chiefs Fan
hashed = bcrypt.generate_password_hash("password").decode("utf-8")
user = User(username='chiefsFan1234', email="chiefsFan1234@yahoo.com", phone_number='+14109919959', password=hashed)
userTest = User.objects(username=user.username).first()
if userTest is None:
    mongo_lock.acquire()
    user.save()
    mongo_lock.release()

    comment = Comment(
                commenter=load_user(user.username), 
                content='Great Game!!!!!!!!!',
                date='2020-03-09',
                game_id='673964',
            )

    mongo_lock.acquire()
    comment.save()
    mongo_lock.release()

    comment = Comment(
                commenter=load_user(user.username), 
                content='Super bowl is next 49ers going down',
                date='2020-03-09',
                game_id='673726',
            )

    mongo_lock.acquire()
    comment.save()
    mongo_lock.release()

# Niners Fan

hashed = bcrypt.generate_password_hash("password2").decode("utf-8")
user = User(username='ninersForever', email="ninersForever@yahoo.com", phone_number='+14104434793', password=hashed)
userTest = User.objects(username=user.username).first()
if userTest is None:
    mongo_lock.acquire()
    user.save()
    mongo_lock.release()

    comment = Comment(
                commenter=load_user(user.username), 
                content='This is the worst Jimmy G needs to go',
                date='2020-03-09',
                game_id='673964',
            )

    mongo_lock.acquire()
    comment.save()
    mongo_lock.release()

    comment = Comment(
                commenter=load_user(user.username), 
                content='You wish @chiefsFan1234',
                date='2020-03-09',
                game_id='673726',
            )

    mongo_lock.acquire()
    comment.save()
    mongo_lock.release()


# The Herminator

hashed = bcrypt.generate_password_hash("giraffe").decode("utf-8")
user = User(username='larryHerman', email="iLoveGiraffes@yahoo.com", phone_number='+14109912315', password=hashed)
userTest = User.objects(username=user.username).first()
if userTest is None:
    mongo_lock.acquire()
    user.save()
    mongo_lock.release()

    comment = Comment(
                commenter=load_user(user.username), 
                content='This was a fun game but next time I would like to sit in a closer row',
                date='2020-04-10',
                game_id='673964',
            )

    mongo_lock.acquire()
    comment.save()
    mongo_lock.release()

    comment = Comment(
                commenter=load_user(user.username), 
                content='What is a steeler they should be the Pittsburgh Giraffes',
                date='2020-04-10',
                game_id='673825',
            )

    mongo_lock.acquire()
    comment.save()
    mongo_lock.release()

# Perkins

hashed = bcrypt.generate_password_hash("vens").decode("utf-8")
user = User(username='pickNerkins', email="perks@yahoo.com", phone_number='+14432232086', password=hashed)
userTest = User.objects(username=user.username).first()
if userTest is None:
    mongo_lock.acquire()
    user.save()
    mongo_lock.release()

    comment = Comment(
                commenter=load_user(user.username), 
                content='Lamar still the MVP we will win it next year',
                date='2020-04-10',
                game_id='673723',
            )

    mongo_lock.acquire()
    comment.save()
    mongo_lock.release()


sport_client = SportClient("1")

from . import messaging
# start messaging timer
Timer(messaging.twilio_timer_interval, messaging.send_scheduled_messages).start()

session = {}

from flask_app.main.routes import main
from flask_app.users.routes import users

app.register_blueprint(main)
app.register_blueprint(users)