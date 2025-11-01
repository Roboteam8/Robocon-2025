from typing import TypedDict

import cv2
import cv2.aruco as aruco
import numpy as np
from picamera2 import Picamera2

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

Detection = TypedDict(
    "Detection",
    {"relative_pos": tuple[float, float], "rotation": float, "marker_id": int},
)


def detect_ar() -> list[Detection]:
    """
    ARマーカーを検出し、各マーカーまでの相対位置（単位:mm）とカメラの回転、マーカーIDのリストを返す。
    Returns:
        list[Detection]: 検出されたARマーカーのリスト。各要素はrelative_pos, rotation, marker_idを含む。
    """
    frame = CAMERA.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    corners, marker_ids, _ = DETECTOR.detectMarkers(gray)

    if marker_ids is None:
        return []

    result: list[Detection] = []
    for corner, marker_id in zip(corners, marker_ids):
        success, rvec, tvec = cv2.solvePnP(
            MARKER_POINTS, corner, CAMERA_MATRIX, DIST_COEFFS
        )
        if success:
            x, y, z = tvec.flatten()
            relative_pos = (float(x), float(z))
            rotation, _ = cv2.Rodrigues(rvec)
            angle = float(np.arctan2(rotation[1, 0], rotation[0, 0]))
            result.append(
                {
                    "relative_pos": relative_pos,
                    "rotation": np.degrees(angle),
                    "marker_id": int(marker_id),
                }
            )

    return result
