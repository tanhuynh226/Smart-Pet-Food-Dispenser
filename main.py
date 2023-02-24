import os
import numpy as np
import time
import constant
import threading
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import pymysql
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
pet_one = []
pet_two = []
pet_one_fed_status = False
pet_two_fed_status = False
phone_number = int()
dist_before_motion = float()
pet_one_dispenses_per_day = int()
pet_one_amount_dispensed = int()
pet_one_increments = int()
pet_one_time_between_increments = int()
pet_two_dispenses_per_day = int()
pet_two_amount_dispensed = int()
pet_two_increments = int()
pet_two_time_between_increments = int()


def dispenser_one(pet_one, dispenses_per_day, amount_dispensed, increments, time_between_increments):
    global global_pet, pet_one_fed_status
    while True:
        pet_one_fed_status = False
        mask_one = np.in1d(global_pet, pet_one)
        for value in mask_one:
            if value == True:
                print('Dispenser 1 pet match confirm')
                i = 0
                while i < increments:
                    stepper_one.dispense(constant.STEPPER_ONE_STEP, amount_dispensed/increments)
                    time.sleep(time_between_increments)
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

def dispenser_two(pet_two, dispenses_per_day, amount_dispensed, increments, time_between_increments):
    global global_pet, pet_two_fed_status
    while True:
        pet_two_fed_status = False
        mask_two = np.in1d(global_pet, pet_two)
        for value in mask_two:
            if value == True:
                print('Dispenser 2 pet match confirm')
                i = 0
                while i < increments:
                    stepper_two.dispense(constant.STEPPER_TWO_STEP, amount_dispensed/increments)
                    time.sleep(time_between_increments)
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

def sql_listener(cur):
    global phone_number, pet_one_dispenses_per_day, pet_one_amount_dispensed, pet_one_increments, pet_one_time_between_increments, pet_two_dispenses_per_day, pet_two_amount_dispensed, pet_two_increments, pet_two_time_between_increments
    while True:
         # Stores owner's phone number
        while True:
            try:
                sql = "SELECT phone_number FROM Gen;"
                cur.execute(sql)
                phone_number = cur.fetchone()[0]
                phone_number = '+' + str(phone_number)
                lookup = client.lookups.v1.phone_numbers(phone_number).fetch()
                print('Phone number saved as' + phone_number)
                break
            except TwilioRestException:
                print('Invalid phone number. Please try again.')

        print('Beginning initial calibration...')

        # Stores distance without pet in front of the dispenser
        sql = "SELECT calibrate_distance FROM Gen;"
        cur.execute(sql)
        if cur.fetchone()[0]:
            dist_before_motion = get_distance_before_motion()
            sql = "UPDATE Gen SET calibrate_distance = false WHERE calibrate_distance = true;"
            cur.execute(sql)
            print(dist_before_motion)
            print('Distance to floor saved.')

        # Delay so that "enter" key has time to reset
        time.sleep(0.1)

        # Assigns first pet type to dispenser 1
        sql = "SELECT detect_pet FROM Dispenser1;"
        cur.execute(sql)
        if cur.fetchone()[0]:
            pet_one = store_pet()
            sql = "UPDATE Dispenser1 SET detect_pet = false WHERE detect_pet = true;"
            cur.execute(sql)
            sql = "UPDATE Dispenser1 SET pet_breed = '" + pet_one + "';"
            cur.execute(sql)
            print('Pet one saved as ', pet_one)

        # Fetch dispenser 1 settings from database
        sql = "SELECT dispenses_per_day, amount_dispensed, increments, time_between_increments FROM Dispenser1;"
        cur.execute(sql)
        pet_one_dispenses_per_day = cur.fetchone()[0]
        print(pet_one_dispenses_per_day)
        pet_one_amount_dispensed = cur.fetchone()[1]
        print(pet_one_amount_dispensed)
        pet_one_increments = cur.fetchone()[2]
        print(pet_one_increments)
        pet_one_time_between_increments = cur.fetchone()[3]
        print(pet_one_time_between_increments)

        # Assigns second pet type to dispenser 2
        sql = "SELECT detect_pet FROM Dispenser2;"
        cur.execute(sql)
        if cur.fetchone()[0]:
            pet_two = store_pet()
            sql = "UPDATE Dispenser2 SET detect_pet = false WHERE detect_pet = true;"
            cur.execute(sql)
            sql = "UPDATE Dispenser2 SET pet_breed = '" + pet_two + "';"
            cur.execute(sql)
            print('Pet two saved as ', pet_two)

        # Fetch dispenser 2 settings from database
        sql = "SELECT dispenses_per_day, amount_dispensed, increments, time_between_increments FROM Dispenser2;"
        pet_two_dispenses_per_day = cur.fetchone()[0]
        pet_two_amount_dispensed = cur.fetchone()[1]
        pet_two_increments = cur.fetchone()[2]
        pet_two_time_between_increments = cur.fetchone()[3]

if __name__ == '__main__':
    try: 
        db = pymysql.connect(host=os.environ['AWS_RDS_ENDPOINT'],
                             user=os.environ['AWS_RDS_USERNAME'],
                             passwd=os.environ['AWS_RDS_PASSWORD'],
                             db='dispenser')
        cur = db.cursor()

        # Create a thread to listen for changes in the database
        mysql = threading.Thread(target=sql_listener, args=(cur, ))
        motion = threading.Thread(target=motion_detected, args=(dist_before_motion, ))
        d1 = threading.Thread(target=dispenser_one, args=(pet_one, pet_one_dispenses_per_day, pet_one_amount_dispensed, pet_one_increments, pet_one_time_between_increments, ))
        d2 = threading.Thread(target=dispenser_two, args=(pet_two, pet_two_dispenses_per_day, pet_two_amount_dispensed, pet_two_increments, pet_two_time_between_increments, ))

        mysql.daemon = True
        motion.daemon = True
        d1.daemon = True
        d2.daemon = True

        mysql.start()
        motion.start()
        d1.start()
        d2.start()
        
        mysql.join()
        motion.join()
        d1.join()
        d2.join()

    except KeyboardInterrupt:
        print('Exiting program...')
        db.close()
        release_camera()
        GPIO.cleanup()
