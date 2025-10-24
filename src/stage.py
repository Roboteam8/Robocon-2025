from abc import ABCMeta, abstractmethod
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
        x (float): 壁のx座標 (左端)
        obstacled_y (list[tuple[float, float]]): 障害物があるy座標の範囲のリスト [(start_y, end_y), ...]
    """

    x: float
    obstacled_y: list[tuple[float, float]]

    def visualize(self, ax: Axes):
        width = 50  # 壁の幅
        for start_y, end_y in self.obstacled_y:
            ax.add_patch(
                Rectangle(
                    (self.x - width / 2, start_y),
                    width,
                    end_y - start_y,
                    color="brown",
                )
            )


@dataclass
class Area(Visualizable, metaclass=ABCMeta):
    """
    エリアの情報を管理するクラス
    Attributes:
        position (tuple[int, int]): エリアの左下座標 (x, y)
        size (int): エリアの一辺の長さ (mm)
    """

    position: tuple[int, int]
    size: int

    @property
    def center(self) -> tuple[float, float]:
        return (
            self.position[0] + self.size / 2,
            self.position[1] + self.size / 2,
        )

    @abstractmethod
    def _get_color(self) -> str:
        pass

    def visualize(self, ax: Axes):
        rect = Rectangle(
            self.position,
            self.size,
            self.size,
            edgecolor=self._get_color(),
            fill=False,
            linewidth=2,
        )
        rect.set_clip_path(rect)
        ax.add_patch(rect)


@dataclass
class GoalArea(Area):
    """
    ゴールの情報を管理するクラス
    Attributes:
        position (tuple[int, int]): ゴールの左下座標 (x, y)
        size (int): ゴールの一辺の長さ (mm)
        goal_id (int): ゴールの識別子
    """

    goal_id: int

    def _get_color(self) -> str:
        return f"C{self.goal_id - 1}"

    def visualize(self, ax: Axes):
        super().visualize(ax)
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
class StartArea(Area):
    """
    スタートエリアの情報を管理するクラス
    Attributes:
        position (tuple[int, int]): スタートエリアの左下座標 (x, y)
        size (int): スタートエリアの一辺の長さ (mm)
        parcel_size (tuple[int, int]): 荷物のサイズ (幅, 高さ)
    """

    position: tuple[int, int]
    size: int
    parcel_size: tuple[int, int] = (175, 225)

    def _get_color(self) -> str:
        return "yellow"

    def visualize(self, ax: Axes):
        super().visualize(ax)
        center = self.position[0] + self.size / 2, self.position[1] + self.size / 2
        ax.add_patch(
            Rectangle(
                (
                    center[0] - self.parcel_size[0] / 2,
                    center[1] - self.parcel_size[1] / 2,
                ),
                self.parcel_size[0],
                self.parcel_size[1],
                fill=False,
                edgecolor="black",
            )
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
    wall: Wall
    goals: list[GoalArea]
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
