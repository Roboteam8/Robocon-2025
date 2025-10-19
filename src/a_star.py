import heapq
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes

from visualize import Visualizable


@dataclass
class AStarPlanner(Visualizable):
    stage_size: tuple[int, int]  # ステージサイズ (mm) (width, height)
    cell_size: int  # グリッドセルのサイズ (mm)
    obstacle_expansion: int = 0  # 障害物拡張半径 (mm)

    grid_shape: tuple[int, int] = field(init=False)  # グリッドの個数 (cols, rows)
    grid_map: np.ndarray[tuple[int, int], np.dtype[np.uint8]] = field(
        init=False
    )  # グリッドマップ (0: free, 1: obstacle)

    def __post_init__(self):
        self.grid_shape = (
            self.stage_size[0] // self.cell_size,
            self.stage_size[1] // self.cell_size,
        )
        self.grid_map = np.zeros(self.grid_shape, dtype=int)  # 0: free, 1: obstacle

    def set_obstacles(
        self, obstacles: list[tuple[tuple[int, int], tuple[int, int]]]
    ) -> None:
        """
        障害物をグリッドマップに設定する

        Args:
            obstacles (list[tuple[tuple[int, int], tuple[int, int]]]): 障害物リスト [((x1, y1), (x2, y2)), ...]
        """
        for (x1, y1), (x2, y2) in obstacles:
            grid_x1 = max(0, (x1 - self.obstacle_expansion) // self.cell_size)
            grid_y1 = max(0, (y1 - self.obstacle_expansion) // self.cell_size)
            grid_x2 = min(
                self.grid_shape[0] - 1,
                (x2 + self.obstacle_expansion) // self.cell_size,
            )
            grid_y2 = min(
                self.grid_shape[1] - 1,
                (y2 + self.obstacle_expansion) // self.cell_size,
            )

            self.grid_map[grid_y1 : grid_y2 + 1, grid_x1 : grid_x2 + 1] = 1

    def plan_path(
        self, start_world: tuple[float, float], goal_world: tuple[float, float]
    ) -> list[tuple[float, float]] | None:
        """
        A*アルゴリズムで経路を計画する

        Args:
            start_world (tuple[float, float]): (x, y) スタート座標
            goal_world (tuple[float, float]): (x, y) ゴール座標

        Returns:
            list[tuple[float, float]] | None: 経路点のリスト or None
        """
        # ワールド座標をグリッド座標に変換
        start_node = (
            int(start_world[1] / self.cell_size),
            int(start_world[0] / self.cell_size),
        )
        goal_node = (
            int(goal_world[1] / self.cell_size),
            int(goal_world[0] / self.cell_size),
        )

        # スタート/ゴールが障害物上にある場合、一番近いセルを探す
        if self.obstacle_map[start_node] == 1:
            nearest_start = self._find_nearest_free_cell(start_node)
            if nearest_start is None:
                return None
            start_node = nearest_start
        if self.obstacle_map[goal_node] == 1:
            nearest_goal = self._find_nearest_free_cell(goal_node)
            if nearest_goal is None:
                return None
            goal_node = nearest_goal

        open_set: list[tuple[float, tuple[int, int]]] = []
        heapq.heappush(open_set, (0.0, start_node))  # (f_cost, node)

        came_from: dict[tuple[int, int], tuple[int, int]] = {}
        g_cost: dict[tuple[int, int], float] = {start_node: 0}

        while open_set:
            _, current_node = heapq.heappop(open_set)

            if current_node == goal_node:
                return self._reconstruct_path(came_from, current_node)

            # 8方向の隣接ノードを探索
            for move in [
                (0, 1),
                (0, -1),
                (1, 0),
                (-1, 0),
                (1, 1),
                (1, -1),
                (-1, 1),
                (-1, -1),
            ]:
                neighbor_node = (current_node[0] + move[0], current_node[1] + move[1])

                # グリッド範囲外かチェック
                if not (
                    0 <= neighbor_node[0] < self.grid_size[1]
                    and 0 <= neighbor_node[1] < self.grid_size[0]
                ):
                    continue

                # 障害物セルかチェック
                if self.obstacle_map[neighbor_node] == 1:
                    continue

                # 新しいg_costを計算
                move_cost = np.sqrt(move[0] ** 2 + move[1] ** 2)  # 斜め移動も考慮
                new_g_cost = g_cost[current_node] + move_cost

                if neighbor_node not in g_cost or new_g_cost < g_cost[neighbor_node]:
                    g_cost[neighbor_node] = new_g_cost
                    # ヒューリスティックコスト (ユークリッド距離)
                    h_cost = np.sqrt(
                        (neighbor_node[0] - goal_node[0]) ** 2
                        + (neighbor_node[1] - goal_node[1]) ** 2
                    )
                    f_cost = new_g_cost + h_cost
                    heapq.heappush(open_set, (f_cost, neighbor_node))
                    came_from[neighbor_node] = current_node

        return None

    def smooth_path(self, path: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """
        経路を滑らかに補間する

        Args:
            path (list[tuple[float, float]]): 元の経路点リスト

        Returns:
            list[tuple[float, float]]: 補間された経路点リスト
        """
        if len(path) < 2:
            return path

        smoothed_path = [path[0]]
        for i in range(1, len(path)):
            start = np.array(smoothed_path[-1])
            end = np.array(path[i])
            distance = np.linalg.norm(end - start)
            num_points = max(int(distance / (self.cell_size / 2)), 1)

            for j in range(1, num_points + 1):
                t = j / num_points
                interpolated_point = (1 - t) * start + t * end
                smoothed_path.append((interpolated_point[0], interpolated_point[1]))

        return smoothed_path

    def _reconstruct_path(
        self,
        came_from: dict[tuple[int, int], tuple[int, int]],
        current_node: tuple[int, int],
    ) -> list[tuple[float, float]]:
        """
        経路復元

        Args:
            came_from (dict[tuple[int, int], tuple[int, int]]): ノードの遷移元情報
            current_node (tuple[int, int]): ゴールノード

        Returns:
            list[tuple[float, float]]: 経路点のリスト
        """
        path = []
        while current_node in came_from:
            # グリッド座標をワールド座標に戻す
            world_pos = (
                current_node[1] * self.cell_size,
                current_node[0] * self.cell_size,
            )
            path.append(world_pos)
            current_node = came_from[current_node]
        path.append(
            (current_node[1] * self.cell_size, current_node[0] * self.cell_size)
        )

        # スタート位置を追加
        start_world = (
            current_node[1] * self.cell_size,
            current_node[0] * self.cell_size,
        )
        path.append(start_world)

        return path[::-1]  # 逆順にして返す

    def _find_nearest_free_cell(
        self, start_node: tuple[int, int]
    ) -> tuple[int, int] | None:
        """
        障害物セルの近くにある空いているセルを探す

        Args:
            start_node (tuple[int, int]): (x, y) スタート座標

        Returns:
            tuple[int, int] | None: 空いているセルの座標 or None
        """
        # 4方向にBFSで探索
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        visited = set()
        queue = [start_node]
        while queue:
            current = queue.pop(0)
            if self.obstacle_map[current] == 0:
                return current
            visited.add(current)
            for d in directions:
                neighbor = (current[0] + d[0], current[1] + d[1])
                if (
                    0 <= neighbor[0] < self.grid_size[1]
                    and 0 <= neighbor[1] < self.grid_size[0]
                    and neighbor not in visited
                ):
                    queue.append(neighbor)
        return None

    def visualize(self, ax: Axes):
        """
        障害物マップをAxesに描画
        Args:
            ax (Axes): 描画先のMatplotlibのAxesオブジェクト
        """
        ax.imshow(
            self.obstacle_map,
            cmap="Greys",
            origin="lower",
            extent=(
                0,
                self.grid_size[0] * self.cell_size,
                0,
                self.grid_size[1] * self.cell_size,
            ),
            alpha=0.5,
        )
