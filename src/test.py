import time

from pathfinding import PathPlanner
from robot import Robot


def test_robot_arm(robot: Robot):
    robot.arm.open_shoulders()
    print("Shoulders opened")
    time.sleep(0.2)
    robot.arm.grip_hands()
    print("Hands gripped")
    time.sleep(0.2)
    robot.arm.close_shoulders()
    print("Shoulders closed")
    print("Pickup sequence complete")
    time.sleep(1)
    robot.arm.open_shoulders()
    print("Shoulders opened")
    time.sleep(0.2)
    robot.arm.release_hands()
    print("Hands released")
    time.sleep(0.2)
    robot.arm.close_shoulders()
    print("Shoulders closed")
    print("Release sequence complete")


def test_robot_pathfollowing(robot: Robot, planner: PathPlanner):
    start = robot.position
    end = (4000, 1500)
    path = planner.plan_path(start, end)
    print(f"Planned path from {start} to {end}: {path}")
    robot.drive(path)
    print("Robot has reached the destination")
