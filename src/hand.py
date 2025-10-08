import RPi.GPIO as GPIO
import time

SERVO_RIGHT = 26  # 右サーボGPIOピン

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
    print("右サーボ 初期位置補正 + 右回転テスト開始")

    # 初期位置を20°左へ補正（見た目の中心に合わせる）
    initial_angle = 20
    set_angle(pwm_right, initial_angle)
    time.sleep(1)

    # 右回転方向（時計回り）へ動かす
    for offset in range(0, 41, 5):  # 0→5→...→40
        target_angle = initial_angle + offset  # 正方向が右回転
        print(f"右回転: {target_angle}°")
        set_angle(pwm_right, target_angle)
        time.sleep(0.5)

    # 初期位置に戻す
    set_angle(pwm_right, initial_angle)
    print("テスト完了")

except KeyboardInterrupt:
    pass

finally:
    pwm_right.stop()
    GPIO.cleanup()

