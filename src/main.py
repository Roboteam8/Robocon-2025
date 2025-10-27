import numpy as np
from matplotlib.axes import Axes
from matplotlib.backend_bases import Event, MouseEvent

from pathfinding import PathPlanner
from robot import Robot, Wheel
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
    r_wheel = Wheel(start_stop_pin=16, run_break_pin=20, direction_pin=21, pwm_pin=2)
    l_wheel = Wheel(start_stop_pin=13, run_break_pin=19, direction_pin=26, pwm_pin=3)
    robot = Robot(
        position=(
            start_area.position[0] + start_area.size / 2,
            start_area.position[1] + start_area.size / 2,
        ),
        rotation=np.radians(180),
        radius=500 / 2,
        r_wheel=r_wheel,
        l_wheel=l_wheel,
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
    path_planner = PathPlanner(stage)

    _ = robot.drive(path_planner.plan_path(robot.position, goals[2].center))

    def additional_plot(ax: Axes):
        def on_click(event: Event):
            if not isinstance(event, MouseEvent):
                return
            x, y = event.xdata, event.ydata
            if x is None or y is None:
                return
            _ = robot.drive(path_planner.plan_path(robot.position, (x, y)))

        ax.figure.canvas.mpl_connect("button_press_event", on_click)

    visualize(frame_rate=30, additional_plot=additional_plot)


if __name__ == "__main__":
    main()
