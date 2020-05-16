from twilio.rest import Client
import os
from threading import Timer
from threading import Lock
from . import mongo_lock, sport_client, utils
from flask_app.models import User
from flask_login import current_user

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_send_number = '+12057821165'
twilio_timer_interval = 3.0

twilio_client = Client(account_sid, auth_token)

def send_message(message, recipient):
	message = twilio_client.messages.create(body=message, from_=twilio_send_number, to=recipient)

def send_scheduled_messages():
	mongo_lock.acquire()
	for user in User.objects():
		for subscription in user.game_subscriptions:
			game = sport_client.getEventByID(subscription)
			print(game.dateEventLocal)
			if game.dateEventLocal is not None:
				game_date = utils.extract_date_tuple(game.dateEventLocal)
				curr_date = utils.current_date_tuple()

			if game_date <= curr_date or game.dateEventLocal is None:
				send_message(game.getEventDescription(True), user.phone_number)
				new_subscriptions = user.game_subscriptions
				new_subscriptions.remove(int(subscription))
				user.modify(game_subscriptions=new_subscriptions)

	mongo_lock.release()

	# reschedule the timer
	Timer(twilio_timer_interval, send_scheduled_messages).start()
