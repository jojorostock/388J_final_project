from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
import pyotp

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    profile_pic = db.ImageField()
    otp_secret = db.StringField(required=True, min_length=16, max_length=16, default=pyotp.random_base32())

    # Returns unique string identifying our object
    def get_id(self):
        return self.username

class Comment(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    game_id = db.StringField(required=True, min_length=9, max_length=9)


