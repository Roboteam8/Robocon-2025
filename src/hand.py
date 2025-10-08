import RPi.GPIO as GPIO
import time

SERVO_RIGHT = 26  # 右サーボGPIOピン

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_RIGHT, GPIO.OUT)

pwm_right = GPIO.PWM(SERVO_RIGHT, 50)  # 50Hz
pwm_right.start(88)

def set_angle(pwm, angle):
    """PWMに角度を送る"""
    angle = max(0, min(180, angle))   # 0〜180°に制限
    duty = 2.5 + (angle / 18)         # サーボ用デューティ比（中心を安定化）
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

try:
    print("右サーボ 右回転テスト開始")

    # ✅ 初期位置（ユーザが「正しい」と確認した位置）
    initial_angle = 160
    set_angle(pwm_right, initial_angle)
    time.sleep(1)

    # ✅ angleを減らすことで右回転に
    for target_angle in [160, 150, 140, 130, 120]:
        print(f"右回転: {target_angle}°")
        set_angle(pwm_right, target_angle)
        time.sleep(0.6)

    # ✅ 元の位置に戻す
    print("元の位置に戻ります...")
    set_angle(pwm_right, initial_angle)
    print("テスト完了")

except KeyboardInterrupt:
    pass

finally:
    pwm_right.stop()
    GPIO.cleanup()
