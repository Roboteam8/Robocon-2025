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
# サーボ角度制御関数
# -----------------------------
def set_angle(pwm, angle):
    """
    PWMに角度を送る
    angle: 0〜180の人間がわかる角度
    """
    angle = max(0, min(180, angle))  # 安全範囲制限
    duty = 2.5 + (angle / 18)        # サーボ用デューティ比計算
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)                  # 信号保持時間を長めに
    pwm.ChangeDutyCycle(0)

# -----------------------------
# メイン処理
# -----------------------------
try:
    print("右サーボ 右回転テスト開始")

    # 初期位置（物理的に反転したモーターを考慮）
    initial_angle = 30  # 適宜変更可能。反転前より左寄りに設定
    set_angle(pwm_right, initial_angle)
    time.sleep(1)

    # 右回転方向へ動かす（反転済みなので増加方向で右回転）
    for target_angle in [30, 40, 50, 60, 70]:
        print(f"右回転: {target_angle}°")
        set_angle(pwm_right, target_angle)
        time.sleep(0.5)

    # 元の位置に戻す
    print("元の位置に戻ります...")
    set_angle(pwm_right, initial_angle)
    print("テスト完了")

except KeyboardInterrupt:
    print("テスト中断")

finally:
    pwm_right.stop()
    GPIO.cleanup()
