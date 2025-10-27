import asyncio
from dataclasses import dataclass, field

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

    _pwm: PWM = field(init=False)
    _run_break_on: bool = False

    def __post_init__(self):
        GPIO.setup(self.start_stop_pin, GPIO.OUT)
        GPIO.setup(self.run_break_pin, GPIO.OUT)
        GPIO.setup(self.direction_pin, GPIO.OUT)
        GPIO.setup(self.pwm_pin, GPIO.OUT)

        self._pwm = GPIO.PWM(self.pwm_pin, 1000)  # 1kHz
        self._pwm.start(0)

        GPIO.output(self.run_break_pin, GPIO.HIGH)
        GPIO.output(self.start_stop_pin, GPIO.HIGH)

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
        GPIO.output(self.direction_pin, speed < 0)
        self._pwm.ChangeDutyCycle(abs(speed))


@dataclass
class Robot(Visualizable):
    """
    ロボットの情報を管理するクラス
    Attributes:
        position (tuple[float, float]): ロボットの位置 (x, y)
        rotation (float): ロボットの向き (rad)
        radius (float): ロボットの半径
        r_wheel (Wheel): 右ホイールオブジェクト
        l_wheel (Wheel): 左ホイールオブジェクト
    """

    position: tuple[float, float]
    rotation: float
    radius: float

    r_wheel: Wheel
    l_wheel: Wheel

    _dc = 20
    _r_min = _dc * 50
    _wheel_circumference = 100 * np.pi
    _speed = _wheel_circumference * _r_min / 60

    async def _go_straight(self, length: float):
        """
        ロボットを直進させるメソッド
        Args:
            length (float): 直進距離 (mm)
        """
        duration = length / self._speed
        self.r_wheel.set_speed(self._dc)
        self.l_wheel.set_speed(self._dc)
        self.r_wheel.on()
        self.l_wheel.on()
        await asyncio.sleep(duration)
        self.r_wheel.off()
        self.l_wheel.off()

    async def _turn(self, angle: float):
        """
        ロボットを回転させるメソッド
        Args:
            angle (float): 回転角度 (rad)
        Returns:
        """
        arc_length = self.radius * abs(angle)
        duration = arc_length / self._speed
        if angle > 0:
            self.r_wheel.set_speed(-self._dc)
            self.l_wheel.set_speed(self._dc)
        else:
            self.r_wheel.set_speed(self._dc)
            self.l_wheel.set_speed(-self._dc)
        self.r_wheel.on()
        self.l_wheel.on()
        await asyncio.sleep(duration)
        self.r_wheel.off()
        self.l_wheel.off()

    _path: list[tuple[float, float]] = field(default_factory=list)

    async def drive(self, path: list[tuple[float, float]]) -> None:
        """
        ロボットを指定された経路に沿って移動させるメソッド
        Args:
            path (list[tuple[float, float]]): 移動経路の座標リスト
        """
        self._path = path

        for tx, ty in self._path:
            cx, cy = self.position
            if tx == cx and ty == cy:
                continue

            angle_diff = np.arctan2(ty - cy, tx - cx) - self.rotation
            if abs(angle_diff) > 1e-2:
                await self._turn(angle_diff)
                # TODO: mock
                self.rotation = np.arctan2(ty - cy, tx - cx)

            position_diff = np.hypot(tx - cx, ty - cy)
            if abs(position_diff) > 1e-2:
                await self._go_straight(position_diff)
                # TODO: mock
                self.position = (tx, ty)

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

        x, y = self.position
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
        arrow_dx = arrow_length * np.cos(self.rotation)
        arrow_dy = arrow_length * np.sin(self.rotation)
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
