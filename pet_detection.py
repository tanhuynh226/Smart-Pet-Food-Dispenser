import os
import cv2
import time
import boto3
import constant
import keyboard
import RPi.GPIO as GPIO
from ultrasonic_class import UltrasonicRanger
from dotenv import load_dotenv

load_dotenv()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

ultrasonic_pet_detect = UltrasonicRanger()
rek_client = boto3.client('rekognition')

capture = cv2.VideoCapture(-1, cv2.CAP_V4L)

def collect_frames():
    
    img_counter = 0
    start_time = time.time()

    while (img_counter < 5):
        ret, frame = capture.read()
        if time.time() - start_time >= 1: # Check if 1 sec passed
            img_name = 'frames/frame_{}.png'.format(img_counter)
            cv2.imwrite(img_name, frame)
            print('frame_{} written!'.format(img_counter))
            start_time = time.time()
            img_counter += 1

def detect_pet():
    img_counter = 0
    pet = []

    while (img_counter < 5):
        filename = 'frames/frame_{}.png'.format(img_counter)
        with open(filename, 'rb') as image:
            response = rek_client.detect_labels(Image={'Bytes': image.read()})

        labels = response['Labels']
        #print(f'Found {len(labels)} labels in the image:')
        for label in labels:
            if label['Name'] == 'Dog':
                confidence = label['Confidence']
                pet = detect_dog_breed(filename)
                break
            elif label['Name'] == 'Cat':
                confidence = label['Confidence']
                pet = ['Cat']
                break
        if pet:
            break
        img_counter += 1
    
    return pet

def detect_dog_breed(photo):
    pet = []
    model=os.environ['AWS_DOG_BREEDS_MODEL_ARN']
    min_confidence=60

    with open(photo, 'rb') as image:
        response = rek_client.detect_custom_labels(Image={'Bytes': image.read()},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    labels = response['CustomLabels']
    if labels:
        for label in labels:
            name = label['Name']
            pet.append(name)
        return pet
    else:
        return None

def store_pet():
    while True:
        if keyboard.is_pressed('enter'):
            collect_frames()
            pet = detect_pet()
            return pet

def release_camera():
    img_counter = 0
    while (img_counter < 5):
        img_name = 'frames/frame_{}.png'.format(img_counter)
        os.remove(img_name)
        img_counter += 1
    capture.release()

def get_distance_before_motion():
    while True:
        if keyboard.is_pressed('enter'):
            dist = ultrasonic_pet_detect.distance(constant.ULTRASONIC_TRIGGER_PET, constant.ULTRASONIC_ECHO_PET)
            return dist

if __name__ == '__main__':
#     print('Place your first pet in front of the camera and press enter once you have done so.')
#     pet_one = store_pet()
#     print(pet_one)
#     print('Pet one saved')
# 
#     print('Place your second pet in front of the camera and press enter once you have done so.')
#     pet_two = store_pet()
#     print(pet_two)
#     print('Pet two saved')
    release_camera()