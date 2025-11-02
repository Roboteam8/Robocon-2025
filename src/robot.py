import asyncio
from dataclasses import dataclass, field

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from ar import ARMarker
from robot_parts.arm import Arm
from robot_parts.camera import detect_ar
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

    async def drive(
        self, path: list[tuple[float, float]], markers: list[ARMarker], back = False
    ) -> None:
        """
        指定された経路に沿ってロボットを運転する非同期メソッド

        Args:
            path (list[tuple[float, float]]): ロボットが辿る経路の座標リスト
        """
        self.__path = path[::-1] if back else path

        for i, (tx, ty) in enumerate(self.__path):
            self.detect_position(markers)
            cx, cy = self.position
            if tx == cx and ty == cy:
                continue

            angle_diff = (np.arctan2(ty - cy, tx - cx) - self.rotation + np.pi) % (
                2 * np.pi
            ) - np.pi
            await self.driver.turn(angle_diff)
            self.rotation = (self.rotation + angle_diff + np.pi) % (2 * np.pi) - np.pi

            position_diff = np.hypot(tx - cx, ty - cy)
            await self.driver.straight(position_diff)
            while position_diff > 0:
                chunk = min(position_diff, 300)
                await self.driver.straight(-chunk if back else chunk)
                self.detect_position(markers)
                cx1, cy1 = self.position
                angle_diff = (np.arctan2(ty - cy1, tx - cx1) - self.rotation + np.pi) % (
                    2 * np.pi
                ) - np.pi
                if angle_diff > np.degrees(10):
                    self.__path.insert(i, (cx1, cy1))
                    self.rotation = np.arctan2(ty - cy1, tx - cx1)
                    break
                position_diff -= chunk
            self.position = (tx, ty)
        await asyncio.sleep(0.1)

    async def pickup_parcel(self):
        """
        荷物をピックアップする非同期メソッド
        """
        await self.arm.release_hands()
        await self.arm.open_shoulders()
        # distance = float("inf")
        # while distance >= 150:
        #     distance = await hear_ultrasonic()
        #     if distance >= 150:
        #         await self.driver.straight(10)
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
        await self.driver.straight(-300)
        # await self.arm.close_shoulders()
        # await asyncio.sleep(0.1)

    def detect_position(self, markers: list[ARMarker]):
        detected = detect_ar()
        if not detected:
            return
        xs = []
        ys = []
        for (rx, ry), m_id in detected:
            if m_id >= len(markers):
                continue
            mx, my = markers[m_id - 1].position
            ma = markers[m_id - 1].normal_angle
            x = mx + rx * np.cos(ma) + ry * np.sin(ma)
            y = my + rx * np.sin(ma) - ry * np.cos(ma)
            xs.append(x)
            ys.append(y)
            print(f"AR ID:{m_id} pos:({x:.1f},{y:.1f})")
        self.position = (float(np.mean(xs)), float(np.mean(ys)))

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
