import asyncio
from fastapi import FastAPI, WebSocket

from robot import Robot
from stage import Stage

app = FastAPI()

def get_static_data(stage: Stage):
    return {
        "type": "static",
        "x_size": stage.x_size,
        "y_size": stage.y_size,
        "wall": {
            "x": stage.wall.x,
            "obstacled_y": stage.wall.obstacled_y,
        },
        "goals": [{ "pos": goal.position, "size": goal.size, "color": goal.color(), "id": goal.goal_id } for goal in stage.goals],
        "starts": {
            "pos": stage.start_area.position,
            "size": stage.start_area.size,
            "color": stage.start_area.color(),
        },
        "robot": {
            "radius": stage.robot.radius
        }
    }

def get_dynamic_data(robot: Robot):
    return {
        "type": "dynamic",
        "robot": {
            "pos": robot.position,
            "rotation": robot.rotation,
            "path": robot.path
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    stage: Stage | None = getattr(app.state, "stage", None)
    if stage is None:
        await ws.close(code=1000)
        return

    static_data = get_static_data(stage)
    await ws.send_json(static_data)

    try:
        while True:
            dynamic_data = get_dynamic_data(stage.robot)
            await ws.send_json(dynamic_data)
            await asyncio.sleep(1 / 30)
    finally:
        await ws.close()
