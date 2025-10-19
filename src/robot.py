from dataclasses import dataclass

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from a_star import AStarPlanner
from visualize import Visualizable


@dataclass
class Robot(Visualizable):
    """ロボットの情報を管理するクラス"""

    position: tuple[float, float]  # ロボットの位置 (x, y)
    rotation: float  # ロボットの向き (rad)
    radius: float  # ロボットの半径

    _path: list[tuple[float, float]] | None = None  # 走行経路
    _path_index: int = 0  # 現在の経路インデックス

    def set_path(self, destination: tuple[float, float], planner: AStarPlanner) -> None:
        """目的地と経路計画オブジェクトを設定する関数"""
        self._path = planner.plan_path(self.position, destination)
        self._path_index = 0

    def pickup_box(self):
        """ロボットが箱を拾う動作をする関数"""
        pass

    def drop_box(self):
        """ロボットが箱を置く動作をする関数"""
        pass

    def read_ar_marker(self):
        """ARマーカーを読み取り、プロパティを更新する関数"""
        pass

    _rotation_speed: float = np.radians(15.0)  # ロボットの回転速度 (rad per tick)
    _movement_speed: float = 100.0  # ロボットの移動速度 (mm per tick)

    def tick(self):
        """ロボットの状態を更新する関数"""
        if self._path is None or self._path_index >= len(self._path):
            # 経路がないか、経路の終端に到達している場合、何もしない
            return

        target_x, target_y = self._path[self._path_index]
        current_x, current_y = self.position
        direction_vector = np.array([target_x - current_x, target_y - current_y])
        distance_to_target = np.linalg.norm(direction_vector)
        rotation_to_target = np.arctan2(direction_vector[1], direction_vector[0])
        rotation_diff = (rotation_to_target - self.rotation + np.pi) % (
            2 * np.pi
        ) - np.pi
        # 角度の更新
        if abs(rotation_diff) > self._rotation_speed:
            self.rotation += np.sign(rotation_diff) * self._rotation_speed
            self.rotation %= 2 * np.pi
        else:
            self.rotation = rotation_to_target
            # 位置の更新
            if distance_to_target > self._movement_speed:
                move_vector = (
                    direction_vector / distance_to_target * self._movement_speed
                )
                self.position = (
                    current_x + move_vector[0],
                    current_y + move_vector[1],
                )
            else:
                self.position = (target_x, target_y)
                self._path_index += 1

    def animate(self, ax: Axes) -> list[Artist]:
        x, y = self.position
        animated: list[Artist] = []
        # ロボットの円
        circle = Circle(
            (x, y),
            self.radius,
            fill=True,
            color="blue",
        )
        animated.append(ax.add_patch(circle))
        # ロボットの向きを示す矢印
        arrow_length = self.radius
        arrow_dx = arrow_length * np.cos(self.rotation)
        arrow_dy = arrow_length * np.sin(self.rotation)
        arrow = ax.arrow(
            x,
            y,
            arrow_dx,
            arrow_dy,
            width=5,
            length_includes_head=True,
            color="white",
        )
        animated.append(ax.add_patch(arrow))
        # ロボットの中心点
        center_dot = Circle(
            (x, y),
            self.radius * 0.1,
            color="red",
        )
        animated.append(ax.add_patch(center_dot))
        return animated
