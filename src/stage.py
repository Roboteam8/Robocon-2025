from dataclasses import dataclass, field

from matplotlib.axes import Axes
from matplotlib.backend_bases import Event, MouseEvent
from matplotlib.patches import Rectangle

from a_star import AStarPlanner
from robot import Robot
from visualize import Visualizable


@dataclass
class Goal(Visualizable):
    """ゴールの情報を管理するクラス"""

    position: tuple[int, int]  # ゴールの位置(左下基準) (x, y)
    size: tuple[int, int]  # ゴールのサイズ (x幅, y幅)
    id: int  # ゴールのID

    def visualize(self, ax: Axes):
        x, y = self.position
        width, height = self.size
        rect = Rectangle(
            (x, y),
            width,
            height,
            fill=True,
            color="green",
            alpha=0.5,
        )
        ax.add_patch(rect)
        ax.text(
            x + width / 2,
            y + height / 2,
            f"Goal {self.id}",
            ha="center",
            va="center",
        )


@dataclass
class Stage(Visualizable):
    """ステージの情報を管理するクラス"""

    x_size: int  # ステージのx方向サイズ (mm)
    y_size: int  # ステージのy方向サイズ (mm)
    walls: list[
        tuple[tuple[int, int], tuple[int, int]]
    ]  # 壁のリスト [((x1, y1), (x2, y2)), ...]
    goals: list[Goal]  # ゴールのリスト
    robot: Robot  # ステージ上のロボット

    path_planner: AStarPlanner = field(init=False)  # 経路計画オブジェクト

    def __post_init__(self):
        cell_size = 50  # グリッドセルのサイズ (mm)
        grid_width = self.x_size // cell_size
        grid_height = self.y_size // cell_size
        self.path_planner = AStarPlanner(
            grid_size=(grid_height, grid_width),
            resolution=cell_size,
            robot_radius=self.robot.radius,
        )

        # 壁を障害物として追加
        obstacle_rects = []
        for wall in self.walls:
            (x1, y1), (x2, y2) = wall
            ox = min(x1, x2)
            oy = min(y1, y2)
            ow = abs(x2 - x1) if x1 != x2 else 10  # 壁の厚みを10mmに設定
            oh = abs(y2 - y1) if y1 != y2 else 10
            obstacle_rects.append((ox, oy, ow, oh))
        self.path_planner.add_obstacle(obstacle_rects)

    def visualize(self, ax: Axes):
        ax.set_title("Stage Visualization")
        ax.set_xlim(-self.robot.radius, self.x_size + self.robot.radius)
        ax.set_ylim(-self.robot.radius, self.y_size + self.robot.radius)
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

        # 壁の描画
        for wall in self.walls:
            (x1, y1), (x2, y2) = wall
            ax.plot(
                [x1, x2],
                [y1, y2],
                color="black",
                linewidth=5,
                solid_capstyle="butt",
            )

        def on_click(event: Event):
            if (
                type(event) is MouseEvent
                and event.inaxes == ax
                and event.xdata is not None
                and event.ydata is not None
            ):
                x, y = event.xdata, event.ydata
                self.robot.set_path((x, y), self.path_planner)

        ax.figure.canvas.mpl_connect("button_press_event", on_click)

        return None
