import asyncio

import numpy as np

from pathfinding import PathPlanner
from robot import Robot
from robot_parts.arm import Arm, Hand, Shoulder
from robot_parts.driver import Driver, Wheel
from stage import ARMarker, GoalArea, Stage, StartArea, Wall


async def main(blined=False):
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
        position=((start_area.center[0] - 450, start_area.center[1])),
        rotation=np.radians(0),
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

    # await robot.driver.turn(np.pi / 2)
    # await asyncio.sleep(1)
    # await robot.driver.turn(- np.pi / 2)
    # await asyncio.sleep(1)
    # await robot.driver.turn(np.pi / 2)
    # await asyncio.sleep(1)
    # await robot.driver.turn(-np.pi / 2)

    # await robot.arm.release_hands()
    # await robot.arm.open_shoulders()

    # await robot.pickup_parcel()
    # await asyncio.sleep(5)
    # await robot.release_parcel()

    # await robot.pickup_parcel()

    # await robot.drive(
    #     path_planner.plan_path(
    #         (start_area.center[0] - 450, start_area.center[1]),
    #         (goals[0].center[0] + 450, goals[0].center[1]),
    #     ),
    #     ar_markers,
    # )

    # input()

    # await robot.release_parcel()

    # await robot.driver.turn(np.pi / 2)

    async def strategy():
        try:
            start_pos = (start_area.center[0] - 450, start_area.center[1])
            pathes = [
                path_planner.plan_path(
                    start_pos, (goals[0].center[0] + 450, goals[0].center[1])
                ),
                path_planner.plan_path(
                    start_pos, (goals[1].center[0], goals[1].center[1] - 450)
                ),
                # path_planner.plan_path(
                #     start_pos, (goals[2].center[0], goals[2].center[1] - 450)
                # ),
            ]
            for path in pathes:
                await robot.pickup_parcel()
                await asyncio.sleep(0.2)
                await robot.drive(path, ar_markers if not blined else [])
                await asyncio.sleep(0.2)
                await robot.release_parcel()
                await asyncio.sleep(0.2)
                await robot.drive(path, ar_markers if not blined else [], back=True)
            while True:
                await robot.pickup_parcel()
                await asyncio.sleep(0.2)
                await robot.drive(pathes[1], ar_markers if not blined else [])
                await asyncio.sleep(0.2)
                await robot.release_parcel()
                await asyncio.sleep(0.2)
                await robot.drive(pathes[1], ar_markers if not blined else [], back=True)
        except asyncio.CancelledError:
            print("Strategy task cancelled")

    # await robot.driver.turn(np.radians(90))

    await strategy()
    # await robot.arm.release_hands()

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
