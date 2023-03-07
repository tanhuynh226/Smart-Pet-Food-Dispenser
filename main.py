import os
import numpy as np
import time
import constant
import threading
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import pymysql
import PySimpleGUI as sg
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

def get_title_str(layout):
    return layout[0][0].DisplayText

def get_last_layout_num(layout_order):
    return len(layout_order) - 1

def app():
    global phone_number, pet_one_dispenses_per_day, pet_one_amount_dispensed, pet_one_increments, pet_one_time_between_increments, pet_two_dispenses_per_day, pet_two_amount_dispensed, pet_two_increments, pet_two_time_between_increments

    phone_page = [[sg.Text('Enter your phone number (include country number):', font = ('Arial Bold', 12))],
                [sg.Input('', key = 'phone_number', enable_events = True, expand_x=True, justification='left')],
                [sg.Button('Next', key = 'phone_edit')], 
                [sg.Button('Exit'), sg.Button('Home')]]

    calibration_page = [[sg.Text('Motion Detection Calibration', font = ('Arial Bold', 12))], 
            [sg.Text('Please do not place anything in front of the device. Click the "Ready" button below after ensuring so.', justification = 'center')],
            [sg.Button('Ready', key = 'calibration')],
            [sg.Button('Back'), sg.Button('Next')], 
            [sg.Button('Exit'), sg.Button('Home')]]

    pet_id1 = [[sg.Text('Dispenser 1 Pet Identification', font = ('Arial Bold', 12))], 
            [sg.Text('Please place your first pet in front of the camera. Click the "Ready" button below after ensuring so.', justification = 'center')],
            [sg.Button('Ready', key = 'pet_id1')],
            [sg.Button('Back'), sg.Button('Next')],
            [sg.Button('Exit'), sg.Button('Home')]]

    pet_q1 = [[sg.Text('Input 1st Pet Info', font = ('Arial Bold', 12))],
            [sg.Text('How many times per day would you like your pet to be fed?')],
            [sg.Input('', key = 'pet_one_dispenses_per_day', expand_x=True, justification='left')],
            [sg.Text('How much should each meal be (cups)?')],
            [sg.Input('', key = 'pet_one_amount_dispensed', expand_x=True, justification='left')],
            [sg.Text('How many increments should the food be dispensed?')],
            [sg.Input('', key = 'pet_one_increments', expand_x=True, justification='left')],
            [sg.Text('How many seconds in between each increment (seconds)?')],
            [sg.Input('', key = 'pet_one_time_between_increments', expand_x=True, justification='left')],
            [sg.Button('Back'), sg.Button('Next', key = 'pet1_info')], 
            [sg.Button('Exit'), sg.Button('Home')]]

    pet_id2 = [[sg.Text('Dispenser 2 Pet Identification', font = ('Arial Bold', 12))], 
            [sg.Text('Please place your second pet in front of the camera. Click the "Next" button below after ensuring so.', justification = 'center')],
            [sg.Button('Ready', key = 'pet_id2')],
            [sg.Button('Back'), sg.Button('Next')], 
            [sg.Button('Exit'), sg.Button('Home')]]

    pet_q2 = [[sg.Text('Input 2nd Pet Info', font = ('Arial Bold', 12))],
            [sg.Text('How many times per day would you like your pet to be fed?')],
            [sg.Input('', key = 'pet_two_dispenses_per_day', expand_x=True, justification='left')],
            [sg.Text('How much should each meal be (cups)?')],
            [sg.Input('', key = 'pet_two_amount_dispensed', expand_x=True, justification='left')],
            [sg.Text('How many increments should the food be dispensed?')],
            [sg.Input('', key = 'pet_two_increments', expand_x=True, justification='left')],
            [sg.Text('How many seconds in between each increment (seconds)?')],
            [sg.Input('', key = 'pet_two_time_between_increments', expand_x=True, justification='left')],
            [sg.Button('Back'), sg.Button('Next', key = 'pet2_info')], 
            [sg.Button('Exit'), sg.Button('Home')]]

    layout_order = [phone_page, calibration_page, pet_id1, pet_q1, pet_id2, pet_q2] # The page order that the initial setup takes

    home_button_order = ['Edit Phone Number', 'Recalibrate Motion Sensor', 'Recalibrate Dispenser 1 Pet ID', 'Edit Dispenser 1 Attributes', 'Recalibrate Dispenser 2 Pet ID', 'Edit Dispenser 2 Attributes']
    home_dispenser_label_1 = [[sg.Text('Dispenser 1 Pet')]] + [[sg.Text(pet_one)]]
    home_dispenser_label_2 = [[sg.Text('Dispenser 2 Pet')]] + [[sg.Text(pet_two)]]
    home_page = [[sg.Text('Home Page', font = ('Arial Bold', 12))]] + [[sg.Column(home_dispenser_label_1), sg.Column(home_dispenser_label_2)]] + [[sg.Button(str(button_name))] for button_name in home_button_order] + [[sg.Button('Exit')]]

    layout_order.append(home_page)


    layout = [[sg.Column(layout, key=str(idx), visible=(idx==0)) for idx, layout in enumerate(layout_order)]]

    window = sg.Window('Smart Pet Food Dispenser', layout)

    layout_num = 0 # The first layout in [layout_order] has key 0 and is visible

    while True:
        event, values = window.read()
        #print(values)
        
        if 'Exit' in event or event is None:
            break
        elif event == 'phone_number':
            if values['phone_number'] and values['phone_number'][-1] not in ('0123456789'):
                try:
                    phone_number = values['phone_number']
                    phone_number = '+' + str(phone_number)
                    lookup = client.lookups.v1.phone_numbers(phone_number).fetch()
                    print('Phone number saved as' + phone_number)
                    break
                except TwilioRestException:
                    sg.popup('Invalid phone number. Please try again.')
                    window['phone_number'].update(values['phone_number'][:-1])

        elif event == 'phone_edit':
            window[f'{layout_num}'].update(visible=False)
            layout_num += 1
            window[f'{layout_num }'].update(visible=True)
            print("Phone added")

    ###the READY buttons don't need to go to the next page, they just need to send data to the backend
        elif event == 'calibration':
            dist_before_motion = get_distance_before_motion()
            print(dist_before_motion)
            print('Distance to floor saved.')

        elif event == 'pet_id1':
            pet_one = store_pet()
            print('Pet one saved as ', pet_one)

        elif event == 'pet_id2':
            pet_two = store_pet()
            print('Pet two saved as ', pet_two)

    ###whenever the user pressed 'Next', it is considered a submit button and should update the user inputs into the backend
        elif event == 'pet1_info':
            pet_one_dispenses_per_day = values['pet_one_dispenses_per_day']
            pet_one_amount_dispensed = values['pet_one_amount_dispensed']
            pet_one_increments = values['pet_one_increments']
            pet_one_time_between_increments = values['pet_one_time_between_increments']

            window[f'{layout_num}'].update(visible=False)
            layout_num += 1
            window[f'{layout_num }'].update(visible=True)
            print("EDITED PET 1 INFO")

        elif event == 'pet2_info':
            pet_two_dispenses_per_day = values['pet_two_dispenses_per_day']
            pet_two_amount_dispensed = values['pet_two_amount_dispensed']
            pet_two_increments = values['pet_two_increments']
            pet_two_time_between_increments = values['pet_two_time_between_increments']

            window[f'{layout_num}'].update(visible=False)
            layout_num += 1
            window[f'{layout_num }'].update(visible=True)
            print("EDITED PET 2 INFO")

        elif "Next" in event:
            window[f'{layout_num}'].update(visible=False)
            layout_num += 1
            window[f'{layout_num }'].update(visible=True)
        elif "Back" in event:
            window[f'{layout_num}'].update(visible=False)
            layout_num -= 1
            window[f'{layout_num }'].update(visible=True)
        elif "Home" in event:
            window[f'{layout_num}'].update(visible=False)
            layout_num = get_last_layout_num(layout_order)
            window[f'{layout_num }'].update(visible=True)
        elif layout_num == get_last_layout_num(layout_order):
            # For the home page, find the page with the title corresponding with the button text
            for idx, button_name in enumerate(home_button_order):
                if button_name in event:
                    window[f'{layout_num}'].update(visible=False)
                    layout_num = idx
                    window[f'{layout_num }'].update(visible=True)

    window.close()

if __name__ == '__main__':
    try:
        # Create a thread to open the app
        application = threading.Thread(target=app)
        # Create a thread to detect motion
        motion = threading.Thread(target=motion_detected, args=(dist_before_motion, ))
        # Create a thread for each dispenser
        d1 = threading.Thread(target=dispenser_one, args=(pet_one, pet_one_dispenses_per_day, pet_one_amount_dispensed, pet_one_increments, pet_one_time_between_increments, ))
        d2 = threading.Thread(target=dispenser_two, args=(pet_two, pet_two_dispenses_per_day, pet_two_amount_dispensed, pet_two_increments, pet_two_time_between_increments, ))

        application.daemon = True
        motion.daemon = True
        d1.daemon = True
        d2.daemon = True

        application.start()
        motion.start()
        d1.start()
        d2.start()
        
        application.join()
        motion.join()
        d1.join()
        d2.join()

    except KeyboardInterrupt:
        print('Exiting program...')
        release_camera()
        GPIO.cleanup()
