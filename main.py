import os
import cv2
import numpy as np
import time
import boto3
import constant
import keyboard
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
GPIO.setmode(GPIO.BCM)

ultrasonic_pet_detect = UltrasonicRanger()
ultrasonic_dispenser_one = UltrasonicRanger()
ultrasonic_dispenser_two = UltrasonicRanger()
stepper_one = StepperMotor()
stepper_two = StepperMotor()

ultrasonic_pet_detect.setup(constant.ULTRASONIC_TRIGGER_PET, constant.ULTRASONIC_ECHO_PET)
ultrasonic_dispenser_one.setup(constant.ULTRASONIC_TRIGGER_DISPENSER_ONE, constant.ULTRASONIC_ECHO_DISPENSER_ONE)
ultrasonic_dispenser_two.setup(constant.ULTRASONIC_TRIGGER_DISPENSER_TWO, constant.ULTRASONIC_ECHO_DISPENSER_TWO)
stepper_one.setup(constant.STEPPER_CHANNEL_ONE)
stepper_two.setup(constant.STEPPER_CHANNEL_TWO)

client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

if __name__ == '__main__':
    # Stores owner's phone number
    while True:
        try:
            phone_number = input('Enter your phone number with country code: ')
            phone_number = '+' + phone_number
            lookup = client.lookups.v1.phone_numbers(phone_number).fetch()
            print('Phone number saved.')
            break
        except TwilioRestException:
            print('Invalid phone number. Please try again.')

    print('Beginning initial calibration...')

    # Stores distance without pet in front of the dispenser
    print('Place nothing in front of the ultrasonic ranger and press enter once you have done so.')
    dist_before_motion = store_distance_before_motion()
    print(dist_before_motion)
    print('Distance to floor saved.')

    # Delay so that "enter" key has time to reset
    time.sleep(0.1)

    # Assigns first pet type to dispenser 1
    print('Place your first pet in front of the camera and press enter once you have done so.')
    pet_one = store_pet()
    print('Pet one saved as ' + pet_one)

    # Assigns second pet type to dispenser 2
    print('Place your second pet in front of the camera and press enter once you have done so.')
    pet_two = store_pet()
    print('Pet two saved as ' + pet_two)

    try:
        while True:
            # Testing for "pet dispenser", if it is greater than constant REFILL_DISTANCE_THRESHOLD from top of dispenser
            if ultrasonic_dispenser_one.distance(constant.ULTRASONIC_TRIGGER_DISPENSER_ONE, constant.ULTRASONIC_ECHO_DISPENSER_ONE) > constant.REFILL_DISTANCE_THRESHOLD:
                dispenser_refill_notif('1', phone_number)
            elif ultrasonic_dispenser_two.distance(constant.ULTRASONIC_TRIGGER_DISPENSER_TWO, constant.ULTRASONIC_ECHO_DISPENSER_TWO) > constant.REFILL_DISTANCE_THRESHOLD:
                dispenser_refill_notif('2', phone_number)

            # Testing "motion detection" by comparing distance before and after motion
            dist_after_motion = ultrasonic_pet_detect.distance(constant.ULTRASONIC_TRIGGER_PET, constant.ULTRASONIC_ECHO_PET)
            #print('Measured distance = %.1f cm' % dist_after_motion)
            if (dist_before_motion - dist_after_motion) > constant.MOTION_DISTANCE_THRESHOLD:
                collect_frames()
                pet = detect_pet()
                mask_one = np.in1d(pet, pet_one)
                mask_two = np.in1d(pet, pet_two)
                for value in mask_one:
                    if value == True:
                        stepper_one.dispense(constant.STEPPER_CHANNEL_ONE, constant.TIME_TO_DISPENSE_PET_ONE)
                        dispensed_notif('1', phone_number)
                        break
                for value in mask_two:
                    if value == True:
                        stepper_two.dispense(constant.STEPPER_CHANNEL_TWO, constant.TIME_TO_DISPENSE_PET_TWO)
                        dispensed_notif('2', phone_number)
                        break
            
            time.sleep(.5) 
            
    except KeyboardInterrupt:
        print('Stopped_________')
        release_camera()
        GPIO.cleanup()