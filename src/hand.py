import RPi.GPIO as GPIO
import time

SERVO_RIGHT = 26  # 右サーボGPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_RIGHT, GPIO.OUT)

pwm_right = GPIO.PWM(SERVO_RIGHT, 50)
pwm_right.start(0)

def set_angle(pwm, angle):
    """PWMに角度を送る"""
    angle = max(0, min(180, angle))  # 安全範囲
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    pwm.ChangeDutyCycle(0)

# 右サーボ中央位置（物理的初期位置0°に合わせる）
center_right = 0

try:
    print("右サーボ逆回転補正テスト開始")

    # 初期位置
    set_angle(pwm_right, center_right)
    time.sleep(1)

    # 右回転（プログラム上で反転）
    for offset in range(0, 41, 5):  # 0〜40°
        # 反転補正：180 - (center + offset)
        target_angle = 180 - (center_right + offset)
        target_angle = max(0, min(180, target_angle))
        print(f"右回転（補正済）: {target_angle}°")
        set_angle(pwm_right, target_angle)
        time.sleep(0.5)

    # 中央に戻す
    target_angle = 180 - center_right
    set_angle(pwm_right, target_angle)
    print("テスト完了")

except KeyboardInterrupt:
    pass

finally:
    pwm_right.stop()
    GPIO.cleanup()
