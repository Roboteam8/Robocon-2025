import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from gpio import GPIO, DigitalPin, PwmPin
from visualize import Visualizable


class Wheel:
    __DC: float = 50

    __start_stop: DigitalPin
    __run_break: DigitalPin
    __direction: DigitalPin
    __pwm: PwmPin

    def __init__(
        self, start_stop_pin: int, run_break_pin: int, direction_pin: int, pwm_pin: int
    ):
        self.__start_stop = DigitalPin(start_stop_pin, GPIO.OUT)
        self.__run_break = DigitalPin(run_break_pin, GPIO.OUT)
        self.__direction = DigitalPin(direction_pin, GPIO.OUT)
        self.__pwm = PwmPin(pwm_pin)

    def on(self, direction: Literal[0, 1]):
        self.__direction.set_state(direction)
        self.__pwm.set_dc(self.__DC)

    def off(self):
        self.__pwm.set_dc(0)


class Shoulder:
    __FREQENCY: int = 416

    def __init__(self, open_pin: int, close_pin: int):
        self.__open_pwm = PwmPin(open_pin, self.__FREQENCY)
        self.__close_pwm = PwmPin(close_pin, self.__FREQENCY)

    def open(self):
        self.__open_pwm.set_dc(50)
        time.sleep((1 / self.__FREQENCY) * 400)
        self.__open_pwm.set_dc(0)

    def close(self):
        self.__close_pwm.set_dc(50)
        time.sleep((1 / self.__FREQENCY) * 400)
        self.__close_pwm.set_dc(0)


class Hand:
    __pwm: PwmPin
    __release_angle: float
    __grip_angle: float

    def __init__(self, pin_num: int, release_angle: float, grip_angle: float) -> None:
        self.__pwm = PwmPin(pin_num, freqency=50)
        self.__set_angle(release_angle)
        self.__release_angle = release_angle
        self.__grip_angle = grip_angle

    def __set_angle(self, angle: float):
        self.__pwm.set_dc(2 + (angle / 18))
        time.sleep(0.5)
        self.__pwm.set_dc(0)

    def release(self):
        self.__set_angle(self.__release_angle)

    def grip(self):
        self.__set_angle(self.__grip_angle)

@dataclass
class Arm:
    r_shoulder: Shoulder
    l_shoulder: Shoulder
    r_hand: Hand
    l_hand: Hand

    def open_shoulders(self):
        with ThreadPoolExecutor() as executor:
            executor.submit(self.r_shoulder.open)
            executor.submit(self.l_shoulder.open)

    def close_shoulders(self):
        with ThreadPoolExecutor() as executor:
            executor.submit(self.r_shoulder.close)
            executor.submit(self.l_shoulder.close)

    def release_hands(self):
        with ThreadPoolExecutor() as executor:
            executor.submit(self.r_hand.release)
            executor.submit(self.l_hand.release)

    def grip_hands(self):
        with ThreadPoolExecutor() as executor:
            executor.submit(self.r_hand.grip)
            executor.submit(self.l_hand.grip)


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

    __ANGLE_SPEED = np.radians(360 / 5)
    __SPEED = (138 / 3) * 10

    __drive_thread: threading.Thread | None = field(init=False,default=None)
    __cancel_event: threading.Event = field(init=False, default_factory=threading.Event)
    __position_lock: threading.Lock = field(init= False, default_factory=threading.Lock)

    __path: list[tuple[float, float]] = field(init=False, default_factory=list)

    def drive(self, path: list[tuple[float, float]]) -> None:
        """
        ロボットを指定された経路に沿って移動させるメソッド
        Args:
            path (list[tuple[float, float]]): 移動経路の座標リスト
        """
        if self.__drive_thread and self.__drive_thread.is_alive():
            self.__cancel_event.set()
            self.__drive_thread.join()
        self.__drive_thread = threading.Thread(
            target=lambda: self.__drive(path), daemon=True
        )
        self.__cancel_event.clear()
        self.__drive_thread.start()

    def __drive(self, path: list[tuple[float, float]]) -> None:
        self.__path = path

        for tx, ty in self.__path:
            with self.__position_lock:
                cx, cy = self.position
                current_rotation = self.rotation
            if tx == cx and ty == cy:
                continue

            angle_diff = (np.arctan2(ty - cy, tx - cx) - current_rotation + np.pi) % (
                2 * np.pi
            ) - np.pi
            if abs(angle_diff) > 1e-2:
                self.__turn(angle_diff)

            position_diff = np.hypot(tx - cx, ty - cy)
            if abs(position_diff) > 1e-2:
                self.__go_straight(position_diff)

    def __go_straight(self, length: float):
        """
        ロボットを直進させるメソッド
        Args:
            length (float): 直進距離 (mm)
        """
        duration = length / self.__SPEED
        self.r_wheel.on(1)
        self.l_wheel.on(0)
        while duration > 0:
            if self.__cancel_event.is_set():
                break
            chunk = min(1 / 30, duration)
            with self.__position_lock:
                nx = self.position[0] + chunk * self.__SPEED * np.cos(
                    self.rotation
                )
                ny = self.position[1] + chunk * self.__SPEED * np.sin(
                    self.rotation
                )
                self.position = (nx, ny)
            time.sleep(chunk)
            duration -= chunk
        self.r_wheel.off()
        self.l_wheel.off()

    def __turn(self, angle: float):
        """
        ロボットを回転させるメソッド
        Args:
            angle (float): 回転角度 (rad)
        """
        duration = abs(angle) / self.__ANGLE_SPEED
        if angle > 0:
            self.r_wheel.on(0)
            self.l_wheel.on(1)
        else:
            self.r_wheel.on(1)
            self.l_wheel.on(0)
        while duration > 0:
            if self.__cancel_event.is_set():
                break
            chunk = min(1 / 30, duration)
            delta_angle = chunk * self.__ANGLE_SPEED
            with self.__position_lock:
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

        if self.__path:
            path_xs, path_ys = zip(*self.__path)
            path_line = ax.plot(
                path_xs,
                path_ys,
                linestyle="--",
                color="magenta",
                linewidth=1,
            )
            animated.extend(path_line)

        with self.__position_lock:
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
