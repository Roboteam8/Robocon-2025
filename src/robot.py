from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt


@dataclass
class Robot:
    """ロボットの情報を管理するクラス"""

    position: tuple[float, float]  # ロボットの位置 (x, y)
    rotation: float  # ロボットの向き (rad)
    radius: float  # ロボットの半径

    _path: npt.NDArray[np.float64] | None = field(default=None)  # 走行経路
    _path_index: int = 0  # 現在の経路インデックス

    @property
    def path(self) -> npt.NDArray[np.float64] | None:
        """ロボットの現在の走行経路を取得するプロパティ"""
        return self._path

    @path.setter
    def path(self, path: npt.NDArray[np.float64]) -> None:
        """ロボットの走行経路を設定するプロパティセッター"""
        self._path = path
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

        # 次の目的地を取得
        target_pos = self._path[self._path_index]
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
