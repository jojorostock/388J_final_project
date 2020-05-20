from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import (InputRequired, DataRequired, NumberRange, Length, Email, 
                                EqualTo, ValidationError)
import pyotp

from flask_app.models import User
from flask_app import messaging
from twilio.base.exceptions import TwilioRestException

class SearchForm(FlaskForm):
    search_query = StringField('Query', validators=[InputRequired(), Length(min=1, max=100)])
    submit = SubmitField('Search')

class GameCommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[InputRequired(), Length(min=5, max=500)])
    submit = SubmitField('Enter Comment')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=1, max=40)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    phone = IntegerField('Phone Number', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_phone(self, phone):
        if type(phone.data) is not int:
            raise ValidationError('Phone number must not contain non-numeric characters')
        first_digit = int(phone.data / 10000000000)
        print('first_digit: ' + str(first_digit))
        if (first_digit < 1 or first_digit > 9):
            raise ValidationError('Phone number must 11 digits. Make sure to include country code and area code.')

        try:
            message = messaging.twilio_client.messages.create(to='+' + str(phone.data), from_=messaging.twilio_send_number,
                                   body="You have successfully registered your phone number!")
        except TwilioRestException as e:
            raise ValidationError(e.msg + ' Make sure that the phone number has been registered as a verified number with the Twilio trial account.')

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is taken')

    def validate_email(self, email):        
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError('Email is taken')

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")
    token = StringField('2FA Token', validators=[InputRequired(), Length(min=6, max=6)])

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is None:
            raise ValidationError("That username does not exist in our database.")

    def validate_token(self, token):
        user = User.objects(username=self.username.data).first()
        if user is not None:
            tok_verified = pyotp.TOTP(user.otp_secret).verify(token.data)
            if not tok_verified:
                raise ValidationError("Invalid Token")

class UpdateUsernameForm(FlaskForm):
    username = StringField('Change Username', validators=[InputRequired(), Length(min=1, max=40)])
    submit = SubmitField('Update Username')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")

class NotificationSubscriptionForm(FlaskForm):
    submit = SubmitField('Subscribe')

class NotificationUnsubscriptionForm(FlaskForm):
    submit = SubmitField('Unsubscribe')

