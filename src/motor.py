import RPi.GPIO as GPIO
import time

# ==== ピン設定 ====
# 左モーター用
LEFT_PWM = 12  # PWM信号出力ピン（GPIO12）
LEFT_DIR = 12  # 方向制御ピン（GPIO5）
LEFT_START = 9  # スタート/ストップ制御（GPIO6）

# 右モーター用
RIGHT_PWM = 13  # PWM信号出力ピン（GPIO13）
RIGHT_DIR = 19  # 方向制御ピン（GPIO19）
RIGHT_START = 26  # スタート/ストップ制御（GPIO26）

# ==== GPIO初期化 ====
GPIO.setmode(GPIO.BCM)
GPIO.setup([LEFT_DIR, LEFT_START, RIGHT_DIR, RIGHT_START], GPIO.OUT)
GPIO.setup([LEFT_PWM, RIGHT_PWM], GPIO.OUT)

# PWM周波数（例：1kHz）
left_pwm = GPIO.PWM(LEFT_PWM, 1000)
right_pwm = GPIO.PWM(RIGHT_PWM, 1000)
left_pwm.start(0)
right_pwm.start(0)


# ==== 制御関数 ====
def set_motor(direction_pin, start_pin, pwm, speed):
    """
    speed: -100〜100 (%)
    正の値 → 正転、負の値 → 逆転、0 → 停止
    """
    if speed > 0:
        GPIO.output(direction_pin, GPIO.HIGH)  # 正転
        GPIO.output(start_pin, GPIO.HIGH)  # 運転開始
    elif speed < 0:
        GPIO.output(direction_pin, GPIO.LOW)  # 逆転
        GPIO.output(start_pin, GPIO.HIGH)
    else:
        GPIO.output(start_pin, GPIO.LOW)  # 停止

    pwm.ChangeDutyCycle(min(abs(speed), 100))


def move(left_speed, right_speed, duration):
    """
    左右モーターの速度を調整して走行
    left_speed, right_speed: -100〜100 (%)
    duration: 動作時間（秒）
    """
    set_motor(LEFT_DIR, LEFT_START, left_pwm, left_speed)
    set_motor(RIGHT_DIR, RIGHT_START, right_pwm, right_speed)
    time.sleep(duration)
    stop()


def stop():
    """両輪停止"""
    GPIO.output(LEFT_START, GPIO.LOW)
    GPIO.output(RIGHT_START, GPIO.LOW)
    left_pwm.ChangeDutyCycle(0)
    right_pwm.ChangeDutyCycle(0)


# ==== 動作例 ====
try:
    move(70, 70, 2)  # 前進2秒
    move(50, 80, 1)  # 左旋回（右速め）
    move(80, 50, 1)  # 右旋回（左速め）
    move(-60, -60, 2)  # 後退2秒
finally:
    stop()
    left_pwm.stop()
    right_pwm.stop()
    GPIO.cleanup()
