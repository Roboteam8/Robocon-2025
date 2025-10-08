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

# ===== 右サーボ中央位置 =====
center_right = 90

try:
    print("右サーボ段階テスト開始")

    # 中央位置にセット
    set_angle(pwm_right, center_right)
    time.sleep(1)

    # 右回転方向に段階的に動かす（0〜40°オフセット）
    for offset in range(0, 41, 5):  # 0,5,10,...,40
        target_angle = center_right + offset
        print(f"右回転: {target_angle}°")
        set_angle(pwm_right, target_angle)

    time.sleep(1)

    # 左回転方向に段階的に動かす（0〜-40°オフセット）
    for offset in range(0, -41, -5):  # 0,-5,-10,...,-40
        target_angle = center_right + offset
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
