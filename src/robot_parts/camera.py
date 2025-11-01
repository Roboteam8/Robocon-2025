import cv2
import cv2.aruco as aruco
import numpy as np
from picamera2 import Picamera2

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

def detect_ar() -> list[tuple[float, float, int]] | None:
    frame = CAMERA.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    corners, marker_ids, _ = DETECTOR.detectMarkers(gray)

    if marker_ids is None:
        return

    result: list[tuple[float, float, int]] = []
    for corner, marker_id in zip(corners, marker_ids):
        success, _, tvec = cv2.solvePnP(MARKER_POINTS, corner, CAMERA_MATRIX, DIST_COEFFS)
        if success:
            result.append((tvec[0][0] * 1000, tvec[2][0] * 1000, marker_id[0]))

    return result
