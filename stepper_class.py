import RPi.GPIO as GPIO
import time
import constant

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

class StepperMotor:
    def setup(self, en_pin, dir_pin, step_pin):
        GPIO.setup(en_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(dir_pin, GPIO.OUT)
        GPIO.setup(step_pin, GPIO.OUT)
        GPIO.output(dir_pin, 1) # clockwise
        GPIO.output(en_pin,GPIO.LOW)

    def dispense(self, en_pin, dir_pin, step_pin, seconds):
        start = time.time()

        while time.time() < start + seconds:
            try:
                GPIO.output(step_pin, GPIO.HIGH)
                time.sleep(0.002)
                GPIO.output(step_pin, GPIO.LOW)
                time.sleep(0.002)
            except KeyboardInterrupt as e:
                print(e)
        print('Motor stopped')
        
if __name__ == '__main__':
    stepper_one = StepperMotor()
    stepper_one.setup(constant.STEPPER_ONE_ENABLE, constant.STEPPER_ONE_DIR, constant.STEPPER_ONE_STEP)
    stepper_one.dispense(constant.STEPPER_ONE_ENABLE, constant.STEPPER_ONE_DIR, constant.STEPPER_ONE_STEP, 10)
    stepper_two = StepperMotor()
    stepper_two.setup(constant.STEPPER_TWO_ENABLE, constant.STEPPER_TWO_DIR, constant.STEPPER_TWO_STEP)
    stepper_two.dispense(constant.STEPPER_TWO_ENABLE, constant.STEPPER_TWO_DIR, constant.STEPPER_TWO_STEP, 10)
    