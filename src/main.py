import numpy as np

from pathfinding import GridMap, PathCalculator
from robot import Robot
from stage import Goal, Stage, StartArea, Wall
from visualize import visualize


def main():
    stage = Stage(
        x_size=5000,
        y_size=3000,
        start_area=StartArea(position=(4000, 0), size=1000),
        walls=[
            Wall(start=(1000, 0), end=(1000, 1000)),
            Wall(start=(1000, 2000), end=(1000, 3000)),
        ],
        goals=[
            Goal(position=(1500, 0), size=1000, goal_id=1),
            Goal(position=(2500, 2000), size=1000, goal_id=2),
            Goal(position=(0, 2000), size=1000, goal_id=3),
        ],
        ar_markers=[],
        robot=Robot(position=(3750, 500), rotation=np.radians(180), radius=500 / 2),
    )

    path = PathCalculator(
        GridMap(stage, cell_size=50, expansion_radius=stage.robot.radius),
        stage.robot.position,
        (500, 1750),
    )
    path.calculate_path()
    stage.robot.set_path(path)

    visualize(30)


if __name__ == "__main__":
    main()
