import asyncio

import numpy as np

from pathfinding import PathPlanner
from robot import Robot
from robot_parts.arm import Arm, Hand, Shoulder
from robot_parts.driver import Driver, Wheel
from stage import ARMarker, GoalArea, Stage, StartArea, Wall


async def main():
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
    driver = Driver(
        r_wheel=Wheel(
            start_stop_pin=16,
            run_break_pin=20,
            direction_pin=21,
            pwm_pin=2,
        ),
        l_wheel=Wheel(
            start_stop_pin=13,
            run_break_pin=19,
            direction_pin=26,
            pwm_pin=3,
        ),
    )
    arm = Arm(
        r_shoulder=Shoulder(
            open_pin=9,
            close_pin=11,
        ),
        l_shoulder=Shoulder(
            open_pin=8,
            close_pin=25,
        ),
        r_hand=Hand(
            pin_num=18,
            release_angle=160,
            grip_angle=120,
        ),
        l_hand=Hand(pin_num=17, release_angle=0, grip_angle=40),
    )
    robot = Robot(
        position=goals[1].center,
        rotation=np.radians(-90),
        radius=500 / 2,
        driver=driver,
        arm=arm,
    )
    ar_markers = [
        ARMarker(position=(5000, 500), normal=(-1, 0)),
        ARMarker(position=(2000, 0), normal=(0, 1)),
        ARMarker(position=(1000, 500), normal=(1, 0)),
        ARMarker(position=(3000, 3000), normal=(0, -1)),
        ARMarker(position=(1000, 2500), normal=(1, 0)),
        ARMarker(position=(500, 0), normal=(0, 1)),
        ARMarker(position=(0, 500), normal=(1, 0)),
        ARMarker(position=(0, 2500), normal=(1, 0)),
        ARMarker(position=(500, 3000), normal=(0, -1)),
    ]

    stage = Stage(
        x_size=5000,
        y_size=3000,
        start_area=start_area,
        wall=wall,
        goals=goals,
        ar_markers=ar_markers,
        robot=robot,
    )

    path_planner = PathPlanner(stage)

    # await robot.drive(path_planner.plan_path(robot.position, goals[2].center), ar_markers)

    while True:
        robot.detect_position(ar_markers)
        await asyncio.sleep(1)

    # async def strategy():
    #     try:
    #         pathes = [
    #             path_planner.plan_path(start_area.center, goal.center) for goal in goals
    #         ]
    #         for path in pathes:
    #             await robot.pickup_parcel()
    #             await robot.drive(path)
    #             await robot.release_parcel()
    #             await robot.drive(path[::-1])
    #         while True:
    #             await robot.pickup_parcel()
    #             await robot.drive(pathes[2])
    #             await robot.release_parcel()
    #             await robot.drive(pathes[2][::-1])
    #     except asyncio.CancelledError:
    #         print("Strategy task cancelled")

    # task = asyncio.Task(strategy())

    # # def additional_plot(ax: Axes):
    # #     def on_click(event: Event):
    # #         if not isinstance(event, MouseEvent):
    # #             return
    # #         x, y = event.xdata, event.ydata
    # #         if x is None or y is None:
    # #             return
    # #         # robot.drive(path_planner.plan_path(robot.position, (x, y)))

    # #     ax.figure.canvas.mpl_connect("button_press_event", on_click)

    # visualize(frame_rate=30)
    # task.cancel()
    # await task


if __name__ == "__main__":
    asyncio.run(main())
