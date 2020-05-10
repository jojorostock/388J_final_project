from twilio.rest import Client
import os

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_send_number = '+12057821165'

twilio_client = Client(account_sid, auth_token)

def send_message(message, recipient):
	message = twilio_client.messages.create(body=message, from_=twilio_send_number, to=recipient)
