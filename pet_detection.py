import os
import cv2
import time
import boto3
import constant
import keyboard
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from notifications import *
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

rek_client = boto3.client('rekognition')

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

def collect_frames():
    capture = cv2.VideoCapture(0)
    img_counter = 0
    start_time = time.time()

    while True:
        ret, frame = capture.read()
        if img_counter == 5:
            break
        if time.time() - start_time >= 1: # Check if 1 sec passed
            img_name = 'frames/frame_{}.png'.format(img_counter)
            cv2.imwrite(img_name, frame)
            print('{} written!'.format(img_counter))
            start_time = time.time()
        img_counter += 1
    
    capture.release()

def detect_pet():
    img_counter = 0

    while True:
        if img_counter == 5:
            break

        with open('frames/frame_{}.png'.format(img_counter), 'rb') as image:
            response = rek_client.detect_labels(Image={'Bytes': image.read()})

        labels = response['Labels']
        print(f'Found {len(labels)} labels in the image:')
        for label in labels:
            if label['Name'] == 'Dog':
                confidence = label['Confidence']
                pet = detect_dog_breed(image)
                break
            elif label['Name'] == 'Cat':
                confidence = label['Confidence']
                pet = 'Cat'
                break
        img_counter += 1
    
    return pet

def store_pet():
    while True:
        if keyboard.is_pressed('enter'):
            collect_frames()
            pet = detect_pet()
            return pet

def detect_dog_breed(photo):
    model='arn:aws:rekognition:us-west-2:490776989874:project/dog_breeds/version/dog_breeds.2022-10-16T17.38.46/1665967125295'
    min_confidence=60

    with open(photo, 'rb') as image:
        response = rek_client.detect_custom_labels(Image={'Bytes': image.read()},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    labels = response['CustomLabels']
    if labels:
        return labels[0]['Name']
    else:
        return None

if __name__ == '__main__':
    # Stores owner's phone number
    while True:
        try:
            phone_number = input('Enter your phone number with country code: ')
            phone_number = '+' + phone_number
            lookup = client.lookups.v1.phone_numbers(phone_number).fetch()
            break
        except TwilioRestException:
            print('Invalid phone number. Please try again.')

    # Stores distance without pet in front of the dispenser
    print('Place nothing in front of the camera and press enter once you have done so.')
    while True:
        if keyboard.is_pressed('enter'):
            dist_before_motion = ultrasonic_pet_detect.distance(constant.ULTRASONIC_TRIGGER_PET, constant.ULTRASONIC_ECHO_PET)
            #print('Measured distance = %.1f cm' % dist_before_motion)
            print('Distance to floor saved.')
            break

    # Assigns first pet type to dispenser 1
    print('Place your first pet in front of the camera and press enter once you have done so.')
    pet_one = store_pet()
    print('Pet one saved')

    # Assigns second pet type to dispenser 2
    print('Place your second pet in front of the camera and press enter once you have done so.')
    pet_two = store_pet()
    print('Pet two saved')

    try:
        while True:
            # Testing "motion detection" by comparing distance before and after motion
            dist_after_motion = ultrasonic_pet_detect.distance(constant.ULTRASONIC_TRIGGER_PET, constant.ULTRASONIC_ECHO_PET)
            #print('Measured distance = %.1f cm' % dist_after_motion)
            if (dist_before_motion - dist_after_motion) > constant.MOTION_DISTANCE_THRESHOLD:
                collect_frames()
                pet = detect_pet()
                if pet == pet_one:
                    stepper_one.dispense(constant.TIME_TO_DISPENSE_PET_ONE)
                    dispensed_one_notif(phone_number)
                elif pet == pet_two: 
                    stepper_two.dispense(constant.TIME_TO_DISPENSE_PET_TWO)
                    dispensed_two_notif(phone_number)
            
            # Testing for "pet dispenser", if it is greater than constant REFILL_DISTANCE_THRESHOLD from top of dispenser
            if ultrasonic_dispenser_one.distance(constant.ULTRASONIC_TRIGGER_DISPENSER_ONE, constant.ULTRASONIC_ECHO_DISPENSER_ONE) > constant.REFILL_DISTANCE_THRESHOLD:
                dispenser_one_refill_notif(phone_number)
            elif ultrasonic_dispenser_two.distance(constant.ULTRASONIC_TRIGGER_DISPENSER_TWO, constant.ULTRASONIC_ECHO_DISPENSER_TWO) > constant.REFILL_DISTANCE_THRESHOLD:
                dispenser_one_refill_notif(phone_number)
            time.sleep(.5) 
            
    except KeyboardInterrupt:
        print('Stopped_________')
        GPIO.cleanup()

