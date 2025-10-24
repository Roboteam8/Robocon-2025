from itertools import pairwise

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from shapely import LineString, Point, Polygon, unary_union
from shapely.plotting import patch_from_polygon

from stage import Stage, Wall
from visualize import Visualizable


class PathPlanner(Visualizable):
    """
    経路計画を管理するクラス
    Attributes:
        shape (Polygon): 障害物の形状
    """

    shape: Polygon = Polygon()

    _wall: Wall
    _expansion_radius: float

    def __init__(self, stage: Stage, safe_margin: float = 10):
        self._wall = stage.wall
        self._expansion_radius = stage.robot.radius + safe_margin

        outer_frame = LineString(
            [
                (0, 0),
                (stage.x_size, 0),
                (stage.x_size, stage.y_size),
                (0, stage.y_size),
                (0, 0),
            ]
        )
        wall_shapes = [
            LineString([(stage.wall.x, ys), (stage.wall.x, ye)])
            for ys, ye in stage.wall.obstacled_y
        ]

        buffered_obstacles = [
            obstacle.buffer(self._expansion_radius)
            for obstacle in wall_shapes + [outer_frame]
        ]
        merged_obstacles = unary_union(buffered_obstacles)

        if isinstance(merged_obstacles, Polygon):
            self.shape = merged_obstacles

    def plan_path(
        self, start: tuple[float, float], end: tuple[float, float]
    ) -> list[tuple[float, float]]:
        """
        指定した開始点から終了点までの経路を計画するメソッド

        Args:
            start (tuple[float, float]): 開始点 (x, y)
            end (tuple[float, float]): 終了点 (x, y)

        Returns:
            list[tuple[float, float]]: 計画された経路の点のリスト
        """
        sx, sy = self._nearest_free_point(start)
        ex, ey = self._nearest_free_point(end)

        path = [(sx, sy)]

        if min(sx, ex) < self._wall.x < max(sx, ex):
            free_y_area: list[tuple[float, float]] = []
            for w1, w2 in pairwise(self._wall.obstacled_y):
                if w1[1] + self._expansion_radius < w2[0] - self._expansion_radius:
                    free_y_area.append(
                        (w1[1] + self._expansion_radius, w2[0] - self._expansion_radius)
                    )

            free_y_mids = [(fs + fe) / 2 for fs, fe in free_y_area]
            y_mid = min(free_y_mids, key=lambda y: abs((sy + ey) / 2 - y))

            path.append((sx, y_mid))
            path.append((ex, y_mid))
        elif sx != ex and sy != ey:
            path.append((ex, sy))

        path.append((ex, ey))
        return path

    def _nearest_free_point(self, point: tuple[float, float]) -> tuple[float, float]:
        """
        指定した点から最も近い障害物のない点を取得するメソッド

        Args:
            point (tuple[float, float]): 基準点 (x, y)

        Returns:
            tuple[float, float]: 最も近い障害物のない点 (x, y)
        """
        if self.shape.is_empty:
            return point
        p = Point(point)
        if not self.shape.contains(p):
            return point
        for interior in self.shape.interiors:
            if interior.contains(p):
                nearest = interior.interpolate(interior.project(p))
                return (nearest.x, nearest.y)
        return point

    def visualize(self, ax: Axes) -> None:
        plt.rcParams["hatch.linewidth"] = 5
        ax.add_patch(
            patch_from_polygon(
                self.shape, hatch="//", facecolor="gray", edgecolor="yellow", alpha=0.3
            )
        )
