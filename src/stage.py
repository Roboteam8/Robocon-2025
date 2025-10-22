from dataclasses import dataclass

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D

from robot import Robot
from visualize import Visualizable


@dataclass
class Wall(Visualizable):
    """
    壁の情報を管理するクラス
    Attributes:
        start (tuple[int, int]): 壁の始点座標 (x, y)
        end (tuple[int, int]): 壁の終点座標 (x, y)
    """

    start: tuple[int, int]
    end: tuple[int, int]

    def visualize(self, ax: Axes):
        ax.plot(
            [self.start[0], self.end[0]],
            [self.start[1], self.end[1]],
            color="brown",
            linewidth=5,
            solid_capstyle="butt",
        )


@dataclass
class Goal(Visualizable):
    """
    ゴールの情報を管理するクラス
    Attributes:
        position (tuple[int, int]): ゴールの左下座標 (x, y)
        size (int): ゴールの一辺の長さ (mm)
        goal_id (int): ゴールの識別子
    """

    position: tuple[int, int]
    size: int
    goal_id: int

    def visualize(self, ax: Axes):
        ax.add_patch(
            Rectangle(
                self.position,
                self.size,
                self.size,
                facecolor="lightgreen",
                edgecolor="green",
            )
        )
        ax.text(
            self.position[0] + self.size / 2,
            self.position[1] + self.size / 2,
            f"Goal {self.goal_id}",
            color="black",
            fontsize=12,
            ha="center",
            va="center",
        )


@dataclass
class ARMarker(Visualizable):
    """
    ARマーカーの情報を管理するクラス
    Attributes:
        position (tuple[int, int]): ARマーカーの座標 (x, y)
        normal (tuple[int, int]): ARマーカーの法線ベクトル (nx, ny)
        marker_id (int): ARマーカーの識別子
    """

    position: tuple[int, int]
    normal: tuple[int, int]
    marker_id: int

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
            f"AR Marker {self.marker_id}",
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


@dataclass
class StartArea(Visualizable):
    """
    スタートエリアの情報を管理するクラス
    Attributes:
        position (tuple[int, int]): スタートエリアの左下座標 (x, y)
        size (int): スタートエリアの一辺の長さ (mm)
    """

    position: tuple[int, int]
    size: int

    def visualize(self, ax: Axes):
        ax.add_patch(
            Rectangle(
                self.position,
                self.size,
                self.size,
                facecolor="lightyellow",
                edgecolor="yellow",
            )
        )
        center = self.position[0] + self.size / 2, self.position[1] + self.size / 2
        parcel_size = 175, 225
        ax.add_patch(
            Rectangle(
                (center[0] - parcel_size[0] / 2, center[1] - parcel_size[1] / 2),
                parcel_size[0],
                parcel_size[1],
                fill=False,
                edgecolor="black",
            )
        )


@dataclass
class Stage(Visualizable):
    """
    ステージの情報を管理するクラス
    Attributes:
        x_size (int): ステージのx方向サイズ (mm)
        y_size (int): ステージのy方向サイズ (mm)
        start_area (StartArea): スタートエリアの情報
        walls (list[Wall]): 壁のリスト
        goals (list[Goal]): ゴールのリスト
        ar_markers (list[ARMarker]): ARマーカーのリスト
        robot (Robot): ステージ上のロボット
    """

    x_size: int
    y_size: int
    start_area: StartArea
    walls: list[Wall]
    goals: list[Goal]
    ar_markers: list[ARMarker]
    robot: Robot

    def visualize(self, ax: Axes):
        ax.set_title("Stage Visualization")
        ax.axis("off")
        ax.set_aspect("equal", adjustable="box")

        # ステージの枠
        ax.add_patch(
            Rectangle(
                (0, 0),
                self.x_size,
                self.y_size,
                fill=None,
                edgecolor="black",
            )
        )

        return None
