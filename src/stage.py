from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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

    x_size: int  # ステージのx方向サイズ (mm)
    y_size: int  # ステージのy方向サイズ (mm)
    walls: list[
        tuple[tuple[int, int], tuple[int, int]]
    ]  # 壁のリスト [((x1, y1), (x2, y2)), ...]
    goals: list[Goal]  # ゴールのリスト
    robot: Robot
