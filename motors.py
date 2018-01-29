import RPi.GPIO as GPIO


# I am still confused about which pin is right
M1B = 23
M1F = 21
M2B = 16
M2F = 18


class Motor(object):
    type = 'Motor'

    def __init__(self, pin_fw, pin_bw):

        self.pin_fw = pin_fw
        self.pin_bw = pin_bw
        self._speed = 0

    def speed(self, speed=100):

        if speed > 100 or speed < -100:
            raise ValueError("Speed must be between -100 and 100")

        self._speed = speed
        if speed > 0:
            self.pwm_bw.ChangeDutyCycle(0)
            self.pwm_fw.ChangeDutyCycle(speed)
        if speed < 0:
            self.pwm_fw.ChangeDutyCycle(0)
            self.pwm_bw.ChangeDutyCycle(abs(speed))
        if speed == 0:
            self.pwm_fw.ChangeDutyCycle(0)
            self.pwm_bw.ChangeDutyCycle(0)

        return speed


motor = [Motor(M1F, M1B), Motor(M2F, M2B)]


def init():
    GPIO.setmode(GPIO.BOARD)

    for i in range(0, 2):
        setup_gpio(motor[i].pin_fw, GPIO.OUT, initial=GPIO.LOW)
        setup_gpio(motor[i].pin_bw, GPIO.OUT, initial=GPIO.LOW)

        motor[i].pwm_fw = GPIO.PWM(motor[i].pin_fw, 100)
        motor[i].pwm_fw.start(0)

        motor[i].pwm_bw = GPIO.PWM(motor[i].pin_bw, 100)
        motor[i].pwm_bw.start(0)


def setup_gpio(pin=None, mode=None, initial=0):
    if pin is not None and mode is not None:
        if mode == GPIO.OUT:
            GPIO.setup(pin, mode, initial=initial)
        else:
            GPIO.setup(pin, mode)

    def stop(self):
        self.speed(0)
