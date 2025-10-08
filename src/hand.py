import RPi.GPIO as GPIO
import time

# --- サーボ設定 ---
RIGHT_SERVO_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(RIGHT_SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(RIGHT_SERVO_PIN, 50)  # 50HzでPWM生成
servo.start(0)

def set_angle(angle):
    duty = 2.5 + (angle / 18)
    GPIO.output(RIGHT_SERVO_PIN, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.4)
    GPIO.output(RIGHT_SERVO_PIN, False)
    servo.ChangeDutyCycle(0)

try:
    print("右サーボ テスト開始")

    # --- 初期位置（少し左寄り = 70°） ---
    print("初期位置（70°）へ移動中...")
    set_angle(70)
    time.sleep(1)

    # --- 右回転テスト ---
    print("右へ回転（110°へ）...")
    set_angle(110)
    time.sleep(1)

    # --- 元に戻す ---
    print("中央（70°）へ戻す...")
    set_angle(70)
    time.sleep(1)

    print("テスト完了")

except KeyboardInterrupt:
    print("終了します")

finally:
    servo.stop()
    GPIO.cleanup()
