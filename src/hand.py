import RPi.GPIO as GPIO
import time

# -----------------------------
# 右サーボ設定
# -----------------------------
SERVO_RIGHT = 26  # 右サーボGPIOピン

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_RIGHT, GPIO.OUT)

pwm_right = GPIO.PWM(SERVO_RIGHT, 50)  # 50Hz
pwm_right.start(0)

# -----------------------------
# サーボ角度制御関数（逆回転対応）
# -----------------------------
def set_angle(pwm, angle):
    """
    PWMに角度を送る
    angle: 0〜180の人間がわかる角度
    """
    angle = max(0, min(180, angle))  # 安全範囲制限
    duty = 2.5 + ((180 - angle) / 18)  # 逆回転に変換
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

# -----------------------------
# メイン処理
# -----------------------------
try:
    print("右サーボ 逆回転テスト開始")

    # 初期位置を150度に設定
    initial_angle = 150
    set_angle(pwm_right, initial_angle)
    time.sleep(1)

    # 逆回転方向で右に動かす例（数値を減らすと右回転）
    for target_angle in [150, 140, 130, 120, 110]:
        print(f"右回転（逆モード）: {target_angle}°")
        set_angle(pwm_right, target_angle)
        time.sleep(0.5)

    # 元の位置に戻す
    print("元の位置（150°）に戻ります...")
    set_angle(pwm_right, initial_angle)
    print("テスト完了")

except KeyboardInterrupt:
    print("テスト中断")

finally:
    pwm_right.stop()
    GPIO.cleanup()
