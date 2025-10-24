import numpy as np
from matplotlib.axes import Axes

from pathfinding import Path
from robot import Robot
from stage import GoalArea, Stage, StartArea, Wall
from visualize import visualize


def main():
    start_area = StartArea(position=(4000, 0), size=1000)
    goals = [
        GoalArea(position=(1500, 0), size=1000, goal_id=1),
        GoalArea(position=(2500, 2000), size=1000, goal_id=2),
        GoalArea(position=(0, 2000), size=1000, goal_id=3),
    ]
    wall = Wall(
        x=1000,
        obstacled_y=[(0, 1000), (2000, 3000)],
    )
    robot = Robot(
        position=(
            start_area.position[0] + start_area.size / 2,
            start_area.position[1] + start_area.size / 2,
        ),
        rotation=np.radians(180),
        radius=500 / 2,
    )
    stage = Stage(
        x_size=5000,
        y_size=3000,
        start_area=start_area,
        wall=wall,
        goals=goals,
        ar_markers=[],
        robot=robot,
    )

    pathes = [
        Path(start_area.center, goal.center, color=f"C{i}")
        for i, goal in enumerate(stage.goals)
    ]
    robot.set_path(pathes[0])

    def additional_plot(ax: Axes):
        pass

    visualize(frame_rate=30, additional_plot=additional_plot)


if __name__ == "__main__":
    main()
