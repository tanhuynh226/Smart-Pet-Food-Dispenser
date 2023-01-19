import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
load_dotenv()

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

def dispenser_one_refill_notif(phone_number):
  message = client.messages.create(
    body='Dispenser 1 needs to be refilled!',
    from_='+15618213167',
    to=phone_number
  )

def dispenser_two_refill_notif(phone_number):
  message = client.messages.create(
    body='Dispenser 2 needs to be refilled!',
    from_='+15618213167',
    to=phone_number
  )

def dispensed_one_notif(phone_number):
  message = client.messages.create(
    body='Dispenser 1 has dispensed food!',
    from_='+15618213167',
    to=phone_number
  )

def dispensed_two_notif(phone_number):
  message = client.messages.create(
    body='Dispenser 2 has dispensed food!',
    from_='+15618213167',
    to=phone_number
  )

if __name__ == '__main__':
  # dispenser_one_refill_notif('+14086149226')
  # dispensed_one_notif('+14086149226')
  while True:
        try:
            phone_number = input('Enter your phone number with country code: ')
            phone_number = '+' + phone_number
            lookup = client.lookups.v1.phone_numbers(phone_number).fetch()
            break
        except TwilioRestException:
            print('Invalid phone number. Please try again.')
  print(lookup.phone_number)