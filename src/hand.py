import RPi.GPIO as GPIO
import time

SERVO_RIGHT = 26  # 右サーボのGPIOピン

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_RIGHT, GPIO.OUT)

pwm_right = GPIO.PWM(SERVO_RIGHT, 50)
pwm_right.start(0)

def set_angle(pwm, angle):
    """PWMに角度を送る"""
    angle = max(0, min(180, angle))  # 安全範囲制限
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    pwm.ChangeDutyCycle(0)

try:
    print("右サーボテスト開始")

    # 初期位置0°（左端）
    set_angle(pwm_right, 0)
    time.sleep(1)

    # 右回転0°→40°まで段階的に動かす
    for angle in range(0, 41, 5):  # 0,5,10,...,40
        print(f"右回転: {angle}°")
        set_angle(pwm_right, angle)
        time.sleep(0.5)

    # 右回転後、中央位置に戻す（0°）
    set_angle(pwm_right, 0)
    print("右サーボテスト完了")

except KeyboardInterrupt:
    pass

finally:
    pwm_right.stop()
    GPIO.cleanup()
