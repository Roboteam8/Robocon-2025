from pathfinding import find_path
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
    )
    robot = Robot(position=(4750, 250), rotation=135.0, size=500)

    stage.robot = robot  # ロボットをステージに配置

    destination = (250, 250)
    path = find_path(stage, robot.position, destination)
    if path is not None:
        robot.set_path(path)
    stage.preview_stage(path)


if __name__ == "__main__":
    main()
