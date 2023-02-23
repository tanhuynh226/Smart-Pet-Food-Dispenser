import os
import numpy as np
import time
import constant
import threading
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from notifications import *
from pet_detection import *
import RPi.GPIO as GPIO
from ultrasonic_class import UltrasonicRanger
from stepper_class import StepperMotor
from dotenv import load_dotenv

load_dotenv()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

ultrasonic_pet_detect = UltrasonicRanger()
ultrasonic_dispenser_one = UltrasonicRanger()
ultrasonic_dispenser_two = UltrasonicRanger()
stepper_one = StepperMotor()
stepper_two = StepperMotor()

ultrasonic_pet_detect.setup(constant.ULTRASONIC_TRIGGER_PET, constant.ULTRASONIC_ECHO_PET)
ultrasonic_dispenser_one.setup(constant.ULTRASONIC_TRIGGER_DISPENSER_ONE, constant.ULTRASONIC_ECHO_DISPENSER_ONE)
ultrasonic_dispenser_two.setup(constant.ULTRASONIC_TRIGGER_DISPENSER_TWO, constant.ULTRASONIC_ECHO_DISPENSER_TWO)
stepper_one.setup(constant.STEPPER_ONE_DIR, constant.STEPPER_ONE_STEP)
stepper_two.setup(constant.STEPPER_TWO_DIR, constant.STEPPER_TWO_STEP)

client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

global_pet = []
pet_one_fed_status = False
pet_two_fed_status = False

def dispenser_one(pet_one, dispenses_per_day, amount_dispensed, increments):
    global global_pet, pet_one_fed_status
    while True:
        pet_one_fed_status = False
        #print('Measured distance = %.1f cm' % dist_after_motion)
        mask_one = np.in1d(global_pet, pet_one)
        for value in mask_one:
            if value == True:
                print('Dispenser 1 pet match confirm')
                i = 0
                while i < increments:
                    stepper_one.dispense(constant.STEPPER_ONE_STEP, amount_dispensed/increments)
                    time.sleep(5)
                    i += 1
                pet_one_fed_status = True
                dispensed_notif('1', phone_number)
                # Testing for "pet dispenser", if it is greater than constant REFILL_DISTANCE_THRESHOLD from top of dispenser
                if ultrasonic_dispenser_one.distance(constant.ULTRASONIC_TRIGGER_DISPENSER_ONE, constant.ULTRASONIC_ECHO_DISPENSER_ONE) > constant.REFILL_DISTANCE_THRESHOLD:
                    dispenser_refill_notif('1', phone_number)
                global_pet = []
                time.sleep(86400 / dispenses_per_day)
                break
        
        time.sleep(.5)

def dispenser_two(pet_two, dispenses_per_day, amount_dispensed, increments):
    global global_pet, pet_two_fed_status
    while True:
        pet_two_fed_status = False
        #print('Measured distance = %.1f cm' % dist_after_motion)
        mask_two = np.in1d(global_pet, pet_two)
        for value in mask_two:
            if value == True:
                print('Dispenser 2 pet match confirm')
                i = 0
                while i < increments:
                    stepper_two.dispense(constant.STEPPER_TWO_STEP, amount_dispensed/increments)
                    time.sleep(5)
                    i += 1
                pet_two_fed_status = True
                dispensed_notif('2', phone_number)
                # Testing for "pet dispenser", if it is greater than constant REFILL_DISTANCE_THRESHOLD from top of dispenser
                if ultrasonic_dispenser_two.distance(constant.ULTRASONIC_TRIGGER_DISPENSER_TWO, constant.ULTRASONIC_ECHO_DISPENSER_TWO) > constant.REFILL_DISTANCE_THRESHOLD:
                    dispenser_refill_notif('2', phone_number)
                global_pet = []
                time.sleep(86400 / dispenses_per_day)
                break
        
        time.sleep(.5)

def motion_detected(dist_before_motion):
    global global_pet, pet_one_fed_status, pet_two_fed_status
    while True:
        print('Checking if motion is detected')
        dist_after_motion = ultrasonic_pet_detect.distance(constant.ULTRASONIC_TRIGGER_PET, constant.ULTRASONIC_ECHO_PET)
        if ((dist_before_motion - dist_after_motion) > constant.MOTION_DISTANCE_THRESHOLD) and (pet_one_fed_status == False or pet_two_fed_status == False):
            collect_frames()
            global_pet = detect_pet()
            print('Sleeping after motion detection...')
            time.sleep(5)

if __name__ == '__main__':
    try: 
        # Stores owner's phone number
        while True:
            try:
#                 phone_number = input('Enter your phone number with country code: ')
                phone_number = str(14086149226)
                phone_number = '+' + phone_number
                lookup = client.lookups.v1.phone_numbers(phone_number).fetch()
                print('Phone number saved.')
                break
            except TwilioRestException:
                print('Invalid phone number. Please try again.')

        print('Beginning initial calibration...')

        # Stores distance without pet in front of the dispenser
        print('Place nothing in front of the ultrasonic ranger and press enter once you have done so.')
        dist_before_motion = get_distance_before_motion()
        print(dist_before_motion)
        print('Distance to floor saved.')

        # Delay so that "enter" key has time to reset
        time.sleep(0.1)

        # Assigns first pet type to dispenser 1
        print('Place your first pet in front of the camera and press enter once you have done so.')
        pet_one = store_pet()
        print('Pet one saved as ', pet_one)
#         pet_one_dispenses_per_day = int(input('Enter how many times per day to dispense food for this pet: '))
#         pet_one_amount_dispensed = float(input('Enter how much food to dispense for this pet: '))
        pet_one_dispenses_per_day = 1
        pet_one_amount_dispensed = 5
        pet_one_increments = 1

        # Assigns second pet type to dispenser 2
        print('Place your second pet in front of the camera and press enter once you have done so.')
        pet_two = store_pet()
        print('Pet two saved as ', pet_two)
#         pet_two_dispenses_per_day = int(input('Enter how many times per day to dispense food for this pet: '))
#         pet_two_amount_dispensed = float(input('Enter how much food to dispense for this pet: '))
        pet_two_dispenses_per_day = 1
        pet_two_amount_dispensed = 5
        pet_two_increments = 1

        motion = threading.Thread(target=motion_detected, args=(dist_before_motion, ))
        d1 = threading.Thread(target=dispenser_one, args=(pet_one, pet_one_dispenses_per_day, pet_one_amount_dispensed, pet_one_increments, ))
        d2 = threading.Thread(target=dispenser_two, args=(pet_two, pet_two_dispenses_per_day, pet_two_amount_dispensed, pet_two_increments, ))

        motion.daemon = True
        d1.daemon = True
        d2.daemon = True

        motion.start()
        d1.start()
        d2.start()
        
        motion.join()
        d1.join()
        d2.join()

    except KeyboardInterrupt:
        print('Exiting program...')
        release_camera()
        GPIO.cleanup()
