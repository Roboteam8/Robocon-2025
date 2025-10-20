import RPi.GPIO as GPIO
import time
import threading
import sys

# --- 設定 ---
EMERGENCY_PIN = 17  # 非常停止ボタン入力ピン番号
MOTOR_L_PIN = 18  # 左モーターPWMピン例
MOTOR_R_PIN = 23  # 右モーターPWMピン例

running = True  # 非常停止でFalseになる


# --- モーター制御スレッド ---
def motor_control():
    global running
    while running:
        # 実際のモーター制御処理（PWM出力など）
        GPIO.output(MOTOR_L_PIN, GPIO.HIGH)
        GPIO.output(MOTOR_R_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(MOTOR_L_PIN, GPIO.LOW)
        GPIO.output(MOTOR_R_PIN, GPIO.LOW)
        time.sleep(0.5)


# --- 非常停止時の割り込み処理 ---
def emergency_stop(channel):
    global running
    running = False
    # 出力を全て停止
    GPIO.output(MOTOR_L_PIN, GPIO.LOW)
    GPIO.output(MOTOR_R_PIN, GPIO.LOW)
    GPIO.cleanup()
    sys.exit(0)


# --- GPIO設定 ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(EMERGENCY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MOTOR_L_PIN, GPIO.OUT)
GPIO.setup(MOTOR_R_PIN, GPIO.OUT)

# 割り込み設定：ボタンが押されたら（LOW）非常停止
GPIO.add_event_detect(
    EMERGENCY_PIN, GPIO.FALLING, callback=emergency_stop, bouncetime=300
)

try:
    # モーター制御スレッド起動
    motor_thread = threading.Thread(target=motor_control)
    motor_thread.start()

    # メインループ（特に表示なし）
    while running:
        time.sleep(1)

except KeyboardInterrupt:
    running = False
    GPIO.cleanup()
    sys.exit(0)
