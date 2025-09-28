from dataclasses import dataclass

import matplotlib.patches as patches
import matplotlib.pyplot as plt

from src.robot import Robot


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
                (0, 0), self.width, self.depth, fill=None, edgecolor="black"
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

        # ロボットを描画
        if self.robot:
            rx, ry = self.robot.position
            size = self.robot.size
            ax.add_patch(
                patches.Circle(
                    (rx, ry),
                    radius=size // 2,
                    fill=True,
                    edgecolor="blue",
                )
            )
            ax.text(rx, ry, "Robot", color="white", ha="center", va="center")

        # 見た目の調整
        ax.set_aspect("equal", adjustable="box")
        plt.title("Stage Preview")
        plt.xlim(-500, self.width + 500)
        plt.ylim(-500, self.depth + 500)
        plt.axis("off")
        plt.grid()

        plt.show()
