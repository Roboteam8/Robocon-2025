import RPi.GPIO as GPIO
import time

SERVO_RIGHT = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_RIGHT, GPIO.OUT)

pwm_right = GPIO.PWM(SERVO_RIGHT, 50)
pwm_right.start(0)

def set_angle(pwm, angle):
    """PWMに角度を送る"""
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    pwm.ChangeDutyCycle(0)

# ===== ソフト上で中央位置を再定義 =====
# 物理的に逆向きなら180、通常なら90
center_right = 180  # ここを変えると中央を補正可能

try:
    print("右サーボ段階テスト開始")

    # 中央位置にセット
    set_angle(pwm_right, center_right)
    time.sleep(1)

    # 右回転方向に段階的に動かす（0〜40°オフセット）
    for offset in range(0, 41, 5):
        target_angle = center_right + offset
        # 180°を超えないように制限
        target_angle = min(target_angle, 180)
        print(f"右回転: {target_angle}°")
        set_angle(pwm_right, target_angle)

    time.sleep(1)

    # 左回転方向に段階的に動かす（0〜-40°オフセット）
    for offset in range(0, -41, -5):
        target_angle = center_right + offset
        target_angle = max(target_angle, 0)
        print(f"左回転: {target_angle}°")
        set_angle(pwm_right, target_angle)

    # 最後に中央に戻す
    set_angle(pwm_right, center_right)
    print("テスト完了")

except KeyboardInterrupt:
    pass

finally:
    pwm_right.stop()
    GPIO.cleanup()
