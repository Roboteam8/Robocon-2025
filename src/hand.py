import RPi.GPIO as GPIO
import time

# ===== GPIO設定 =====
TRIG = 2   # トリガー
ECHO = 3   # エコー
SERVO = 21  # サーボ

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(SERVO, GPIO.OUT)

# サーボPWM設定
pwm = GPIO.PWM(SERVO, 50)  # 50Hz
pwm.start(0)

# ===== サーボ角度設定関数 =====
def set_angle(angle):
    duty = 2 + (angle / 18)  # 0°→2%, 180°→12%
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

# ===== 超音波距離測定関数（タイムアウト付き） =====
def get_distance(timeout=1.0):
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()

    # パルス開始を待つ
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start - start_time > timeout:
            return None  # タイムアウト

    # パルス終了を待つ
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end - start_time > timeout:
            return None  # タイムアウト

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # cmに変換
    return round(distance, 2)

# ===== メインループ =====
try:
    while True:
        dist = get_distance()
        if dist is None:
            print("距離が測れません")
            set_angle(0)  # タイムアウト時はサーボを0度に
        else:
            print(f"距離: {dist} cm")
            if dist <= 20:  # 閾値
                set_angle(40)
            else:
                set_angle(0)

        time.sleep(2)

except KeyboardInterrupt:
    print("終了します")

finally:
    pwm.stop()
    GPIO.cleanup()
