import RPi.GPIO as GPIO
import time

# --- ピン設定 ---
TRIG = 2
ECHO = 3

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    """HC-SR04から距離を測定（cm単位で返す）"""
    GPIO.output(TRIG, False)
    time.sleep(0.1)  # 安定のための待ち時間

    # 超音波パルス送信
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10μsパルス
    GPIO.output(TRIG, False)

    pulse_start = None
    pulse_end = None
    timeout = 0.02  # 20ms以内に応答がなければタイムアウト

    start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() - start > timeout:
            return None  # タイムアウト

    start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() - start > timeout:
            return None  # タイムアウト

    # 値が取れなかった場合は無効
    if pulse_start is None or pulse_end is None:
        return None

    # 距離を計算
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2
    return round(distance, 2)


try:
    print("測定を開始します（3秒ごとに出力）")
    while True:
        dist = get_distance()
        if dist is None:
            print("測定失敗（信号なしまたはタイムアウト）")
        else:
            print(f"距離: {dist} cm")
        time.sleep(3)  # ← 3秒ごとに測定

except KeyboardInterrupt:
    print("\n終了します")
    GPIO.cleanup()
