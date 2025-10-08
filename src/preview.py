from matplotlib import patches
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.artist import Artist

from robot import Robot
from stage import Stage


def preview(stage: Stage) -> tuple[Figure, Axes]:
    """
    ステージのプレビューを表示する関数

    Args:
        stage (Stage): ステージの情報
    Returns:
        fig (Figure): 描画オブジェクト
        ax (Axes): 描画用の座標軸オブジェクト
    """
    fig, ax = plt.subplots()

    # ステージの枠
    ax.add_patch(
        patches.Rectangle(
            (0, 0),
            stage.x_size,
            stage.y_size,
            fill=None,
            edgecolor="black",
            zorder=10,
        )
    )

    # 壁の描画
    for wall in stage.walls:
        (x1, y1), (x2, y2) = wall
        ax.plot(
            [x1, x2],
            [y1, y2],
            color="black",
            linewidth=5,
            zorder=20,
            solid_capstyle="butt",
        )

    # ゴールの描画
    for goal in stage.goals:
        x, y = goal.position
        width, height = goal.size
        ax.add_patch(
            patches.Rectangle(
                (x, y),
                width,
                height,
                fill=True,
                color="green",
                alpha=0.5,
                zorder=30,
            )
        )
        ax.text(
            x + width / 2,
            y + height / 2,
            str(goal.id),
            fontsize=20,
            ha="center",
            va="center",
            zorder=40,
        )

    robot_artists: list[Artist] = []

    # ロボットの描画関数
    def draw_robot(ax: Axes, robot: Robot) -> list[Artist]:
        return robot_artists

    return fig, ax
