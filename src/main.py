import numpy as np

from pathfinding import find_path
from preview import preview
from robot import Robot
from stage import Goal, Stage


def main():
    stage = Stage(
        x_size=5000,
        y_size=3000,
        walls=[((800, 0), (800, 1000)), ((800, 2000), (800, 3000))],
        goals=[
            Goal(position=(1900, 0), size=(800, 800), id=1),
            Goal(position=(3300, 2200), size=(800, 800), id=2),
            Goal(position=(0, 2200), size=(800, 800), id=3),
        ],
        robot=Robot(position=(4700, 300), rotation=np.radians(180), radius=500 / 2),
    )

    destination = (400, 1950)
    path = find_path(stage.grid_map, stage.robot.position, destination)
    if path is not None:
        stage.robot.path = path

    preview(stage, show_grid_map=True)


if __name__ == "__main__":
    main()
