import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

hand_left_pin = 17
hand_right_pin = 18
CW_R = 9    # CW(時計回り)用パルス
CCW_R = 11   # CCW(反時計回り)用パルス
CW_L = 25    # CW(時計回り)用パルス
CCW_L = 8   # CCW(反時計回り)用パルス
start_right_pin = 16
run_right_pin = 20
dir_right_pin = 21
pw_right_pin = 2
start_left_pin = 13
run_left_pin = 19
dir_left_pin = 26
pw_left_pin = 3

GPIO.setup(CW_L, GPIO.OUT)
GPIO.setup(CCW_L, GPIO.OUT)
GPIO.setup(CW_R, GPIO.OUT)
GPIO.setup(CCW_R, GPIO.OUT)
GPIO.setup(hand_left_pin, GPIO.OUT)
GPIO.setup(hand_right_pin, GPIO.OUT)
GPIO.setup(start_left_pin, GPIO.OUT)
GPIO.setup(run_left_pin, GPIO.OUT)
GPIO.setup(pw_left_pin, GPIO.OUT)
GPIO.setup(dir_left_pin, GPIO.OUT)
GPIO.setup(start_right_pin, GPIO.OUT)
GPIO.setup(run_right_pin, GPIO.OUT)
GPIO.setup(pw_right_pin, GPIO.OUT)
GPIO.setup(dir_right_pin, GPIO.OUT)

GPIO.output(start_left_pin, GPIO.HIGH)
GPIO.output(run_left_pin, GPIO.HIGH)
GPIO.output(start_right_pin, GPIO.HIGH)
GPIO.output(run_right_pin, GPIO.HIGH)

steppoint = 400
delaypoint = 0.0006
angle_per_sec = 360 / 5
spd_per_sec = 138 / 3 

pwm_left = GPIO.PWM(hand_left_pin, 50)  # 50Hz
pwm_right = GPIO.PWM(hand_right_pin, 50)
pwm_left.start(0)
pwm_right.start(0)

def step(pin_L, pin_R, steps=200, delay=0.005):
    for _ in range(steps):
        GPIO.output(pin_L, GPIO.HIGH)
        GPIO.output(pin_R, GPIO.HIGH)   # ON
        time.sleep(delay)
        GPIO.output(pin_L, GPIO.LOW) 
        GPIO.output(pin_R, GPIO.LOW) # OFF
        time.sleep(delay)

def set_angle(pwm, angle):
    """
    PWMに送る角度を設定
    angle: 0～180の範囲
    """
    duty = 2 + (angle / 18)  # SG90などの標準サーボ用
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # サーボが動く時間を確保
    pwm.ChangeDutyCycle(0) 

def straight(dis):
    runtime = abs(dis) / spd_per_sec
    if dis >= 0:
        GPIO.output(dir_left_pin, GPIO.LOW)
        GPIO.output(dir_right_pin, GPIO.HIGH)
    else:
        GPIO.output(dir_left_pin, GPIO.HIGH)
        GPIO.output(dir_right_pin, GPIO.LOW)

    pin_left.ChangeDutyCycle(50) 
    pin_right.ChangeDutyCycle(50)
    time.sleep(runtime)
    pin_left.ChangeDutyCycle(0)
    pin_right.ChangeDutyCycle(0)

def turn_right(angle):
    turntime = angle / angle_per_sec
    GPIO.output(dir_left_pin, GPIO.LOW)
    GPIO.output(dir_right_pin, GPIO.LOW)    
    GPIO.output(dir_left_pin, GPIO.HIGH)
    GPIO.output(dir_right_pin, GPIO.HIGH)
    pin_left.ChangeDutyCycle(35)
    pin_right.ChangeDutyCycle(35)
    time.sleep(turntime)
    pin_left.ChangeDutyCycle(0)
    pin_right.ChangeDutyCycle(0)

input("Press any key...")

GPIO.output(start_left_pin, GPIO.LOW)
GPIO.output(run_left_pin, GPIO.LOW)
GPIO.output(start_right_pin, GPIO.LOW)
GPIO.output(run_right_pin, GPIO.LOW)

pin_left = GPIO.PWM(pw_left_pin, 1000)
pin_right = GPIO.PWM(pw_right_pin, 1000)
pin_left.start(0)
pin_right.start(0)
time.sleep(1)

try:
    set_angle(pwm_left, 0)  # 左サーボ安全位置
    set_angle(pwm_right, 160)
    time.sleep(1)
    distance_input = input("距離を入力してください")
    distance = float(distance_input)
    angle_input = input("回転角度を入力してください：")
    angles = int(angle_input)

    print(f"距離{distance}cm前進")
    straight(distance)
    print(f"角度{angles}だけ回転")
    turn_right(angles)
    time.sleep(2)
    print(f"CW方向にステップ回転")
    step(CW_R, CCW_L, steppoint+200, delaypoint)
    input("何か押して掴む")
    time.sleep(1)
    set_angle(pwm_left, 40)  # 左サーボ40°
    set_angle(pwm_right, 120)
    time.sleep(1)
    step(CCW_R, CW_L, steppoint, delaypoint)
    time.sleep(1)
    distance_input = input("距離を入力してください")
    distance = float(distance_input)
    angle_input = input("回転角度を入力してください：")
    angles = int(angle_input)

    print(f"距離{distance}cm前進")
    straight(distance)
    print(f"角度{angles}だけ回転")
    turn_right(angles)
    time.sleep(2)
    input("何か押して置きに行く")
    time.sleep(1)
    step(CW_R, CCW_L, steppoint+300, delaypoint)
    time.sleep(1)
    set_angle(pwm_left, 0)  # 左サーボ安全位置
    set_angle(pwm_right, 160)
    time.sleep(1)
    distance_input = input("距離を入力してください")
    distance = float(distance_input)
    angle_input = input("回転角度を入力してください：")
    angles = int(angle_input)

    print(f"距離{distance}cm前進")
    straight(distance)
    print(f"角度{angles}だけ回転")
    turn_right(angles)
    time.sleep(2)

finally:
    GPIO.cleanup()




