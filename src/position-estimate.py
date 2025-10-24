import numpy as np
import cv2
from cv2 import aruco
from scipy.spatial.transform import Rotation as R
import math


def main():
    img = cv2.imread("test_image_1.png")  # 画像の読み取り
    # マーカーサイズ
    marker_length = 0.056  # メートル単位
    # マーカーの辞書選択
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    camara_matrix = np.array(
        [[919.53063477, 0, 639.5], [0, 919.53063477, 359.5], [0, 0, 1]]
    )
    distortion_coefficients = np.array([0.0, 0.0, 0.0, 0.0, 0.0])

    while True:
        ret, img = cap.read()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, dictionary)
        aruco.drawDetectedMarkers(img, corners, ids(0, 255, 255))
        if len(corners) > 0:
            for i, corner in enumerate(corners):
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(
                    corners, marker_length, camara_matrix, distortion_coefficients
                )
                tvec = np.squeeze(tvec)
                rvec = np.squeeze(rvec)
                # 回転ベクトルを回転行列に変換
                R_ct, _ = cv2.Rodrigues(rvec)
                R_tc = R_ct.T
                # カメラの位置を計算
                cam_pos = -R_tc @ tvec
                # 姿勢
                rot = R.from_matrix(R_tc)
                quat = rot.as_quat()  # (x, y, z, w)
                eular_rad = rot.as_euler("xyz", degrees=True)
                pitch, roll, yaw = eular_rad
                # pitch = -math.atan2(R_tc[2, 0], math.sqrt(R_tc[0, 0]**2 + R_tc[1, 0]**2))
                print(f"ID: {ids[0][0]}Camera Position (x, y, z): {cam_pos}")
                print(f"[ID{ids[0][0]}] Robot Yaw[deg]: {pitch}")
                # 可視化
                draw_pole_length = marker_length / 2
                cv2.drawFrameAxes(
                    img,
                    camara_matrix,
                    distortion_coefficients,
                    rvec,
                    tvec,
                    draw_pole_length,
                )
        cv2.imshow("drawDetectesMakers", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
