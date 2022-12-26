import cv2
import time
import boto3

rek_client = boto3.client('rekognition')

def detect_pet_loop():
    # ultrasonic ranger loops to detect when there is a pet in front
    # calls collect_frames, then detect_pet if there is
    pass

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

