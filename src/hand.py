import time

import RPi.GPIO as GPIO

# GPIO番号で指定
servo_pin = 21

# GPIO設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

# PWM設定 (50Hz)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)


# 角度をデューティ比に変換する関数
def set_angle(angle):
    duty = 2 + (angle / 18)  # 0°=2.5%、180°=12.5%くらい
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)  # サーボが動くのを待つ
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)


try:
    while True:
        # 0度に動かす
        set_angle(0)
        time.sleep(1)

        # 40度に動かす
        set_angle(40)
        time.sleep(1)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
