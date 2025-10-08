import RPi.GPIO as GPIO
import time

SERVO_RIGHT = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_RIGHT, GPIO.OUT)

pwm_right = GPIO.PWM(SERVO_RIGHT, 50)
pwm_right.start(0)

def set_angle(pwm, angle):
    """PWMに角度を送る"""
    # 物理的制限：0°〜180°に制限
    angle = max(0, min(180, angle))
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    pwm.ChangeDutyCycle(0)

# 右サーボの物理的中央位置を0度として扱う
# 右回転方向に段階的に動かす
try:
    print("右サーボ右回転テスト開始")

    # 初期位置0°
    set_angle(pwm_right, 0)
    time.sleep(1)

    # 右回転方向に段階的に動かす（0°→40°→80°→…最大180°）
    for angle in range(0, 91, 10):  # 0°〜90°まで右回転
        print(f"右回転: {angle}°")
        set_angle(pwm_right, angle)
        time.sleep(0.5)

    # 最後に初期位置に戻す
    set_angle(pwm_right, 0)
    print("テスト完了")

except KeyboardInterrupt:
    pass

finally:
    pwm_right.stop()
    GPIO.cleanup()
