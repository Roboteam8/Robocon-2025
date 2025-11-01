import asyncio

import cv2
import cv2.aruco as aruco
import numpy as np
from picamera2 import Picamera2

from robot import Robot
from stage import ARMarker

CAMREA_RELATIVE_POS = 202.5

CAMERA_MATRIX = np.array([[600, 0, 320], [0, 600, 240], [0, 0, 1]], dtype=float)
DIST_COEFFS = np.zeros((5, 1))

MARKER_SIZE = 0.125
MARKER_POINTS = np.array(
    [
        [-MARKER_SIZE / 2, MARKER_SIZE / 2, 0],
        [MARKER_SIZE / 2, MARKER_SIZE / 2, 0],
        [MARKER_SIZE / 2, -MARKER_SIZE / 2, 0],
        [-MARKER_SIZE / 2, -MARKER_SIZE / 2, 0],
    ],
    dtype=np.float32,
)

DETECTOR = aruco.ArucoDetector(
    aruco.getPredefinedDictionary(aruco.DICT_4X4_50), aruco.DetectorParameters()
)

CAMERA = Picamera2()
CAMERA.configure(
    CAMERA.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
)
CAMERA.start()


def detect_ar() -> list[tuple[tuple[float, float], int]]:
    """
    ARマーカーを検出し、各マーカーまでの相対位置（単位:mm）とマーカーIDのリストを返す。
    Returns:
        list[tuple[tuple[float, float], int]]: 各マーカーまでの相対位置 (x, z) とマーカーIDのリスト
    """
    frame = CAMERA.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    corners, marker_ids, _ = DETECTOR.detectMarkers(gray)

    if marker_ids is None:
        return []

    result: list[tuple[tuple[float, float], int]] = []
    for corner, marker_id in zip(corners, marker_ids):
        success, _, tvec = cv2.solvePnP(
            MARKER_POINTS, corner, CAMERA_MATRIX, DIST_COEFFS
        )
        if success:
            x, _, z = tvec.flatten()
            result.append(((float(x * 1000), float(z * 1000)), int(marker_id)))

    return result




async def correct_path(robot: Robot, ar_markers: list[ARMarker]):
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
        if not detected:
            print("AR Marker: None detected")
        await asyncio.sleep(1)
