import heapq

import numpy as np
import numpy.typing as npt
from scipy.interpolate import splev, splprep

from stage import GridMap


def find_path(
    grid_map: GridMap,
    start: tuple[float, float],
    end: tuple[float, float],
) -> npt.NDArray[np.float64] | None:
    """
    A*アルゴリズムで経路を探索し、滑らかに補完した経路を返す関数
    Args:
        grid_map (GridMap): グリッドマップオブジェクト
        start (tuple[float, float]): スタート地点 (x, y)
        end (tuple[float, float]): ゴール地点 (x, y)
    Returns:
        npt.NDArray[np.float64] | None: 補間された経路の座標配列
    """
    start_cell = grid_map.nearest_reachable_cell(start)
    end_cell = grid_map.nearest_reachable_cell(end)
    if start_cell is None or end_cell is None:
        return None

    cell_size = grid_map.cell_size
    rows, cols = grid_map.shape
    open_set: list[tuple[int, tuple[int, int]]] = [(0, start_cell)]
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score = {start_cell: 0}
    f_score = {start_cell: heuristic(start_cell, end_cell)}
    closed_set = set()
    while open_set:
        current = heapq.heappop(open_set)[1]
        if current == end_cell:
            return finalize_path(came_from, current, cell_size, start, end)

        closed_set.add(current)
        for direction in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if (
                0 <= neighbor[0] < rows
                and 0 <= neighbor[1] < cols
                and grid_map[neighbor[0], neighbor[1]] == 0
            ):
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(
                        neighbor, end_cell
                    )
                    if neighbor not in [i[1] for i in open_set]:
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


def finalize_path(
    came_from: dict[tuple[int, int], tuple[int, int]],
    current: tuple[int, int],
    cell_size: int,
    start: tuple[float, float],
    end: tuple[float, float],
) -> npt.NDArray[np.float64]:
    """
    探索した経路を再構築し、B-Splineで滑らかに補完する関数
    Args:
        came_from (dict[tuple[int, int], tuple[int, int]]): 各点の親点の辞書
        current (tuple[int, int]): ゴール地点の座標 (y, x)
        cell_size (int): セルサイズ
        start (tuple[float, float]): スタート地点の実座標 (x, y)
        end (tuple[float, float]): ゴール地点の実座標 (x, y)
    Returns:
        npt.NDArray[np.float64]: 再構築された経路の座標配列
    """
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()

    # セル座標を実座標に変換
    path_coords = np.array(
        [
            (x * cell_size + cell_size / 2, y * cell_size + cell_size / 2)
            for y, x in path
        ]
    )

    # スタートとエンドを正確に設定
    path_coords[0] = np.array(start)
    path_coords[-1] = np.array(end)

    # B-Splineで滑らかに補完
    if len(path_coords) < 3:
        return path_coords  # 点が少ない場合は補完しない

    tck, u = splprep(path_coords.T, s=0)
    unew = np.linspace(0, 1.0, num=max(100, len(path_coords) * 3))
    # TODO: mypyのバグ？
    out = splev(unew, tck)  # type: ignore
    smoothed_path = np.vstack(out).T

    return smoothed_path
