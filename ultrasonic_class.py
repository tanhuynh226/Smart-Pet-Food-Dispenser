import RPi.GPIO as GPIO
import time
import constant

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

class UltrasonicRanger:
    def setup(self, trigger, echo):
        GPIO.setup(trigger, GPIO.OUT)
        GPIO.setup(echo, GPIO.IN)

    def distance(self, trigger, echo):
        dist_arr = []
        GPIO.output(trigger, True)
    
        time.sleep(0.00001)
        GPIO.output(trigger, False)
        
        while(len(dist_arr) < 5):
            startTime = time.time()
            stopTime = time.time()

            while GPIO.input(echo) == 0:
                startTime = time.time()

            while GPIO.input(echo) == 1:
                stopTime = time.time()

            timeElapsed = stopTime - startTime
            dist_arr.append((timeElapsed * 34300) / 2)
        sum = 0
        for x in dist_arr:
            sum += x
        distance = sum/len(dist_arr)
        
        return distance

if __name__ == '__main__':
    ultrasonic_pet_detect = UltrasonicRanger()
    ultrasonic_pet_detect.setup(constant.ULTRASONIC_TRIGGER_PET, constant.ULTRASONIC_ECHO_PET)
    print(ultrasonic_pet_detect.distance(constant.ULTRASONIC_TRIGGER_PET, constant.ULTRASONIC_ECHO_PET))
