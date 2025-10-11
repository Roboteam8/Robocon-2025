from __future__ import annotations

import heapq
from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt
from scipy.interpolate import splev, splprep

if TYPE_CHECKING:
    from stage import Stage


def find_path(
    stage: Stage,
    start: tuple[float, float],
    end: tuple[float, float],
) -> npt.NDArray[np.float64] | None:
    """
    A*アルゴリズムで経路を探索し、滑らかに補完した経路を返す関数
    Args:
        stage (Stage): ステージオブジェクト
        start (tuple[float, float]): スタート地点 (x, y)
        end (tuple[float, float]): ゴール地点 (x, y)
    Returns:
        npt.NDArray[np.float64] | None: 補間された経路の座標配列
    """
    cell_start = stage.nearest_reachable_cell(start)
    cell_end = stage.nearest_reachable_cell(end)
    if cell_start is None or cell_end is None:
        return None

    open_set = [(0, cell_start)]
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score = {cell_start: 0}
    f_score = {cell_start: heuristic(cell_start, cell_end)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == cell_end:
            return finalize_path(came_from, current, stage.cell_size, start, end)

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
                0 <= neighbor[0] < stage.grid_map.shape[0]
                and 0 <= neighbor[1] < stage.grid_map.shape[1]
            ):
                continue
            if stage.grid_map[neighbor[0], neighbor[1]] == 1:
                continue

            tentative_g_score = g_score[current] + (dx**2 + dy**2) ** 0.5
            if tentative_g_score < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, cell_end)
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
    探索した経路を再構築し、滑らかに補完する関数
    Args:
        came_from (dict[tuple[int, int], tuple[int, int]]): 各点の親点の辞書
        current (tuple[int, int]): ゴール地点の座標 (y, x)
        cell_size (int): セルサイズ
    Returns:
        npt.NDArray[np.float64]: 再構築された経路の座標配列
    """
    path: list[tuple[float, float]] = [end]
    while current in came_from:
        path.append(
            (
                current[1] * cell_size + cell_size / 2,
                current[0] * cell_size + cell_size / 2,
            )
        )
        current = came_from[current]
    path.append(
        (current[1] * cell_size + cell_size / 2, current[0] * cell_size + cell_size / 2)
    )
    path.append(start)
    path.reverse()
    if len(path) < 4:
        return np.array(path, dtype=np.float64)

    tck, _ = splprep([np.array(path)[:, 0], np.array(path)[:, 1]], s=1000)
    # TODO
    path = splev(np.linspace(0, 1, 100), tck)  # type: ignore
    return np.array(path).T
