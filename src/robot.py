from dataclasses import dataclass


@dataclass
class Robot:
    """ロボットの情報を管理するクラス"""

    position: tuple[int, int]  # ロボットの位置 (x, y)
    orientation: float  # ロボットの向き (degrees)
    size: int  # ロボットのサイズ (diameter in mm)
