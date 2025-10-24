from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from shapely import LineString, Point, Polygon, unary_union
from shapely.plotting import patch_from_polygon

from stage import Stage
from visualize import Visualizable


class PathPlanner(Visualizable):
    """
    経路計画を管理するクラス
    Attributes:
        shape (Polygon): 障害物の形状
    """

    shape: Polygon = Polygon()

    def __init__(self, stage: Stage):
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
            obstacle.buffer(stage.robot.radius + 10)
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

        if min(sx, ex) < 1000 < max(sx, ex):
            path.append((sx, 1500))
            path.append((ex, 1500))
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
        nearest_point = self.shape.interiors[0].interpolate(
            self.shape.interiors[0].project(p)
        )
        return (nearest_point.x, nearest_point.y)

    def visualize(self, ax: Axes) -> None:
        plt.rcParams["hatch.linewidth"] = 5
        ax.add_patch(
            patch_from_polygon(
                self.shape, hatch="//", facecolor="gray", edgecolor="yellow", alpha=0.3
            )
        )
