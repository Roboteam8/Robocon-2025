import time
import cv2
import cv2.aruco as aruco
import numpy as np
from picamera2 import Picamera2

# --- カメラパラメータ（概算） ---
camera_matrix = np.array([[600, 0, 320],
                          [0, 600, 240],
                          [0, 0, 1]], dtype=float)
dist_coeffs = np.zeros((5,1))

# --- ARマーカーサイズ（mm単位） ---
marker_size_mm = 50
marker_size_m = marker_size_mm / 1000

# --- ArUco辞書とパラメータ ---
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()

# --- マーカーID → 種類 ---
marker_types = {i: f"Type {i}" for i in range(11)}

# --- Picamera2 初期化 ---
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()

ar_relative_distance = {}

print("ESCキーで終了")

while True:
    frame = picam2.capture_array()
    if frame is None or frame.size == 0:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is not None:
        for i, corner in enumerate(corners):
            rvec, tvec, _ = aruco.estimatePoseSingleMarkers(
                corner, marker_size_m, camera_matrix, dist_coeffs
            )
            tvec = tvec[0][0]

            marker_id = ids[i][0]
            dx_mm = tvec[0] * 1000
            dy_mm = tvec[2] * 1000
            marker_type = marker_types.get(marker_id, "Unknown")

            ar_relative_distance[marker_id] = {
                'type': marker_type,
                'dx': dx_mm,
                'dy': dy_mm
            }

    if ar_relative_distance:
        print("------ AR Marker Info ------")
        for mid, info in ar_relative_distance.items():
            print(f"ID {mid} ({info['type']}): dx={info['dx']:.1f}mm, dy={info['dy']:.1f}mm")
        print("---------------------------\n")

    # 0.5秒待つ
    time.sleep(0.5)

    # ESCで終了
    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()
picam2.stop()
