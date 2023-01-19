import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv

load_dotenv()

client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

def dispenser_refill_notif(dispenser_number, phone_number):
  message = client.messages.create(
    body='Dispenser ' + dispenser_number + ' needs to be refilled!',
    from_='+15618213167',
    to=phone_number
  )

def dispensed_notif(dispenser_number, phone_number):
  message = client.messages.create(
    body='Dispenser ' + dispenser_number + ' has dispensed food!',
    from_='+15618213167',
    to=phone_number
  )

if __name__ == '__main__':
  dispenser_refill_notif('1', '+14086149226')
  dispensed_notif('2', '+14086149226')
  # while True:
  #       try:
  #           phone_number = input('Enter your phone number with country code: ')
  #           phone_number = '+' + phone_number
  #           lookup = client.lookups.v1.phone_numbers(phone_number).fetch()
  #           break
  #       except TwilioRestException:
  #           print('Invalid phone number. Please try again.')
  # print(lookup.phone_number)