from dataclasses import dataclass

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
        destination (tuple[float, float] | None): 目的地の位置 (x, y) または None
    """

    position: tuple[float, float]
    rotation: float
    radius: float

    destination: tuple[float, float] | None = None

    def animate(self, ax: Axes) -> list[Artist]:
        x, y = self.position
        animated: list[Artist] = []
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
