from twilio.rest import Client
import os
from threading import Timer
from threading import Lock
from . import mongo_lock

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_send_number = '+12057821165'
twilio_timer_interval = 60.0

twilio_client = Client(account_sid, auth_token)

def send_message(message, recipient):
	message = twilio_client.messages.create(body=message, from_=twilio_send_number, to=recipient)

def send_scheduled_messages():
	mongo_lock.acquire()
	# todo: check mongo for current notifications, call send_message() for every one,
	# and update mongo to show that the message has been sent
	mongo_lock.release()

	# reschedule the timer
	Timer(twilio_timer_interval, send_scheduled_messages).start()
