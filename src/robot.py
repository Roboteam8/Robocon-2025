import asyncio
from dataclasses import dataclass, field

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from robot_parts.arm import Arm
from robot_parts.driver import Driver
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

    async def drive(self, path: list[tuple[float, float]]) -> None:
        """
        指定された経路に沿ってロボットを運転する非同期メソッド

        Args:
            path (list[tuple[float, float]]): ロボットが辿る経路の座標リスト
        """
        self.__path = path

        for tx, ty in self.__path:
            cx, cy = self.position
            if tx == cx and ty == cy:
                continue

            angle_diff = (np.arctan2(ty - cy, tx - cx) - self.rotation + np.pi) % (
                2 * np.pi
            ) - np.pi
            if abs(angle_diff) > 1e-2:
                await self.driver.turn(angle_diff)
            self.rotation += angle_diff

            position_diff = np.hypot(tx - cx, ty - cy)
            if abs(position_diff) > 1e-2:
                await self.driver.straight(position_diff)
            self.position = (tx, ty)
        await asyncio.sleep(0.1)

    async def pickup_parcel(self):
        """
        荷物をピックアップする非同期メソッド
        """
        await self.arm.open_shoulders()
        await asyncio.sleep(0.1)
        await self.arm.grip_hands()
        await asyncio.sleep(0.1)
        await self.arm.close_shoulders()
        await asyncio.sleep(0.1)

    async def release_parcel(self):
        await self.arm.open_shoulders()
        await asyncio.sleep(0.1)
        await self.arm.release_hands()
        await asyncio.sleep(0.1)
        await self.arm.close_shoulders()
        await asyncio.sleep(0.1)

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
