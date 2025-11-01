from dataclasses import dataclass

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D

from visualize import Visualizable


@dataclass
class ARMarker(Visualizable):
    """
    ARマーカーの情報を管理するクラス
    Attributes:
        position (tuple[int, int]): ARマーカーの座標 (x, y)
        normal (tuple[int, int]): ARマーカーの法線ベクトル (nx, ny)
    """

    position: tuple[int, int]
    normal: tuple[int, int]

    @property
    def normal_angle(self):
        return np.arctan2(self.normal[1], self.normal[0])

    def visualize(self, ax: Axes):
        marker_size = 800
        ax.add_patch(
            Rectangle(
                (
                    self.position[0] - marker_size / 2,
                    self.position[1] - marker_size / 2,
                ),
                10,
                marker_size,
                facecolor="blanchedalmond",
                edgecolor="black",
                transform=Affine2D().rotate_deg_around(
                    self.position[0],
                    self.position[1],
                    np.degrees(np.arctan2(self.normal[1], self.normal[0])),
                ),
            )
        )
        ax.text(
            self.position[0],
            self.position[1],
            "AR Marker",
            color="black",
            fontsize=12,
            ha="center",
            va="center",
            transform=Affine2D().rotate_deg_around(
                self.position[0],
                self.position[1],
                np.degrees(np.arctan2(self.normal[1], self.normal[0])),
            ),
        )
