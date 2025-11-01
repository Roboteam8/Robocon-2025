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
        self, path: list[tuple[float, float]], markers: list[ARMarker]
    ) -> None:
        """
        指定された経路に沿ってロボットを運転する非同期メソッド

        Args:
            path (list[tuple[float, float]]): ロボットが辿る経路の座標リスト
        """
        self.__path = path

        for i, (tx, ty) in enumerate(self.__path):
            if tx == self.position[0] and ty == self.position[1]:
                continue

            angle_diff = (
                np.arctan2(ty - self.position[1], tx - self.position[0])
                - self.rotation
                + np.pi
            ) % (2 * np.pi) - np.pi
            await self.driver.turn(angle_diff)
            self.rotation += angle_diff

            await asyncio.sleep(0.3)

            position_diff = np.hypot(tx - self.position[0], ty - self.position[1])
            while position_diff > 5:
                await self.driver.straight(min(position_diff, 300))
                self.detect_position(markers)
                if dx == self.position[0] and dy == self.position[1]:
                    position_diff -= 300
                    continue
                if abs(np.arctan2(ty - dy, tx - dx) - self.rotation) > np.radians(1):
                    self.rotation = np.arctan2(
                        dy - self.position[1], dx - self.position[0]
                    )
                    self.position = (dx, dy)
                    self.__path.insert(i, (tx, ty))
                    break
                position_diff = np.hypot(tx - dx, ty - dy)

            await asyncio.sleep(0.3)
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

    def detect_position(self, markers: list[ARMarker]):
        detected = detect_ar()
        if not detected:
            return
        xs = []
        ys = []
        rs = []
        for (rx, ry), m_id in detected:
            if m_id >= len(markers):
                continue
            mx, my = markers[m_id - 1].position
            ma = markers[m_id - 1].normal_angle
            cr = ma + np.arctan2(ry, rx)
            cr = (cr + np.pi) % (2 * np.pi) - np.pi
            cr = cr - np.pi if cr > 0 else cr + np.pi
            rs.append(cr)
            x = mx - (rx * np.sin(cr) + ry * np.cos(cr))
            y = my - (- rx * np.cos(cr) + ry * np.sin(cr))
            xs.append(x)
            ys.append(y)
            print(f"AR ID:{m_id} pos:({x:.1f},{y:.1f}) rot:{np.degrees(cr):.1f}")
        self.position = (float(np.mean(xs)), float(np.mean(ys)))
        self.rotation = float(np.mean(rs))
        

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
