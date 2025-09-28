from dataclasses import dataclass

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from src.robot import Robot


@dataclass
class Goal:
    """ゴールの情報を管理するクラス"""

    position: tuple[int, int]  # ゴールの位置 (x, y)
    size: tuple[int, int]  # ゴールのサイズ (width, height)
    id: int  # ゴールのID


@dataclass
class Stage:
    """ステージの情報を管理するクラス"""

    width: int  # ステージの横幅 (mm)
    height: int  # ステージの奥行 (mm)
    wall: tuple[tuple[int, int], tuple[int, int]]  # 壁の位置 ((x1, y1), (x2, y2))
    goals: list[Goal]  # ゴールのリスト

    robot: Robot | None = None  # ロボット (初期値はNone)

    def preview_stage(self):
        """ステージのプレビューを表示する関数"""

        # 描画の準備
        ax = plt.axes()

        # ステージの枠を描画
        ax.add_patch(
            patches.Rectangle(
                (0, 0), self.width, self.height, fill=None, edgecolor="black"
            )
        )

        # 壁を描画
        (x1, y1), (x2, y2) = self.wall
        ax.plot([x1, x2], [y1, y2], color="black", linewidth=5)

        # ゴールを描画
        for goal in self.goals:
            gx, gy = goal.position
            gw, gh = goal.size
            ax.add_patch(
                patches.Rectangle(
                    (gx - gw / 2, gy - gh / 2), gw, gh, fill=True, color="green"
                )
            )
            ax.text(gx, gy, f"Goal {goal.id}", color="white", ha="center", va="center")

        # ロボットを描画
        if self.robot:
            rx, ry = self.robot.position
            size = self.robot.size
            ax.add_patch(patches.Circle((rx, ry), radius=size, fill=True, color="blue"))
            ax.text(rx, ry, "Robot", color="white", ha="center", va="center")

        # 見た目の調整
        ax.set_xlim(-50, self.width + 50)
        ax.set_ylim(-50, self.height + 50)
        ax.set_aspect("equal", adjustable="box")

        plt.title("Stage Preview")
        plt.xlabel("X (mm)")
        plt.ylabel("Y (mm)")
        plt.show()
