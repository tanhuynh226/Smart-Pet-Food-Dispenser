import cv2
import time

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