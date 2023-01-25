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
        GPIO.output(trigger, True)
    
        time.sleep(0.00001)
        GPIO.output(trigger, False)
        
        startTime = time.time()
        stopTime = time.time()
        
        while GPIO.input(echo) == 0:
            startTime = time.time()
            
        while GPIO.input(echo) == 1:
            stopTime = time.time()
            
        timeElapsed = stopTime - startTime
        
        distance = (timeElapsed * 34300) / 2
        
        return distance

if __name__ == '__main__':
    ultrasonic_pet_detect = UltrasonicRanger()
    ultrasonic_pet_detect.setup(constant.ULTRASONIC_TRIGGER_PET, constant.ULTRASONIC_ECHO_PET)
    ultrasonic_pet_detect.distance(constant.ULTRASONIC_TRIGGER_PET, constant.ULTRASONIC_ECHO_PET)