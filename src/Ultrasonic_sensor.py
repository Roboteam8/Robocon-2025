import RPi.GPIO as GPIO
import time

# GPIOピンの設定
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    # トリガーを初期化
    GPIO.output(TRIG, False)
    time.sleep(0.1)

    # 超音波パルスを送信
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10µs
    GPIO.output(TRIG, False)

    # ECHOがHIGHになるまで待機
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # ECHOがLOWになるまで待機
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # 時間差を計算
    pulse_duration = pulse_end - pulse_start

    # 音速 = 約34300 cm/s
    distance = pulse_duration * 34300 / 2

    return round(distance, 2)

try:
    while True:
        dist = get_distance()
        print(f"距離: {dist} cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("終了します")
    GPIO.cleanup()