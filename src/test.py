from pathfinding import PathPlanner
from robot import Robot


def test_robot_arm(robot: Robot):
    robot.pickup_parcel()
    print("Robot has picked up the parcel")
    robot.release_parcel()
    print("Robot has released the parcel")


def test_robot_pathfollowing(robot: Robot, planner: PathPlanner):
    start = robot.position
    end = (start[0] + 50, start[1] + 50)
    path = planner.plan_path(start, end)
    print(f"Planned path from {start} to {end}: {path}")
    robot.drive(path)
    print("Robot has reached the destination")
