import threading
import time
from dataclasses import dataclass, field

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from gpio import GPIO
from tasks.driving import Driver
from tasks.parcel_loading import Arm
from visualize import Visualizable


@dataclass
class Robot(Visualizable):
    """
    ロボットの情報を管理するクラス
    Attributes:
        position (tuple[float, float]): ロボットの位置 (x, y)
        rotation (float): ロボットの向き (rad, -pi to pi)
        radius (float): ロボットの半径
        driver (Driver): ロボットの運転を担当するDriverオブジェクト
        arm (Arm): ロボットのアームを担当するArmオブジェクト
    """

    position: tuple[float, float]
    rotation: float
    radius: float

    driver: Driver
    arm: Arm

    __task_thread: threading.Thread = field(init=False, default=None)

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
        self.r_wheel.on(GPIO.HIGH)
        self.l_wheel.on(GPIO.LOW)
        while duration > 0:
            if self.__cancel_event.is_set():
                break
            chunk = min(1 / 30, duration)
            with self.__position_lock:
                nx = self.position[0] + chunk * self.__SPEED * np.cos(self.rotation)
                ny = self.position[1] + chunk * self.__SPEED * np.sin(self.rotation)
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
            self.r_wheel.on(GPIO.LOW)
            self.l_wheel.on(GPIO.HIGH)
        else:
            self.r_wheel.on(GPIO.HIGH)
            self.l_wheel.on(GPIO.LOW)
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
