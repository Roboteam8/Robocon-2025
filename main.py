from src.stage import Stage, Goal
from src.robot import Robot


def main():
    stage = Stage(
        width=5000,
        height=3000,
        wall=((800, 1500), (800, 3000)),
        goals=[
            Goal(position=(1900, 0), size=(800, 800), id=1),
            Goal(position=(3300, 2200), size=(800, 800), id=2),
            Goal(position=(0, 2200), size=(800, 800), id=3),
        ],
    )
    robot = Robot(position=(0, 0), orientation=0.0, size=500)

    stage.robot = robot  # ロボットをステージに配置
    stage.preview_stage()


if __name__ == "__main__":
    main()
