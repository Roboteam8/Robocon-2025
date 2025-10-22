import networkx as nx
import numpy as np
from matplotlib.axes import Axes
from shapely import LineString, Point, Polygon, unary_union
from shapely.plotting import patch_from_polygon

from stage import Stage
from visualize import Visualizable


class PathCalcurator(Visualizable):
    obstacle_area: Polygon

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

        walls = [LineString([wall.start, wall.end]) for wall in stage.walls]

        buffered = [
            obstacle.buffer(stage.robot.radius + 100)
            for obstacle in walls + [outer_frame]
        ]
        merged = unary_union(buffered)
        if isinstance(merged, Polygon):
            self.obstacle_area = merged

    def calcurate_path(self, start: Point, goal: Point) -> LineString | None:
        if self.obstacle_area.contains(start):
            start = self._nearest_reachable_point(start)
        if self.obstacle_area.contains(goal):
            goal = self._nearest_reachable_point(goal)

        direct_line = LineString([start, goal])
        if not self.obstacle_area.intersects(direct_line):
            return direct_line

        moveable_space = unary_union(
            [Polygon(interior) for interior in self.obstacle_area.interiors]
        )
        if not isinstance(moveable_space, Polygon):
            return None

        G = nx.Graph()

        start_node = tuple(start.coords[0])
        goal_node = tuple(goal.coords[0])

        exterior_nodes = [tuple(coord) for coord in moveable_space.exterior.coords[:-1]]

        all_nodes = [start_node, goal_node] + exterior_nodes
        G.add_nodes_from(set(all_nodes))

        node_list = list(G.nodes())

        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                node_a = node_list[i]
                node_b = node_list[j]
                line = LineString([node_a, node_b])

                if moveable_space.contains(line):
                    distance = line.length
                    G.add_edge(node_a, node_b, weight=distance)

        try:
            path_nodes = nx.shortest_path(
                G, source=start_node, target=goal_node, weight="weight"
            )
            return LineString(path_nodes)

        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def _nearest_reachable_point(self, point: Point) -> Point:
        direction = np.array(point.coords[0]) - np.array(
            self.obstacle_area.centroid.coords[0]
        )
        direction /= np.linalg.norm(direction)
        test_point = Point(point.coords[0])
        step_size = 1.0
        while self.obstacle_area.contains(test_point):
            test_point = Point(
                test_point.x + direction[0] * step_size,
                test_point.y + direction[1] * step_size,
            )
        return Point(
            test_point.x - direction[0] * step_size,
            test_point.y - direction[1] * step_size,
        )

    def visualize(self, ax: Axes) -> None:
        if self.obstacle_area.is_empty:
            return
        ax.add_patch(
            patch_from_polygon(
                self.obstacle_area, facecolor="gray", edgecolor="black", alpha=0.5
            )
        )
