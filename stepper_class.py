import RPi.GPIO as GPIO
import time
import sys

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class Motor:
    def setup(self, channel):
        GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)

    def dispense(self, channel, seconds):
        start = time.time()

        while time.time() < start + seconds:
            try:
                GPIO.output(channel, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
                time.sleep(0.002)
                GPIO.output(channel, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
                time.sleep(0.002)
                GPIO.output(channel, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
                time.sleep(0.002)
                GPIO.output(channel, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
                time.sleep(0.002)
                GPIO.output(channel, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
                time.sleep(0.002)
            except KeyboardInterrupt as e:
                print(e)
        print('Motor stopped')