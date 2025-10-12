from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

from pathfinding import find_path

if TYPE_CHECKING:
    from stage import Stage


@dataclass
class Robot:
    """ロボットの情報を管理するクラス"""

    position: tuple[float, float]  # ロボットの位置 (x, y)
    rotation: float  # ロボットの向き (rad)
    radius: float  # ロボットの半径
    destination: tuple[float, float] | None = None  # 目的地 (x, y)
    stage: Stage = field(init=False, repr=False)  # ロボットがいるステージ情報

    path: np.ndarray | None = field(default=None)  # 走行経路
    _path_index: int = 0  # 現在の経路インデックス

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
        if self.path is None and self.destination:
            # 経路が未設定で目的地がある場合、経路探索を行う
            path = find_path(self.stage, self.position, self.destination)
            if path is not None:
                self.path = path
                self._path_index = 0
            else:
                # 経路が見つからない場合、目的地をクリア
                self.destination = None
                return

        if self.path is None or self._path_index >= len(self.path):
            # 経路がないか、経路の終端に到達している場合、何もしない
            return

        # 次の目的地を取得
        target_pos = self.path[self._path_index]
        dest_x, dest_y = target_pos
        curr_x, curr_y = self.position

        # 目的地までの距離と角度を計算
        delta_x = dest_x - curr_x
        delta_y = dest_y - curr_y
        distance = np.hypot(delta_x, delta_y)
        target_angle = np.arctan2(delta_y, delta_x)
        angle_diff = (target_angle - self.rotation + np.pi) % (2 * np.pi) - np.pi

        # 回転処理
        if abs(angle_diff) > self._rotation_speed:
            self.rotation += np.sign(angle_diff) * self._rotation_speed
            self.rotation %= 2 * np.pi
            return

        # 前進処理
        move_dist = min(self._movement_speed, distance)
        if move_dist > 0:
            self.position = (
                curr_x + move_dist * np.cos(self.rotation),
                curr_y + move_dist * np.sin(self.rotation),
            )

        # 次の経路に移る処理
        if distance <= self._movement_speed:
            self._path_index += 1
            if self._path_index >= len(self.path):
                self.path = None
                self.destination = None
