import heapq

import numpy as np
from scipy.interpolate import splev, splprep

from stage import Stage


def find_path(
    stage: Stage, start: tuple[int, int], end: tuple[int, int]
) -> np.ndarray | None:
    """
    A*アルゴリズムで経路を探索し、スプライン曲線で滑らかにする関数
    Args:
        stage (Stage): ステージオブジェクト
        start (tuple[int, int]): スタート地点 (x, y)
        end (tuple[int, int]): ゴール地点 (x, y)
    Returns:
        np.ndarray | None: 補間された経路の座標配列、または経路が見つからない場合はNone
    """
    grid, cell_size = create_grid_map(stage)
    path = a_star_search(grid, start, end, cell_size)
    if not path:
        return None

    return smooth_path(np.array(path))


def create_grid_map(stage: Stage, cell_size=250) -> tuple[np.ndarray, int]:
    """
    ステージ情報からグリッドマップを作成する関数
    Args:
        stage (Stage): ステージオブジェクト
        cell_size (int, optional): グリッドのセルサイズ. Defaults to 250.
    Returns:
        tuple[np.ndarray, int]: グリッドマップとセルサイズ、または作成に失敗した場合はNone
    """

    # ロボットのサイズを考慮して膨張させる半径
    robot_radius_cells = int(np.ceil((stage.robot.size / 2) / cell_size))

    # グリッドマップのサイズを計算
    grid_width = int(np.ceil(stage.x_size / cell_size))
    grid_height = int(np.ceil(stage.y_size / cell_size))
    grid = np.zeros((grid_height, grid_width), dtype=np.uint8)

    # 壁を障害物としてグリッドマップに設定
    for wall in stage.walls:
        (x1, y1), (x2, y2) = wall
        start_x, end_x = sorted((int(x1 / cell_size), int(x2 / cell_size)))
        start_y, end_y = sorted((int(y1 / cell_size), int(y2 / cell_size)))

        for y in range(max(0, start_y), min(grid_height, end_y + 1)):
            for x in range(max(0, start_x), min(grid_width, end_x + 1)):
                grid[y, x] = 1

    # 障害物を膨張させる
    expanded_grid = np.copy(grid)
    for y in range(grid_height):
        for x in range(grid_width):
            if grid[y, x] == 1:
                for dy in range(-robot_radius_cells, robot_radius_cells + 1):
                    for dx in range(-robot_radius_cells, robot_radius_cells + 1):
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < grid_width
                            and 0 <= ny < grid_height
                            and dx**2 + dy**2 <= robot_radius_cells**2
                        ):
                            expanded_grid[ny, nx] = 1

    return expanded_grid, cell_size


def a_star_search(
    grid: np.ndarray,
    start_pos: tuple[float, float],
    end_pos: tuple[float, float],
    cell_size: int,
) -> list[tuple[int, int]] | None:
    """
    A*アルゴリズムで最短経路を探索する関数
    Args:
        grid (np.ndarray): グリッドマップ
        start_pos (tuple[int, int]): スタート地点の座標 (x, y)
        end_pos (tuple[int, int]): ゴール地点の座標 (x, y)
        cell_size (int): セルサイズ
    Returns:
        list[tuple[int, int]] | None: 経路のリスト、または経路が見つからない場合はNone
    """
    start = (int(start_pos[1] / cell_size), int(start_pos[0] / cell_size))
    end = (int(end_pos[1] / cell_size), int(end_pos[0] / cell_size))

    open_set = [(0, start)]
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end:
            return reconstruct_path(came_from, current, cell_size)

        for dy, dx in [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]:
            neighbor = (current[0] + dy, current[1] + dx)

            if not (
                0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]
            ):
                continue
            if grid[neighbor[0], neighbor[1]] == 1:
                continue

            tentative_g_score = g_score[current] + (dx**2 + dy**2) ** 0.5
            if tentative_g_score < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None


def heuristic(a: tuple[int, int], b: tuple[int, int]) -> int:
    """
    マンハッタン距離を計算するヒューリスティック関数
    Args:
        a (tuple[int, int]): 点Aの座標 (y, x)
        b (tuple[int, int]): 点Bの座標 (y, x)
    Returns:
        int: 点Aと点Bのマンハッタン距離
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(
    came_from: dict[tuple[int, int], tuple[int, int]],
    current: tuple[int, int],
    cell_size: int,
) -> list[tuple[int, int]]:
    """
    探索した経路を再構築する関数
    Args:
        came_from (dict[tuple[int, int], tuple[int, int]]): 各点の親点の辞書
        current (tuple[int, int]): ゴール地点の座標 (y, x)
        cell_size (int): セルサイズ
    Returns:
        list[tuple[int, int]]: 再構築された経路のリスト
    """
    path: list[tuple[int, int]] = []
    while current in came_from:
        path.append((current[1] * cell_size, current[0] * cell_size))
        current = came_from[current]
    path.append((current[1] * cell_size, current[0] * cell_size))
    return path[::-1]


def smooth_path(path: np.ndarray) -> np.ndarray:
    """
    B-splineを使用して経路を滑らかにする関数
    Args:
        path (np.ndarray): 経路の座標配列
    Returns:
        np.ndarray: 滑らかにされた経路の座標配列
    """
    if len(path) < 4:
        return path

    tck, u = splprep([path[:, 0], path[:, 1]], s=1000)
    new_points = splev(np.linspace(0, 1, 100), tck)  # type: ignore
    return np.array(new_points).T
