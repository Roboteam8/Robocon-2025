from dataclasses import dataclass, field
from types import CoroutineType

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from robot_parts.arm import Arm
from robot_parts.driver import Driver
from util import CancellableTaskThread
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

    __path: list[tuple[float, float]] = field(init=False, default_factory=list)

    __task_thread: CancellableTaskThread | None = field(init=False, default=None)

    def __set_task(self, coro: CoroutineType):
        if self.__task_thread is not None:
            self.__task_thread.cancel()
            self.__task_thread.join()
        self.__task_thread = CancellableTaskThread(coro)

    def drive(self, path: list[tuple[float, float]]) -> None:
        """
        ロボットを指定された経路に沿って移動させる非同期タスクを開始する。
        既に移動タスクが実行中の場合はキャンセルされ、新しいタスクが開始される。

        Args:
            path (list[tuple[float, float]]): ロボットが移動する経路のリスト
        """
        self.__set_task(self.__drive(path))

    async def __drive(self, path: list[tuple[float, float]]) -> None:
        self.__path = path

        for tx, ty in self.__path:
            cx, cy = self.position
            if tx == cx and ty == cy:
                continue

            angle_diff = (np.arctan2(ty - cy, tx - cx) - self.rotation + np.pi) % (
                2 * np.pi
            ) - np.pi
            if abs(angle_diff) > 1e-2:
                await self.driver.trun(angle_diff)

            position_diff = np.hypot(tx - cx, ty - cy)
            if abs(position_diff) > 1e-2:
                await self.driver.straight(position_diff)

    def pickup_parcel(self):
        """
        ロボットのアームを使って荷物を拾う非同期タスクを開始する。
        既にアーム操作タスクが実行中の場合はキャンセルされ、新しいタスクが開始される。
        """
        self.__set_task(self.__pickup_parcel())

    async def __pickup_parcel(self):
        await self.arm.open_shoulders()
        await self.arm.grip_hands()
        await self.arm.close_shoulders()

    def release_parcel(self):
        """
        ロボットのアームを使って荷物を放す非同期タスクを開始する。
        既にアーム操作タスクが実行中の場合はキャンセルされ、新しいタスクが開始される。
        """
        self.__set_task(self.__release_parcel())

    async def __release_parcel(self):
        await self.arm.open_shoulders()
        await self.arm.release_hands()
        await self.arm.close_shoulders()

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
