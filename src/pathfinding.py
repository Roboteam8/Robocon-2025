from collections import deque

import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from matplotlib.colors import ListedColormap

from stage import Stage
from visualize import Visualizable


class PathPlanner(Visualizable):
    """
    グリッドマップ上でA*アルゴリズムによる経路計画を行うクラス
    Attributes:
        stage (Stage): ステージオブジェクト
        grid_map (npt.NDArray[np.uint8]): グリッドマップ (0: 空き, 1: 障害物)
    """

    stage: Stage
    grid_map: npt.NDArray[np.uint8]

    def __init__(self, stage: Stage, cell_size: int) -> None:
        """
        グリッドマップを初期化し、ステージの障害物情報を設定

        Args:
            stage (Stage): ステージオブジェクト
            cell_size (int): グリッドの1マスのサイズ（mm）
        """
        self.stage = stage
        # グリッドマップの初期化
        shape = stage.y_size // cell_size, stage.x_size // cell_size
        self.grid_map = np.zeros(shape, dtype=np.uint8)

        # ステージの外壁をグリッドマップに設定
        self.grid_map[:, 0] = 1
        self.grid_map[:, -1] = 1
        self.grid_map[0, :] = 1
        self.grid_map[-1, :] = 1

        # 壁をグリッドマップに設定
        for wall in stage.walls:
            x1, y1 = wall.start
            x2, y2 = wall.end

            dx = x2 - x1
            dy = y2 - y1
            steps = max(abs(dx), abs(dy)) // cell_size + 1

            for step in range(steps):
                t = step / steps
                x = int(x1 + t * dx)
                y = int(y1 + t * dy)
                cell_x = x // cell_size
                cell_y = y // cell_size
                self.grid_map[cell_y, cell_x] = 1

        pre_expanded = self.grid_map.copy()
        expansion_radius = stage.robot.radius
        cell_radius = int(expansion_radius // cell_size)
        # 障害物の拡張
        for y in range(self.grid_map.shape[0]):
            for x in range(self.grid_map.shape[1]):
                if pre_expanded[y, x] == 1:
                    for dy in range(-cell_radius, cell_radius + 1):
                        for dx in range(-cell_radius, cell_radius + 1):
                            if (
                                0 <= x + dx < self.grid_map.shape[1]
                                and 0 <= y + dy < self.grid_map.shape[0]
                                and dx * dx + dy * dy <= cell_radius * cell_radius
                            ):
                                self.grid_map[y + dy, x + dx] = 1

    def plan_path(
        self, start: tuple[float, float], goal: tuple[float, float]
    ) -> list[tuple[float, float]] | None:
        """
        A*アルゴリズムで経路を計画するメソッド

        Args:
            start (tuple[float, float]): スタート位置 (x, y)
            goal (tuple[float, float]): ゴール位置 (x, y)

        Returns:
            list[tuple[float, float]] | None: 経路点のリスト or None
        """
        start_cell = self._nearest_free_cell(start)
        goal_cell = self._nearest_free_cell(goal)

        if start_cell is None or goal_cell is None:
            return None

        path_cells = self._a_star_search(start_cell, goal_cell)
        if path_cells is not None:
            path_world = []
            for cell in path_cells:
                x, y = cell
                world_x = (x + 0.5) * (self.stage.x_size / self.grid_map.shape[1])
                world_y = (y + 0.5) * (self.stage.y_size / self.grid_map.shape[0])
                path_world.append((world_x, world_y))
            return path_world

        return None  # 経路が見つからなかった場合

    def _a_star_search(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        """
        A*アルゴリズムで経路を検索するメソッド

        Args:
            start (tuple[int, int]): スタートセルの座標 (cell_x, cell_y)
            goal (tuple[int, int]): ゴールセルの座標 (cell_x, cell_y)

        Returns:
            list[tuple[int, int]] | None: 経路点のリスト or None
        """
        open_set: set[tuple[int, int]] = set()
        closed_set: set[tuple[int, int]] = set()
        came_from: dict[tuple[int, int], tuple[int, int]] = {}

        g_score = {start: 0}
        f_score = {start: self._heuristic(start, goal)}

        open_set.add(start)

        while open_set:
            current = min(open_set, key=lambda cell: f_score.get(cell, float("inf")))

            if current == goal:
                return self._reconstruct_path(came_from, current)

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
                f_score[neighbor] = tentative_g_score + self._heuristic(neighbor, goal)

        return None  # 経路が見つからなかった場合

    def _nearest_free_cell(
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
        cell_x = int(x // (self.stage.x_size / self.grid_map.shape[1]))
        cell_y = int(y // (self.stage.y_size / self.grid_map.shape[0]))

        if self.grid_map[cell_y, cell_x] == 0:
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
                    0 <= nx < self.grid_map.shape[1]
                    and 0 <= ny < self.grid_map.shape[0]
                    and (nx, ny) not in visited
                ):
                    if self.grid_map[ny, nx] == 0:
                        return nx, ny
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return None

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
        current_node: tuple[int, int],
    ) -> list[tuple[int, int]]:
        """
        経路復元

        Args:
            came_from (dict[tuple[int, int], tuple[int, int]]): ノードの遷移元情報
            current_node (tuple[int, int]): ゴールノード

        Returns:
            list[tuple[int, int]]: 経路点のリスト
        """
        path = []
        while current_node in came_from:
            path.append(current_node)
            current_node = came_from[current_node]
        path.append(current_node)
        return path[::-1]  # 逆順にして返す

    def visualize(self, ax: Axes) -> None:
        ax.imshow(
            self.grid_map,
            cmap=ListedColormap([(0, 0, 0, 0), (0, 0, 0, 1)]),
            origin="lower",
            extent=(
                0,
                self.stage.x_size,
                0,
                self.stage.y_size,
            ),
            alpha=0.5,
            zorder=10,
        )
