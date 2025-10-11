import numpy as np
from matplotlib import patches
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.backend_bases import Event, MouseEvent
from matplotlib.figure import Figure

from stage import Stage


def preview(stage: Stage) -> None:
    """
    ステージのプレビューを表示する関数

    Args:
        stage (Stage): ステージの情報
    Returns:
        None
    """
    plotdata: tuple[Figure, list[Axes]] = plt.subplots(2, 1)
    fig, (ax1, ax2) = plotdata

    # ステージプレビューの設定
    ax1.set_title("Stage Preview")
    ax1.set_xlim(-stage.robot.radius, stage.x_size + stage.robot.radius)
    ax1.set_ylim(-stage.robot.radius, stage.y_size + stage.robot.radius)
    ax1.axis("off")
    ax1.set_aspect("equal", adjustable="box")

    # ステージの枠
    ax1.add_patch(
        patches.Rectangle(
            (0, 0),
            stage.x_size,
            stage.y_size,
            fill=None,
            edgecolor="black",
        )
    )

    # 壁の描画
    for wall in stage.walls:
        (x1, y1), (x2, y2) = wall
        ax1.plot(
            [x1, x2],
            [y1, y2],
            color="black",
            linewidth=5,
            solid_capstyle="butt",
        )

    # ゴールの描画
    for goal in stage.goals:
        x, y = goal.position
        width, height = goal.size
        ax1.add_patch(
            patches.Rectangle(
                (x, y),
                width,
                height,
                fill=True,
                color="green",
                alpha=0.5,
            )
        )
        ax1.text(
            x + width / 2,
            y + height / 2,
            str(goal.id),
            fontsize=20,
            ha="center",
            va="center",
        )

    animated: list[Artist] = []

    # 変化物の描画関数
    def update_artists(*_) -> list[Artist]:
        # 前フレームの描画を削除
        while animated:
            artist = animated.pop()
            artist.remove()

        # 経路の描画
        if stage.robot.path is not None:
            path = stage.robot.path
            lines = ax1.plot(
                path[:, 0],
                path[:, 1],
                color="red",
                linewidth=2,
                linestyle="--",
            )
            animated.extend(lines)

        # ロボットのプロパティ
        x, y = stage.robot.position
        radius = stage.robot.radius
        rotation = stage.robot.rotation

        # ロボットの円
        circle = patches.Circle(
            (x, y),
            radius,
            fill=True,
            color="blue",
        )
        animated.append(ax1.add_patch(circle))

        # ロボットの向きを示す矢印
        arrow_length = radius * 1.2
        arrow_dx = arrow_length * np.cos(rotation)
        arrow_dy = arrow_length * np.sin(rotation)
        arrow = patches.FancyArrow(
            x,
            y,
            arrow_dx,
            arrow_dy,
            width=10,
            length_includes_head=True,
            color="white",
        )
        animated.append(ax1.add_patch(arrow))

        # ロボットの中心点
        center_dot = patches.Circle(
            (x, y),
            radius * 0.1,
            color="red",
        )
        animated.append(ax1.add_patch(center_dot))

        return animated

    # 初期描画
    update_artists()

    def animate(frame: int) -> list[Artist]:
        stage.robot.tick()
        return update_artists()

    _ = FuncAnimation(
        fig,
        animate,
        frames=200,
        interval=100,
    )

    def on_click(event: Event) -> None:
        if (
            type(event) is MouseEvent
            and event.inaxes == ax1
            and event.xdata is not None
            and event.ydata is not None
        ):
            x, y = event.xdata, event.ydata
            stage.robot.destination = (x, y)

    fig.canvas.mpl_connect("button_press_event", on_click)

    # グリッドマップの表示
    ax2.set_title("Grid Map")
    grid = stage.grid_map
    ax2.imshow(
        grid, cmap="gray_r", origin="lower", extent=(0, stage.x_size, 0, stage.y_size)
    )
    ax2.set_aspect("equal", adjustable="box")
    ax2.set_xticks(np.arange(0, stage.x_size + 1, stage.cell_size * 2))
    ax2.set_yticks(np.arange(0, stage.y_size + 1, stage.cell_size * 2))
    ax2.axis("off")
    ax2.grid(which="both", color="lightgray", linewidth=0.5)

    plt.show()
