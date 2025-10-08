import RPi.GPIO as GPIO
import time

SERVO_RIGHT = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_RIGHT, GPIO.OUT)

pwm_right = GPIO.PWM(SERVO_RIGHT, 50)
pwm_right.start(0)

def set_angle(pwm, angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

try:
    # 中央90°
    set_angle(pwm_right, 90)
    time.sleep(1)

    # 右方向
    set_angle(pwm_right, 130)
    time.sleep(1)

    # 左方向
    set_angle(pwm_right, 50)
    time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    pwm_right.stop()
    GPIO.cleanup()

