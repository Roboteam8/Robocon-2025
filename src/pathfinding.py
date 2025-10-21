from collections import deque

import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from matplotlib.colors import ListedColormap
from scipy.interpolate import BSpline

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
    cell_size: int

    def __init__(self, stage: Stage, cell_size: int) -> None:
        """
        グリッドマップを初期化し、ステージの障害物情報を設定

        Args:
            stage (Stage): ステージオブジェクト
            cell_size (int): グリッドの1マスのサイズ（mm）
        """
        self.stage = stage
        self.cell_size = cell_size
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
    ) -> npt.NDArray[np.float64] | None:
        """
        A*アルゴリズムで経路を計画するメソッド

        Args:
            start (tuple[float, float]): スタート位置 (x, y)
            goal (tuple[float, float]): ゴール位置 (x, y)

        Returns:
            npt.NDArray[np.float64] | None: 経路点のリスト or None
        """
        start_cell = self._nearest_free_cell(start)
        goal_cell = self._nearest_free_cell(goal)

        if start_cell is None or goal_cell is None:
            return None

        cell_path = self._a_star_search(start_cell, goal_cell)
        if cell_path is not None:
            # グリッドセル座標をワールド座標に変換
            world_path = np.array(
                [self._cell_to_world((cell_x, cell_y)) for cell_x, cell_y in cell_path],
                dtype=np.float64,
            )
            # 経路の平滑化
            smooth_path = self._smooth_path(world_path)
            return smooth_path

        return None  # 経路が見つからなかった場合

    def _a_star_search(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> npt.NDArray[np.int32] | None:
        """
        A*アルゴリズムで経路を検索するメソッド

        Args:
            start (tuple[int, int]): スタートセルの座標 (cell_x, cell_y)
            goal (tuple[int, int]): ゴールセルの座標 (cell_x, cell_y)

        Returns:
            npt.NDArray[np.int32] | None: 経路点の配列 or None
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
        cell_x, cell_y = self._world_to_cell(position)

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

    def _world_to_cell(self, position: tuple[float, float]) -> tuple[int, int]:
        """
        ワールド座標をグリッドセル座標に変換するメソッド

        Args:
            position (tuple[float, float]): 位置 (x, y)

        Returns:
            tuple[int, int]: グリッドセルの座標 (cell_x, cell_y)
        """
        x, y = position
        cell_x = np.ceil(x / self.cell_size).astype(int)
        cell_y = np.ceil(y / self.cell_size).astype(int)
        return cell_x, cell_y

    def _cell_to_world(self, cell: tuple[int, int]) -> tuple[float, float]:
        """
        グリッドセル座標をワールド座標に変換するメソッド

        Args:
            cell (tuple[int, int]): グリッドセルの座標 (cell_x, cell_y)

        Returns:
            tuple[float, float]: 位置 (x, y)
        """
        cell_x, cell_y = cell
        x = (cell_x + 0.5) * self.cell_size
        y = (cell_y + 0.5) * self.cell_size
        return x, y

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
    ) -> npt.NDArray[np.int32]:
        """
        経路復元

        Args:
            came_from (dict[tuple[int, int], tuple[int, int]]): ノードの遷移元情報
            current_node (tuple[int, int]): ゴールノード

        Returns:
            npt.NDArray[np.float64]: 経路点の配列
        """
        total_path: list[tuple[int, int]] = [current_node]
        while current_node in came_from:
            current_node = came_from[current_node]
            total_path.append(current_node)
        total_path.reverse()
        return np.array(total_path, dtype=np.int32)

    def _smooth_path(self, path: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """
        B-スプライン補間による経路の平滑化
        Args:
            path (npt.NDArray[np.float64]): 元の経路点の配列
        Returns:
            npt.NDArray[np.float64]: 平滑化された経路点の配列
        """
        if len(path) < 4:
            return path

        # 制御点数を減らしてスプラインを強くかける
        n_reduced = max(4, len(path) // 2)
        idx = np.linspace(0, len(path) - 1, n_reduced).astype(int)
        path = path[idx]

        # B-スプラインのパラメータ設定
        degree = 3
        n_control_points = len(path)
        n_knots = n_control_points + degree + 1

        # ノットベクトルの生成
        knots = np.zeros(n_knots)
        knots[degree : n_knots - degree] = np.linspace(0, 1, n_knots - 2 * degree)
        knots[n_knots - degree :] = 1

        # B-スプラインの生成
        spline_x = BSpline(knots, path[:, 0], degree)
        spline_y = BSpline(knots, path[:, 1], degree)

        # 補間点の生成
        n_points = max(2 * n_control_points, 100)
        t_values = np.linspace(0, 1, n_points)
        smooth_path = np.vstack((spline_x(t_values), spline_y(t_values))).T

        return smooth_path

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
