from collections import deque
from dataclasses import dataclass
from typing import Self

import numpy as np
import numpy.typing as npt
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.colors import ListedColormap

from stage import Stage
from visualize import Visualizable


class GridMap(Visualizable, npt.NDArray[np.uint8]):
    """
    ステージの障害物をグリッドマップとして表現するクラス

    Attributes:
        cell_size (int): グリッドの1マスのサイズ（mm）
    """

    cell_size: int

    def __new__(
        cls,
        stage: Stage,
        cell_size: int,
        expansion_radius: int = 0,
    ) -> Self:
        x_cells = stage.x_size // cell_size
        y_cells = stage.y_size // cell_size
        instance = np.zeros((y_cells, x_cells), dtype=np.uint8).view(cls)

        instance.cell_size = cell_size
        instance._set_obstacles(stage)
        instance._expand_obstacles(expansion_radius)

        return instance

    def _set_obstacles(self, stage: Stage) -> None:
        """
        ステージの障害物情報をグリッドマップに設定するメソッド

        Args:
            stage (Stage): ステージオブジェクト
        """
        # ステージの外壁
        self[:, 0] = 1
        self[:, -1] = 1
        self[0, :] = 1
        self[-1, :] = 1

        # 壁
        for wall in stage.walls:
            x1, y1 = wall.start
            x2, y2 = wall.end

            dx = x2 - x1
            dy = y2 - y1
            steps = max(abs(dx), abs(dy)) // self.cell_size + 1

            for step in range(steps):
                t = step / steps
                x = int(x1 + t * dx)
                y = int(y1 + t * dy)
                cell_x = x // self.cell_size
                cell_y = y // self.cell_size
                self[cell_y, cell_x] = 1

    def _expand_obstacles(self, radius: int) -> None:
        if radius <= 0:
            return

        # 障害物の拡張
        pre_expanded = self.copy()
        for y in range(self.shape[0]):
            for x in range(self.shape[1]):
                if pre_expanded[y, x] == 1:
                    for dy in range(-radius, radius + 1):
                        for dx in range(-radius, radius + 1):
                            if abs(dy) + abs(dx) <= radius:
                                ny, nx = y + dy, x + dx
                                if 0 <= ny < self.shape[0] and 0 <= nx < self.shape[1]:
                                    self[ny, nx] = 1

    def visualize(self, ax: Axes) -> None:
        ax.imshow(
            self,
            cmap=ListedColormap([(0, 0, 0, 0), "black"]),
            origin="lower",
            extent=(
                0,
                self.shape[1] * self.cell_size,
                0,
                self.shape[0] * self.cell_size,
            ),
            alpha=0.5,
            zorder=10,
        )

    def nearest_free_cell(
        self, position: tuple[float, float]
    ) -> tuple[int, int] | None:
        """
        指定された位置から最も近い空きセルの座標を取得するメソッド

        Args:
            position (tuple[float, float]): 位置 (x, y)

        Returns:
            tuple[int, int] | None: 最も近い空きセルの座標 (cell_x, cell_y) または None
        """
        x, y = position
        cell_x = int(x // self.cell_size)
        cell_y = int(y // self.cell_size)

        if self[cell_y, cell_x] == 0:
            return cell_x, cell_y

        # BFSで最も近い空きセルを探索
        visited = set()
        queue = deque([(cell_x, cell_y)])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        while queue:
            cx, cy = queue.popleft()
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < self.shape[1]
                    and 0 <= ny < self.shape[0]
                    and (nx, ny) not in visited
                ):
                    if self[ny, nx] == 0:
                        return nx, ny
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return None


@dataclass
class PathCalculator(Visualizable, list[tuple[float, float]]):
    """
    グリッドマップ上で経路計画を行うクラス

    Attributes:
        grid_map (GridMap): グリッドマップオブジェクト
    """

    grid_map: GridMap
    start: tuple[float, float]
    goal: tuple[float, float]

    def calculate_path(self) -> None:
        """
        グリッドマップ上でA*アルゴリズムを用いて経路計画を行うメソッド
        """
        start_cell = self.grid_map.nearest_free_cell(self.start)
        goal_cell = self.grid_map.nearest_free_cell(self.goal)

        if start_cell is None or goal_cell is None:
            self.clear()
            return

        # A*アルゴリズムの実装
        open_set = set()
        closed_set = set()
        came_from = {}

        g_score = {start_cell: 0}
        f_score = {start_cell: self._heuristic(start_cell, goal_cell)}

        open_set.add(start_cell)

        while open_set:
            current = min(open_set, key=lambda cell: f_score.get(cell, float("inf")))

            if current == goal_cell:
                self._reconstruct_path(came_from, current)
                return

            open_set.remove(current)
            closed_set.add(current)

            for neighbor in self._get_neighbors(current):
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_score[current] + 1

                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score.get(neighbor, float("inf")):
                    continue

                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + self._heuristic(
                    neighbor, goal_cell
                )

        self.clear()  # 経路が見つからなかった場合

    def _heuristic(self, cell1: tuple[int, int], cell2: tuple[int, int]) -> float:
        """
        ヒューリスティック関数（マンハッタン距離）

        Args:
            cell1 (tuple[int, int]): セル1の座標 (cell_x, cell_y)
            cell2 (tuple[int, int]): セル2の座標 (cell_x, cell_y)

        Returns:
            float: ヒューリスティック値
        """
        return abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1])

    def _get_neighbors(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
        """
        指定されたセルの隣接セルを取得するメソッド

        Args:
            cell (tuple[int, int]): セルの座標 (cell_x, cell_y)

        Returns:
            list[tuple[int, int]]: 隣接セルのリスト
        """
        x, y = cell
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < self.grid_map.shape[1]
                and 0 <= ny < self.grid_map.shape[0]
                and self.grid_map[ny, nx] == 0
            ):
                neighbors.append((nx, ny))
        return neighbors

    def _reconstruct_path(
        self,
        came_from: dict[tuple[int, int], tuple[int, int]],
        current: tuple[int, int],
    ) -> None:
        """
        経路を再構築するメソッド

        Args:
            came_from (dict): 各セルの親セルの辞書
            current (tuple[int, int]): 現在のセルの座標 (cell_x, cell_y)
        """
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        total_path.reverse()

        # グリッドセル座標を実座標に変換
        self = [
            (
                cell[0] * self.grid_map.cell_size + self.grid_map.cell_size / 2,
                cell[1] * self.grid_map.cell_size + self.grid_map.cell_size / 2,
            )
            for cell in total_path
        ]

    def animate(self, ax: Axes) -> list[Artist]:
        x_coords = [pos[0] for pos in self]
        y_coords = [pos[1] for pos in self]
        line = ax.plot(
            x_coords,
            y_coords,
            color="red",
            linewidth=2,
            linestyle="--",
            label="Planned Path",
        )
        return [*line]
