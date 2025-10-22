import numpy as np
from shapely import Point

from pathfinding import PathCalcurator
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
        robot=Robot(position=(4250, 500), rotation=np.radians(180), radius=500 / 2),
    )

    path_calcurator = PathCalcurator(stage)
    path = path_calcurator.calcurate_path(
        start=Point(stage.robot.position),
        goal=Point(500, 2500),
    )

    if path:
        stage.robot.set_path(np.array(path.coords))

    visualize(frame_rate=30)


if __name__ == "__main__":
    main()
