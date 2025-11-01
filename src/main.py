import asyncio

import numpy as np

from pathfinding import PathPlanner
from robot import Robot
from robot_parts.arm import Arm, Hand, Shoulder
from robot_parts.camera import CAMREA_RELATIVE_POS, detect_ar
from robot_parts.driver import Driver, Wheel
from stage import ARMarker, GoalArea, Stage, StartArea, Wall
from visualize import visualize


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
        position=start_area.center,
        rotation=np.radians(180),
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

    # await robot.driver.turn(np.pi)
    # await robot.driver.turn(-np.pi)

    # path_planner = PathPlanner(stage)

    async def correct_path():
        while True:
            detected = detect_ar()
            rx, ry = robot.position
            cx, cy = (
                rx + np.cos(np.pi - robot.rotation) * CAMREA_RELATIVE_POS,
                ry + np.sin(np.pi - robot.rotation) * CAMREA_RELATIVE_POS,
            )
            for (dx, dy), marker_id in detected:
                if len(ar_markers) <= marker_id:
                    continue

                ar_marker = ar_markers[marker_id - 1]

                actual_position = (
                    ar_marker.position[0]
                    + (dx * np.sin(robot.rotation) - dy * np.cos(robot.rotation)),
                    ar_marker.position[1]
                    + (dx * np.cos(robot.rotation) + dy * np.sin(robot.rotation)),
                )
                estimated_relative_position = (
                    np.arctan2(ar_marker.position[1] - cy, ar_marker.position[0] - cx)
                    - robot.rotation
                )
                actual_relative_rotation = np.arctan2(dy, dx) - (np.pi / 2)

                print(f"AR Marker {marker_id}:")
                print(f"  Estimated Position: ({rx:.1f}, {ry:.1f})")
                print(
                    f"  Actual Position:    ({actual_position[0]:.1f}, {actual_position[1]:.1f})"
                )
                print(
                    f"  Estimated Relative Rotation: {np.degrees(estimated_relative_position):.1f} deg"
                )
                print(
                    f"  Actual Relative Rotation:    {np.degrees(actual_relative_rotation):.1f} deg"
                )
                await robot.driver.turn(
                    actual_relative_rotation - estimated_relative_position
                )
            if not detected:
                print("AR Marker: None detected")
            await asyncio.sleep(1)

    await correct_path()

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
