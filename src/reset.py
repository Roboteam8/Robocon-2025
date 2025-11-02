import asyncio

import numpy as np

from robot import Robot
from robot_parts.arm import Arm, Hand, Shoulder
from robot_parts.driver import Driver, Wheel


async def main():
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
        position=(0, 0),
        rotation=np.radians(0),
        radius=500 / 2,
        driver=driver,
        arm=arm,
    )
    await robot.arm.release_hands()
    await robot.arm.open_shoulders()


if __name__ == "__main__":
    asyncio.run(main())
