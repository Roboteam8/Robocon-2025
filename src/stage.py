from collections import deque
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

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
    cell_size: int = 100  # グリッドマップのセルサイズ (mm)
    grid_map: npt.NDArray[np.uint8] = field(
        init=False
    )  # グリッドマップ (0: 通行可能, 1: 障害物)

    def __post_init__(self):
        self.grid_map = self._create_grid_map()

        self.robot.stage = self

    def _create_grid_map(self) -> npt.NDArray[np.uint8]:
        """ステージ情報からグリッドマップを作成する関数"""
        grid_rows = np.ceil(self.y_size / self.cell_size).astype(int)
        grid_cols = np.ceil(self.x_size / self.cell_size).astype(int)
        grid = np.zeros((grid_rows, grid_cols), dtype=np.uint8)

        # 外枠を障害物として設定
        grid[0, :] = 1
        grid[-1, :] = 1
        grid[:, 0] = 1
        grid[:, -1] = 1

        # 壁を障害物としてグリッドマップに設定
        for wall in self.walls:
            (x1, y1), (x2, y2) = wall
            start_x, end_x = sorted(
                (int(x1 / self.cell_size), int(x2 / self.cell_size))
            )
            start_y, end_y = sorted(
                (int(y1 / self.cell_size), int(y2 / self.cell_size))
            )

            for y in range(max(0, start_y), min(grid_rows, end_y + 1)):
                for x in range(max(0, start_x), min(grid_cols, end_x + 1)):
                    grid[y, x] = 1

        # 障害物をロボットサイズを考慮して膨張させる
        robot_radius_cells = int(np.ceil(self.robot.radius / self.cell_size))
        expanded_grid = np.copy(grid)
        for y in range(grid_rows):
            for x in range(grid_cols):
                if grid[y, x] == 1:
                    for dy in range(-robot_radius_cells, robot_radius_cells + 1):
                        for dx in range(-robot_radius_cells, robot_radius_cells + 1):
                            nx, ny = x + dx, y + dy
                            if (
                                0 <= nx < grid_cols
                                and 0 <= ny < grid_rows
                                and dx**2 + dy**2 <= robot_radius_cells**2
                            ):
                                expanded_grid[ny, nx] = 1

        return expanded_grid

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

        if self.grid_map[row, col] == 0:
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

            if self.grid_map[curr_row, curr_col] == 0:
                return (curr_row, curr_col)

            for dr, dc in directions:
                nr, nc = curr_row + dr, curr_col + dc
                if (
                    0 <= nc < self.grid_map.shape[1]
                    and 0 <= nr < self.grid_map.shape[0]
                    and (nr, nc) not in visited
                ):
                    queue.append((nr, nc))
        return None
