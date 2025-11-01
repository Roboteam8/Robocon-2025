import cv2
import numpy as np

# ==========================
# 1. 画像の読み込み
# ==========================
image_path = "stub/ar-sample.jpg"
image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError(f"画像が見つかりません: {image_path}")

# ==========================
# 2. マーカー検出
# ==========================
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
corners, ids, rejected = detector.detectMarkers(im

if ids is None:
    print("マーカーが検出されませんでした。")
    exit()

# ==========================
# 3. カメラパラメータ設定
# ==========================
camera_matrix = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], dtype=float)
dist_coeffs = np.zeros((5, 1))
marker_length = 0.125  # 12.5cm

# ==========================
# 4. 姿勢推定 (estimatePoseSingleMarkers が無い場合)
# ==========================
# solvePnP を手動で使って同等の処理を行う
for i in range(len(ids)):
    # 各マーカーの四隅を取得
    corner = corners[i][0]

    # マーカーの3D座標（ワールド座標系における角）
    obj_points = np.array(
        [
            [-marker_length / 2, marker_length / 2, 0],
            [marker_length / 2, marker_length / 2, 0],
            [marker_length / 2, -marker_length / 2, 0],
            [-marker_length / 2, -marker_length / 2, 0],
        ],
        dtype=np.float32,
    )

    # solvePnPで姿勢を推定
    success, rvec, tvec = cv2.solvePnP(obj_points, corner, camera_matrix, dist_coeffs)
    if not success:
        continue

    # ==========================
    # 5. 回転ベクトル → 回転行列
    # ==========================
    R, _ = cv2.Rodrigues(rvec)
    camera_position = -R.T @ tvec

    # ==========================
    # 6. オイラー角計算
    # ==========================
    sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
    singular = sy < 1e-6

    if not singular:
        roll = np.arctan2(R[2, 1], R[2, 2])
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = np.arctan2(R[1, 0], R[0, 0])
    else:
        roll = np.arctan2(-R[1, 2], R[1, 1])
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = 0

    # ==========================
    # 7. 出力
    # ==========================
    print(f"--- マーカー ID: {ids[i][0]} ---")
    print(f"回転ベクトル:\n{rvec.ravel()}")
    print(f"回転行列:\n{R}")
    print(f"カメラ位置（ワールド座標）:\n{camera_position.ravel()}")
    print(f"オイラー角 [deg]: {np.degrees([roll, pitch, yaw])}")

    # 描画（任意）
    cv2.aruco.drawDetectedMarkers(image, corners, ids)
    cv2.drawFrameAxes(
        image, camera_matrix, dist_coeffs, rvec, tvec, marker_length * 0.5
    )

# 結果表示
cv2.imshow("AR Marker Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
