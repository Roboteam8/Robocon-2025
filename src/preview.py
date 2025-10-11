import numpy as np
from matplotlib import patches
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist

from pathfinding import find_path
from stage import Stage


def preview(stage: Stage) -> None:
    """
    ステージのプレビューを表示する関数

    Args:
        stage (Stage): ステージの情報
    Returns:
        None
    """
    fig, ax = plt.subplots()

    # グローバル設定
    plt.title("Stage Preview")

    # 軸の設定
    ax.set_xlim(-500, stage.x_size + 500)
    ax.set_ylim(-500, stage.y_size + 500)
    ax.axis("off")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, which="both", linestyle="--", color="lightgray", zorder=1000)

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
            )
        )
        ax.text(
            x + width / 2,
            y + height / 2,
            str(goal.id),
            fontsize=20,
            ha="center",
            va="center",
        )

    animated: list[Artist] = []

    # 変化物の描画関数
    def update(*_) -> list[Artist]:
        # 前フレームの描画を削除
        while animated:
            artist = animated.pop()
            artist.remove()

        stage.robot.tick()

        # 経路の描画
        if stage.robot.path is not None:
            path = stage.robot.path
            lines = ax.plot(
                path[:, 0],
                path[:, 1],
                color="red",
                linewidth=2,
                linestyle="--",
            )
            animated.extend(lines)

        # ロボットのプロパティ
        x, y = stage.robot.position
        size = stage.robot.size
        radius = size / 2
        angle_rad = np.deg2rad(stage.robot.rotation)

        # ロボットの円
        circle = patches.Circle(
            (x, y),
            radius,
            fill=True,
            color="blue",
        )
        animated.append(ax.add_patch(circle))

        # ロボットの向きを示す矢印
        arrow_length = radius * 1.2
        arrow_dx = arrow_length * np.cos(angle_rad)
        arrow_dy = arrow_length * np.sin(angle_rad)
        arrow = patches.FancyArrow(
            x,
            y,
            arrow_dx,
            arrow_dy,
            width=size * 0.05,
            length_includes_head=True,
            color="white",
            head_width=size * 0.1,
            head_length=size * 0.1,
        )
        animated.append(ax.add_patch(arrow))

        # ロボットの中心点
        center_dot = patches.Circle(
            (x, y),
            size * 0.05,
            color="red",
        )
        animated.append(ax.add_patch(center_dot))

        # ロボットの座標と角度表示
        info_text = f"Pos: ({x}, {y})\nAngle: {stage.robot.rotation:.1f}°"
        text_artist = ax.text(
            stage.x_size + 100,
            stage.y_size / 2,  # ステージの右側に表示
            info_text,
            fontsize=8,
            ha="left",
            va="center",
        )
        animated.append(text_artist)

        return animated

    # 初期描画
    update()

    _ = FuncAnimation(
        fig,
        update,
        frames=200,
        interval=100,
    )

    def on_click(event) -> None:
        if event.inaxes != ax:
            return
        if event.button == 1:  # 左クリックで目的地設定
            dest_x = event.xdata
            dest_y = event.ydata
            if 0 <= dest_x <= stage.x_size and 0 <= dest_y <= stage.y_size:
                path = find_path(stage, stage.robot.position, (dest_x, dest_y))
                if path is not None:
                    stage.robot.set_path(path)
                update()
                plt.draw()
        elif event.button == 3:  # 右クリックで経路クリア
            stage.robot.path = None
            update()
            plt.draw()

    fig.canvas.mpl_connect("button_press_event", on_click)

    plt.show()
