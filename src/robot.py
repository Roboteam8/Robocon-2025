from dataclasses import dataclass

import numpy as np


@dataclass
class Robot:
    """ロボットの情報を管理するクラス"""

    size: int  # ロボットのサイズ (diameter in mm)

    position: tuple[float, float]  # ロボットの位置 (x, y)
    rotation: float  # ロボットの向き (degrees)

    _MAX_STEERING_ANGLE = 45.0  # 最大操舵角度 (degrees)

    _r_speed = 0.0  # 右車輪の速度
    _l_speed = 0.0  # 左車輪の速度

    def pickup_box(self):
        """ロボットが箱を拾う動作をする関数"""
        pass

    def drop_box(self):
        """ロボットが箱を置く動作をする関数"""
        pass

    def read_ar_marker(self):
        """ARマーカーを読み取り、プロパティを更新する関数"""
        pass

    # こっから下適当に付けたやつなんで消してもいいです
    destination: tuple[float, float] | None = None  # ロボットの目的地 (Nullable)

    _rotation_speed: float = 15.0  # ロボットの回転速度 (degrees per tick)
    _movement_speed: float = 100.0  # ロボットの移動速度 (mm per tick)

    def tick(self):
        """ロボットの状態を更新する関数"""

        if self.destination is None:
            return  # 目的地が設定されていない場合は何もしない

        dest_x, dest_y = self.destination
        curr_x, curr_y = self.position

        # 目的地までの距離と角度を計算
        delta_x = dest_x - curr_x
        delta_y = dest_y - curr_y
        distance = (delta_x**2 + delta_y**2) ** 0.5
        target_angle = np.degrees(np.arctan2(delta_y, delta_x)) % 360

        # 現在の向きと目的地の角度の差を計算
        angle_diff = (target_angle - self.rotation + 180) % 360 - 180

        # 回転処理
        if abs(angle_diff) > 1e-2:  # 小さな誤差を無視
            rotation_step = np.sign(angle_diff) * min(
                self._rotation_speed, abs(angle_diff)
            )
            self.rotation = (self.rotation + rotation_step) % 360
            return  # 回転中は移動しない

        # 移動処理
        if distance > 1e-2:  # 小さな誤差を無視
            movement_step = min(self._movement_speed, distance)
            move_x = movement_step * np.cos(np.radians(self.rotation))
            move_y = movement_step * np.sin(np.radians(self.rotation))
            self.position = (curr_x + move_x, curr_y + move_y)

            # 目的地に到達したかチェック
            if movement_step >= distance:
                self.position = self.destination
                self.destination = None  # 目的地に到達したのでクリア
