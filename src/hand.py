import RPi.GPIO as GPIO
import time

# ===== GPIO設定 =====
TRIG = 2
ECHO = 3
SERVO_LEFT = 21
SERVO_RIGHT = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(SERVO_LEFT, GPIO.OUT)
GPIO.setup(SERVO_RIGHT, GPIO.OUT)

# サーボPWM設定
pwm_left = GPIO.PWM(SERVO_LEFT, 50)
pwm_right = GPIO.PWM(SERVO_RIGHT, 50)
pwm_left.start(0)
pwm_right.start(0)

# ===== サーボ角度設定関数 =====
def set_angle(pwm, angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

# ===== 超音波距離測定関数（タイムアウト付き） =====
def get_distance(trig, echo, timeout=1.0):
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    start_time = time.time()

    # パルス開始待ち
    while GPIO.input(echo) == 0:
        pulse_start = time.time()
        if pulse_start - start_time > timeout:
            return None

    # パルス終了待ち
    while GPIO.input(echo) == 1:
        pulse_end = time.time()
        if pulse_end - start_time > timeout:
            return None

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # cmに変換
    return round(distance, 2)

# ===== メインループ =====
try:
    while True:
        dist = get_distance(TRIG, ECHO)

        if dist is None:
            print("距離が測れません")
            set_angle(pwm_left, 0)
            set_angle(pwm_right, 0)
        else:
            print(f"距離: {dist} cm")
            # 距離が 17±3 cm の範囲
            if 12 <= dist <= 18:
                set_angle(pwm_left, 40)
                set_angle(pwm_right, -40)
            else:
                set_angle(pwm_left, 0)
                set_angle(pwm_right, 0)

        time.sleep(1)

except KeyboardInterrupt:
    print("終了します")

finally:
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()
