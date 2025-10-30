import threading
import time
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from gpio import GPIO, PWM
from visualize import Visualizable


@dataclass
class Wheel:
    start_stop_pin: int
    run_break_pin: int
    direction_pin: int
    pwm_pin: int
    dir_func: Callable[[float], bool]

    _pwm: PWM = field(init=False)
    _run_break_on: bool = False

    def __post_init__(self):
        GPIO.setup(self.start_stop_pin, GPIO.OUT)
        GPIO.setup(self.run_break_pin, GPIO.OUT)
        GPIO.setup(self.direction_pin, GPIO.OUT)
        GPIO.setup(self.pwm_pin, GPIO.OUT)

        self._pwm = GPIO.PWM(self.pwm_pin, 1000)  # 1kHz
        self._pwm.start(0)

    def on(self):
        """
        ホイールを動作状態にするメソッド
        """
        GPIO.output(self.start_stop_pin, GPIO.LOW)

    def off(self):
        """
        ホイールを停止状態にするメソッド
        """
        GPIO.output(self.start_stop_pin, GPIO.HIGH)

    def set_speed(self, speed: float):
        """
        ホイールの速度を設定するメソッド
        Args:
            speed (float): ホイールの速度 (-100.0 〜 100.0)
        """
        GPIO.output(self.direction_pin, self.dir_func(speed))
        self._pwm.ChangeDutyCycle(abs(speed))


@dataclass
class Shoulder:
    r_open_pin: int
    r_close_pin: int
    l_open_pin: int
    l_close_pin: int
    freq = 416

    _r_open_pwm: PWM = field(init=False)
    _r_close_pwm: PWM = field(init=False)
    _l_open_pwm: PWM = field(init=False)
    _l_close_pwm: PWM = field(init=False)

    def __post_init__(self):
        GPIO.setup(self.r_open_pin, GPIO.OUT)
        GPIO.setup(self.r_close_pin, GPIO.OUT)
        GPIO.setup(self.l_open_pin, GPIO.OUT)
        GPIO.setup(self.l_close_pin, GPIO.OUT)

        self._r_open_pwm = GPIO.PWM(self.r_open_pin, self.freq)
        self._r_close_pwm = GPIO.PWM(self.r_close_pin, self.freq)
        self._l_open_pwm = GPIO.PWM(self.l_open_pin, self.freq)
        self._l_close_pwm = GPIO.PWM(self.l_close_pin, self.freq)

        self._r_open_pwm.start(0)
        self._r_close_pwm.start(0)
        self._l_open_pwm.start(0)
        self._l_close_pwm.start(0)

    def open_shoulder(self):
        self._r_open_pwm.ChangeDutyCycle(50)
        self._l_open_pwm.ChangeDutyCycle(50)
        time.sleep((1 / self.freq) * 400)
        self._r_open_pwm.ChangeDutyCycle(0)
        self._l_open_pwm.ChangeDutyCycle(0)

    def close_shoulder(self):
        self._r_close_pwm.ChangeDutyCycle(50)
        self._l_close_pwm.ChangeDutyCycle(50)
        time.sleep((1 / self.freq) * 400)
        self._r_close_pwm.ChangeDutyCycle(0)
        self._l_close_pwm.ChangeDutyCycle(0)


@dataclass
class Hand:
    pin: int
    initial_angle: float
    grip_angle: float

    _pwm: PWM = field(init=False)

    def __post_init__(self):
        GPIO.setup(self.pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self.pin, 50)  # 50Hz
        self._pwm.start(0)
        self._set_angle(self.initial_angle)

    def _set_angle(self, angle: float):
        """
        PWMに送る角度を設定
        angle: 0～180の範囲
        """
        duty = 2 + (angle / 18)  # SG90などの標準サーボ用
        self._pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)  # サーボが動く時間を確保
        self._pwm.ChangeDutyCycle(0)

    def grip(self):
        self._set_angle(self.grip_angle)

    def release(self):
        self._set_angle(self.initial_angle)


@dataclass
class Arm:
    shoulder: Shoulder
    r_hand: Hand
    l_hand: Hand

    def grip_hand(self):
        self.r_hand.grip()
        self.l_hand.grip()

    def release_hand(self):
        self.r_hand.release()
        self.l_hand.release()

    def open_shoulder(self):
        self.shoulder.open_shoulder()

    def close_shoulder(self):
        self.shoulder.close_shoulder()


@dataclass
class Robot(Visualizable):
    """
    ロボットの情報を管理するクラス
    Attributes:
        position (tuple[float, float]): ロボットの位置 (x, y)
        rotation (float): ロボットの向き (rad, -pi to pi)
        radius (float): ロボットの半径
        r_wheel (Wheel): 右ホイールオブジェクト
        l_wheel (Wheel): 左ホイールオブジェクト
        arm (Arm): アームオブジェクト
    """

    position: tuple[float, float]
    rotation: float
    radius: float

    r_wheel: Wheel
    l_wheel: Wheel
    arm: Arm

    _dc = 50
    _angle_per_sec = np.radians(360 / 5)
    _spd_per_sec = (138 / 3) * 10  # mm/s

    _drive_thread: threading.Thread | None = None
    _cancel_event: threading.Event = field(default_factory=threading.Event)
    _position_lock: threading.Lock = field(default_factory=threading.Lock)

    _path: list[tuple[float, float]] = field(default_factory=list)

    def drive(self, path: list[tuple[float, float]]) -> None:
        """
        ロボットを指定された経路に沿って移動させるメソッド
        Args:
            path (list[tuple[float, float]]): 移動経路の座標リスト
        """
        if self._drive_thread and self._drive_thread.is_alive():
            self._cancel_event.set()
            self._drive_thread.join()
        self._drive_thread = threading.Thread(
            target=lambda: self._drive(path), daemon=True
        )
        self._cancel_event.clear()
        self._drive_thread.start()

    def _drive(self, path: list[tuple[float, float]]) -> None:
        self._path = path

        for tx, ty in self._path:
            with self._position_lock:
                cx, cy = self.position
                current_rotation = self.rotation
            if tx == cx and ty == cy:
                continue

            angle_diff = (np.arctan2(ty - cy, tx - cx) - current_rotation + np.pi) % (
                2 * np.pi
            ) - np.pi
            if abs(angle_diff) > 1e-2:
                self._turn(angle_diff)

            position_diff = np.hypot(tx - cx, ty - cy)
            if abs(position_diff) > 1e-2:
                self._go_straight(position_diff)

    def _go_straight(self, length: float):
        """
        ロボットを直進させるメソッド
        Args:
            length (float): 直進距離 (mm)
        """
        duration = length / self._spd_per_sec
        self.r_wheel.set_speed(self._dc)
        self.l_wheel.set_speed(self._dc)
        self.r_wheel.on()
        self.l_wheel.on()
        while duration > 0:
            if self._cancel_event.is_set():
                break
            chunk = min(1 / 30, duration)
            with self._position_lock:
                nx = self.position[0] + chunk * self._spd_per_sec * np.cos(self.rotation)
                ny = self.position[1] + chunk * self._spd_per_sec * np.sin(self.rotation)
                self.position = (nx, ny)
            time.sleep(chunk)
            duration -= chunk
        self.r_wheel.off()
        self.l_wheel.off()

    def _turn(self, angle: float):
        """
        ロボットを回転させるメソッド
        Args:
            angle (float): 回転角度 (rad)
        """
        duration = abs(angle) / self._angle_per_sec
        if angle > 0:
            self.r_wheel.set_speed(-self._dc)
            self.l_wheel.set_speed(self._dc)
        else:
            self.r_wheel.set_speed(self._dc)
            self.l_wheel.set_speed(-self._dc)
        self.r_wheel.on()
        self.l_wheel.on()
        while duration > 0:
            if self._cancel_event.is_set():
                break
            chunk = min(1 / 30, duration)
            delta_angle = chunk * self._angle_per_sec
            with self._position_lock:
                if angle > 0:
                    self.rotation += delta_angle
                else:
                    self.rotation -= delta_angle
            time.sleep(chunk)
            duration -= chunk
        self.r_wheel.off()
        self.l_wheel.off()

    def animate(self, ax: Axes) -> list[Artist]:
        animated: list[Artist] = []

        if self._path:
            path_xs, path_ys = zip(*self._path)
            path_line = ax.plot(
                path_xs,
                path_ys,
                linestyle="--",
                color="magenta",
                linewidth=1,
            )
            animated.extend(path_line)

        with self._position_lock:
            x, y = self.position
            rotation = self.rotation
        # ロボットの円
        circle = Circle(
            (x, y),
            self.radius,
            fill=True,
            color="blue",
        )
        animated.append(ax.add_patch(circle))
        # ロボットの向きを示す矢印
        arrow_length = self.radius
        arrow_dx = arrow_length * np.cos(rotation)
        arrow_dy = arrow_length * np.sin(rotation)
        arrow = ax.arrow(
            x,
            y,
            arrow_dx,
            arrow_dy,
            width=5,
            color="white",
        )
        animated.append(ax.add_patch(arrow))
        # ロボットの中心点
        center_dot = Circle(
            (x, y),
            self.radius * 0.1,
            color="red",
        )
        animated.append(ax.add_patch(center_dot))
        return animated
