from dataclasses import dataclass

import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.artist import Artist

from robot import Robot


@dataclass
class Goal:
    """ゴールの情報を管理するクラス"""

    position: tuple[int, int]  # ゴールの位置(左下基準) (x, y)
    size: tuple[int, int]  # ゴールのサイズ (x幅, y幅)
    id: int  # ゴールのID


@dataclass
class Stage:
    """ステージの情報を管理するクラス"""

    width: int  # ステージの横幅 (mm)
    depth: int  # ステージの奥行 (mm)
    wall: tuple[tuple[int, int], tuple[int, int]]  # 壁の位置 ((x1, y1), (x2, y2))
    goals: list[Goal]  # ゴールのリスト

    robot: Robot | None = None  # ロボット (Nullable)

    def preview_stage(self):
        """ステージのプレビューを表示する関数"""

        # 描画の準備
        ax = plt.axes()

        # ステージの枠を描画
        ax.add_patch(
            patches.Rectangle(
                (0, 0), self.width, self.depth, fill=None, edgecolor="black", zorder=10
            )
        )

        # ゴールを描画
        for goal in self.goals:
            px, py = goal.position
            sx, sy = goal.size
            ax.add_patch(patches.Rectangle((px, py), sx, sy, fill=True, color="green"))
            ax.text(
                px + sx // 2,
                py + sy // 2,
                f"Goal {goal.id}",
                color="white",
                ha="center",
                va="center",
            )

        # 壁を描画
        (x1, y1), (x2, y2) = self.wall
        ax.add_patch(
            patches.Rectangle(
                (x1, y1),
                x2 - x1,
                y2 - y1,
                edgecolor="brown",
                facecolor="saddlebrown",
            )
        )

        robot_artists: list[Artist] = []

        # ロボットの描画関数
        def draw_robot():
            if self.robot is None:
                return

            rx, ry = self.robot.position
            rsize = self.robot.size
            rrot = self.robot.rotation

            # ロボットの円を描画
            robot_circle = patches.Circle(
                (rx, ry), rsize / 2, fill=True, color="blue", zorder=20
            )
            ax.add_patch(robot_circle)
            robot_artists.append(robot_circle)

            # ロボットの向きを示す線を描画
            line_length = rsize / 2
            line_dx = line_length * np.cos(np.radians(rrot))
            line_dy = line_length * np.sin(np.radians(rrot))
            direction_line = patches.FancyArrow(
                rx,
                ry,
                line_dx,
                line_dy,
                width=5,
                length_includes_head=True,
                color="white",
                zorder=25,
            )
            ax.add_patch(direction_line)
            robot_artists.append(direction_line)

            # ロボットの位置と向きをテキストで表示
            info_text = ax.text(
                rx,
                ry - rsize / 2 - 20,
                f"Pos: ({int(rx)}, {int(ry)})\nRot: {int(rrot)}°",
                color="black",
                ha="center",
                va="top",
                zorder=30,
            )
            robot_artists.append(info_text)

        # ロボットを初回描画
        draw_robot()

        # アニメーション関数
        def tick(frame):
            if self.robot is None:
                return []

            # ロボットの状態を更新
            self.robot.tick()

            # 既存のロボット描画を削除
            for artist in robot_artists:
                artist.remove()
            robot_artists.clear()

            # ロボットを再描画
            draw_robot()

            return robot_artists

        # アニメーションの設定
        ani = animation.FuncAnimation(plt.gcf(), tick, frames=200, interval=100)

        # クリックイベントの設定
        def on_click(event):
            if self.robot is None:
                return
            if event.inaxes != ax:
                return
            # クリック位置を目的地に設定
            self.robot.destination = (event.xdata, event.ydata)

        plt.gcf().canvas.mpl_connect("button_press_event", on_click)

        # 見た目の調整
        ax.set_aspect("equal", adjustable="box")
        plt.title("Stage Preview")
        plt.xlim(-500, self.width + 500)
        plt.ylim(-500, self.depth + 500)
        plt.axis("off")
        plt.grid()

        plt.show()
