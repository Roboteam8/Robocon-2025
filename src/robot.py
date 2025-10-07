from dataclasses import dataclass, field

import numpy as np


@dataclass
class Robot:
    """ロボットの情報を管理するクラス"""

    size: int  # ロボットのサイズ (diameter in mm)

    position: tuple[int, int]  # ロボットの位置 (x, y)
    rotation: float  # ロボットの向き (degrees)

    _MAX_STEERING_ANGLE = 45.0  # 最大操舵角度 (degrees)
    _MIN_TURNING_RADIUS: float = field(
        init=False
    )  # 最小回転半径 (mm), 初期値は0、__post_init__で計算

    _r_speed = 0.0  # 右車輪の速度
    _l_speed = 0.0  # 左車輪の速度

    def __post_init__(self):
        """初期化後に最小回転半径を計算"""
        if np.sin(np.radians(self._MAX_STEERING_ANGLE)) == 0:
            # 操舵角度が0の場合は無限大とする（直進のみ）
            self._MIN_TURNING_RADIUS = float("inf")
        else:
            # L / sin(α) で計算 (Lはホイールベース、ここではsize/2と仮定)
            wheelbase = self.size / 2
            self._MIN_TURNING_RADIUS = wheelbase / np.sin(
                np.radians(self._MAX_STEERING_ANGLE)
            )

    def pickup_box(self):
        """ロボットが箱を拾う動作をする関数"""
        pass

    def drop_box(self):
        """ロボットが箱を置く動作をする関数"""
        pass

    def read_ar_marker(self):
        """ARマーカーを読み取り、プロパティを更新する関数"""
        pass

    path: np.ndarray | None = field(default=None, repr=False)  # 走行経路
    _path_index: int = 0

    destination: tuple[float, float] | None = None  # ロボットの目的地 (Nullable)

    _rotation_speed: float = 15.0  # ロボットの回転速度 (degrees per tick)
    _movement_speed: float = 100.0  # ロボットの移動速度 (mm per tick)

    def tick(self):
        """ロボットの状態を更新する関数"""

        if self.path is None or self._path_index >= len(self.path):
            return  # 経路がない、または経路の終点に到達した場合は何もしない

        # 次の目的地を取得
        target_pos = self.path[self._path_index]
        dest_x, dest_y = target_pos
        curr_x, curr_y = self.position

        # 目的地までの距離と角度を計算
        delta_x = dest_x - curr_x
        delta_y = dest_y - curr_y
        distance = (delta_x**2 + delta_y**2) ** 0.5
        target_angle = np.degrees(np.arctan2(delta_y, delta_x)) % 360

        # 現在の向きと目的地の角度の差を計算
        angle_diff = (target_angle - self.rotation + 180) % 360 - 180

        # 回転処理
        if abs(angle_diff) > 5.0:  # 向きの誤差が5度以上なら回転
            rotation_step = np.sign(angle_diff) * min(
                self._rotation_speed, abs(angle_diff)
            )
            self.rotation = (self.rotation + rotation_step) % 360
        else:
            # 移動処理
            movement_step = min(self._movement_speed, distance)
            move_x = movement_step * np.cos(np.radians(self.rotation))
            move_y = movement_step * np.sin(np.radians(self.rotation))
            self.position = (curr_x + move_x, curr_y + move_y)

            # 次の目的地に近づいたらインデックスを進める
            if distance < self._movement_speed:
                self._path_index += 1

    def set_path(self, path: np.ndarray):
        """経路を設定する関数"""
        self.path = path
        self._path_index = 0
