from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
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

    _path: npt.NDArray[np.float64] = field(
        default_factory=lambda: np.empty((0, 2), dtype=np.float64)
    )
    _path_index: int = 0

    def set_path(self, path: npt.NDArray[np.float64]) -> None:
        """
        ロボットの移動経路を設定するメソッド

        Args:
            path (npt.NDArray[np.float64]): ロボットの移動経路
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
        if self._path_index >= len(self._path):
            return
        cx, cy = self.position
        tx, ty = self._path[self._path_index]
        distance = np.hypot(tx - cx, ty - cy)
        direction = np.arctan2(ty - cy, tx - cx)
        if distance < 1e-2:
            self.position = (tx, ty)
            self._path_index += 1
            return
        # 向きを回転させる
        angle_diff = (direction - self.rotation + np.pi) % (2 * np.pi) - np.pi
        max_rotation = self._rotation_speed * dt
        if abs(angle_diff) >= 1e-2:
            rotation_amount = np.clip(angle_diff, -max_rotation, max_rotation)
            self.rotation += rotation_amount
            self.rotation %= 2 * np.pi
            return
        else:
            self.rotation = direction
        # 位置を移動させる
        max_distance = self._speed * dt
        move_distance = min(distance, max_distance)
        new_x = cx + move_distance * np.cos(self.rotation)
        new_y = cy + move_distance * np.sin(self.rotation)
        self.position = (new_x, new_y)

    def animate(self, ax: Axes) -> list[Artist]:
        animated: list[Artist] = []

        if self._path.size > 0:
            # 経路の描画
            path_x, path_y = zip(*self._path)
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
