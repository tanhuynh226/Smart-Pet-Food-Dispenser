import cv2
import time
import boto3
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO_TRIGGER = 18
GPIO_ECHO = 24

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

rek_client = boto3.client('rekognition')

def collect_frames():
    capture = cv2.VideoCapture(0)
    img_counter = 0
    frame_set = []
    start_time = time.time()

    while True:
        ret, frame = capture.read()
        if img_counter == 5:
            break
        if time.time() - start_time >= 1: # Check if 1 sec passed
            img_name = "frames/frame_{}.png".format(img_counter)
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_counter))
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

def distance():
    GPIO.output(GPIO_TRIGGER, True)
    
    
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
    StartTime = time.time()
    StopTime = time.time()
    
    while GPIO.input(GPIO_ECHO) ==0:
        StartTime = time.time()
        
    while GPIO.input(GPIO_ECHO) ==1:
        StopTime = time.time()
        
    TimeElapsed = StopTime-StartTime
    
    distance= (TimeElapsed*34300)/2
    
    return distance

if __name__ == '__main__':
    try:
        #this only displays the distance 
        while True:
            dist = distance()
            print("Measured distance = %.1f cm" % dist)
            #testing "motion detection"
            #if (dist2-dist1) >
                #collect_frames()
                #detect_pet()
            
            #testing for "pet dispenser", if it is greater than 20cm from top of dispenser
            if dist > 20:
                print("Refill")
            time.sleep(.5) 
            
    except KeyboardInterrupt:
        print("Stopped_________")
        GPIO.cleanup()

