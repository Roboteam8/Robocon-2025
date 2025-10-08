import RPi.GPIO as GPIO
import time

# -----------------------------
# GPIO設定
# -----------------------------
TRIG = 2
ECHO = 3
SERVO_LEFT = 21
SERVO_RIGHT = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(SERVO_LEFT, GPIO.OUT)
GPIO.setup(SERVO_RIGHT, GPIO.OUT)

pwm_left = GPIO.PWM(SERVO_LEFT, 50)
pwm_right = GPIO.PWM(SERVO_RIGHT, 50)
pwm_left.start(0)
pwm_right.start(0)

# -----------------------------
# サーボ制御関数
# -----------------------------
def set_angle(pwm, angle, reverse=False):
    """
    pwm: PWMオブジェクト
    angle: 0〜180
    reverse: Trueなら逆回転モード
    """
    angle = max(0, min(180, angle))
    if reverse:
        duty = 2.5 + ((180 - angle) / 18)
    else:
        duty = 2.5 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

# -----------------------------
# 超音波距離測定関数
# -----------------------------
def measure_distance(timeout=0.03):
    GPIO.output(TRIG, False)
    time.sleep(0.05)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    start_time = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start - start_time > timeout:
            return None

    pulse_end = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end - pulse_start > timeout:
            return None

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # cm換算
    return round(distance, 2)

# -----------------------------
# メインループ
# -----------------------------
try:
    print("サーボ＆超音波テスト開始")

    # 初期位置
    left_angle = 10
    right_angle = 10
    set_angle(pwm_left, left_angle)
    set_angle(pwm_right, right_angle, reverse=True)
    time.sleep(1)

    while True:
        dist = measure_distance()
        if dist is None:
            print("距離が測れません")
            time.sleep(1)
            continue

        print(f"距離: {dist} cm")

        # 距離が10cm ±5cmならサーボ動作
        if 5 <= dist <= 15:
            # 左サーボ：数字増やして右回転
            left_angle = min(left_angle + 10, 180)
            set_angle(pwm_left, left_angle)
            # 右サーボ：逆回転モード、数字増やして右回転
            right_angle = min(right_angle + 10, 180)
            set_angle(pwm_right, right_angle, reverse=True)
        else:
            print("距離範囲外のためサーボ停止")
        time.sleep(1)

except KeyboardInterrupt:
    print("終了")

finally:
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()
