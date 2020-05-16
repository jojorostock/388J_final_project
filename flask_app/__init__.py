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

# lock to ensure synchronization of mongodb access
mongo_lock = Lock()

app = Flask(__name__)
app.config['MONGODB_HOST'] = 'mongodb://localhost:27017/sport_database'
app.config['SECRET_KEY'] = b'\x020;yr\x91\x11\xbe"\x9d\xc1\x14\x91\xadf\xec'

# mongo = PyMongo(app)
db = MongoEngine(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
bcrypt = Bcrypt(app)

sport_client = SportClient("1")

from . import messaging
# start messaging timer
Timer(messaging.twilio_timer_interval, messaging.send_scheduled_messages).start()

session = {}

from flask_app.main.routes import main
from flask_app.users.routes import users

app.register_blueprint(main)
app.register_blueprint(users)