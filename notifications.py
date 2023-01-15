import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

def refillNotif():
  message = client.messages.create(
    body="Dispenser needs to be refilled!",
    from_="+15618213167",
    to="+14086149226"
  )

def dispensedNotif():
  message = client.messages.create(
    body="Food has been dispensed!",
    from_="+15618213167",
    to="+14086149226"
  )

if __name__ == '__main__':
  refillNotif()
  dispensedNotif()