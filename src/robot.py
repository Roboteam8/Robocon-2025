from dataclasses import dataclass, field

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from visualize import Visualizable


@dataclass
class Robot(Visualizable):
    """
    ロボットの情報を管理するクラス
    Attributes:
        position (tuple[float, float]): ロボットの位置 (x, y)
        rotation (float): ロボットの向き (rad)
        radius (float): ロボットの半径
    """

    position: tuple[float, float]
    rotation: float
    radius: float

    _path: list[tuple[float, float]] = field(default_factory=list)
    _path_index: int = 0

    def set_path(self, path: list[tuple[float, float]]) -> None:
        """
        ロボットの移動経路を設定するメソッド

        Args:
            path (list[tuple[float, float]]): ロボットの移動経路
        """
        self._path = path
        self._path_index = 0

    _speed: float = 100  # mm/s
    _rotation_speed: float = np.radians(90)  # rad/s

    def update(self, dt: float) -> None:
        """
        ロボットの位置と向きを更新するメソッド

        Args:
            dt (float): 経過時間 (秒)
        """
        if self._path_index < len(self._path):
            target_x, target_y = self._path[self._path_index]
            current_x, current_y = self.position

            direction = np.arctan2(target_y - current_y, target_x - current_x)
            distance = np.hypot(target_x - current_x, target_y - current_y)

            # 向きを更新
            angle_diff = (direction - self.rotation + np.pi) % (2 * np.pi) - np.pi
            max_rotation = self._rotation_speed * dt
            if abs(angle_diff) < max_rotation:
                self.rotation = direction
            else:
                self.rotation += np.sign(angle_diff) * max_rotation

            # 位置を更新
            move_distance = min(self._speed * dt, distance)
            new_x = current_x + move_distance * np.cos(self.rotation)
            new_y = current_y + move_distance * np.sin(self.rotation)
            self.position = (new_x, new_y)

            # 目的地に到達したか確認
            if distance <= move_distance:
                self._path_index += 1

    def animate(self, ax: Axes) -> list[Artist]:
        animated: list[Artist] = []

        if self._path:
            # 経路の描画
            path_x, path_y = zip(*self._path[self._path_index :])
            (line,) = ax.plot(
                path_x,
                path_y,
                color="red",
                linestyle="--",
                linewidth=2,
            )
            animated.append(line)

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
            capstyle="butt",
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
