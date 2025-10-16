from collections import deque
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
from scipy.ndimage import binary_dilation

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
    robot: Robot  # ステージ上のロボット
    grid_map: "GridMap" = field(init=False)  # グリッドマップ (0: 通行可能, 1: 障害物)

    def __post_init__(self):
        self.grid_map = GridMap(self, cell_size=100)


class GridMap(npt.NDArray[np.uint8]):
    """グリッドマップを表すクラス

    0: 通行可能
    1: 障害物
    """

    cell_size: int  # セルサイズ (mm)

    def __new__(cls, stage: "Stage", cell_size: int = 100) -> "GridMap":
        rows = (stage.y_size + cell_size - 1) // cell_size
        cols = (stage.x_size + cell_size - 1) // cell_size
        instance = super().__new__(cls, (rows, cols), dtype=np.uint8)
        instance.cell_size = cell_size
        instance[:] = np.zeros((rows, cols), dtype=np.uint8)

        for wall in stage.walls:
            (x1, y1), (x2, y2) = wall
            r1, c1 = int(y1 / cell_size), int(x1 / cell_size)
            r2, c2 = int(y2 / cell_size), int(x2 / cell_size)
            rr = np.linspace(r1, r2, max(abs(r2 - r1), abs(c2 - c1)) + 1, dtype=int)
            cc = np.linspace(c1, c2, max(abs(r2 - r1), abs(c2 - c1)) + 1, dtype=int)
            for r, c in zip(rr, cc):
                if 0 <= r < rows and 0 <= c < cols:
                    instance[r, c] = 1

        instance[0, :] = 1
        instance[-1, :] = 1
        instance[:, 0] = 1
        instance[:, -1] = 1

        instance._expand_obstacles(stage.robot.radius)
        return instance

    def _expand_obstacles(self, radius: float) -> None:
        """障害物を指定された半径分膨張させる関数

        Args:
            radius (float): 膨張させる半径 (mm)
        """

        struct_size = int(np.ceil(radius / self.cell_size))
        struct = np.zeros((2 * struct_size + 1, 2 * struct_size + 1), dtype=bool)
        for y in range(-struct_size, struct_size + 1):
            for x in range(-struct_size, struct_size + 1):
                if x**2 + y**2 <= struct_size**2:
                    struct[y + struct_size, x + struct_size] = True

        expanded = binary_dilation(self == 1, structure=struct).astype(np.uint8)
        self[:] = expanded

    def nearest_reachable_cell(
        self, position: tuple[float, float]
    ) -> tuple[int, int] | None:
        """指定された位置から最も近い通行可能なセルを見つける関数

        Args:
            position (tuple[float, float]): 位置 (x, y)
        Returns:
            tuple[int, int] | None: 最も近い通行可能なセルの座標 (x, y)、または見つからない場合はNone
        """
        x, y = position
        row = int(y / self.cell_size)
        col = int(x / self.cell_size)

        if self[row, col] == 0:
            return (row, col)  # 指定位置が通行可能ならそのまま返す

        visited = set()
        queue = deque([(row, col)])
        directions = [
            (0, 1),
            (1, 0),
            (0, -1),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]
        while queue:
            curr_row, curr_col = queue.popleft()
            if (curr_row, curr_col) in visited:
                continue
            visited.add((curr_row, curr_col))

            if self[curr_row, curr_col] == 0:
                return (curr_row, curr_col)

            for dr, dc in directions:
                nr, nc = curr_row + dr, curr_col + dc
                if (
                    0 <= nc < self.shape[1]
                    and 0 <= nr < self.shape[0]
                    and (nr, nc) not in visited
                ):
                    queue.append((nr, nc))
        return None
