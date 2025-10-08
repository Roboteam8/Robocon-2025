import RPi.GPIO as GPIO
import time

SERVO_RIGHT = 26  # 右サーボGPIOピン

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_RIGHT, GPIO.OUT)

pwm_right = GPIO.PWM(SERVO_RIGHT, 50)
pwm_right.start(0)

def set_angle(pwm, angle):
    """PWMに角度を送る"""
    angle = max(0, min(180, angle))
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    pwm.ChangeDutyCycle(0)

try:
    print("右サーボ 右回転テスト開始")

    # 初期位置（今の正しい位置を維持）
    initial_angle = (160//180)*100
    set_angle(pwm_right, initial_angle)
    time.sleep(1)

    # 🔁 回転方向を反転：angle を増やすと右回転になるように補正
    for offset in range(0,40 , 5):  # 0→5→...→40
        target_angle = initial_angle - (60 - offset)  # ←ここで右回転方向を反転
        print(f"右回転: {target_angle}°")
        set_angle(pwm_right, target_angle)
        time.sleep(0.5)

    # 元の位置に戻す
    set_angle(pwm_right, initial_angle)
    print("テスト完了")

except KeyboardInterrupt:
    pass

finally:
    pwm_right.stop()
    GPIO.cleanup()
