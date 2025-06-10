import numpy as np
import cv2
import mediapipe as mp
import time
import mss
import win32gui
import win32con
import win32api

def nhan_dien_mat(stop_flag):
    # Khởi tạo MediaPipe Face Mesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # Cấu hình camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 15)

    # Cấu hình chụp màn hình
    sct = mss.mss()
    monitors = sct.monitors[1:]

    # Tạo cửa sổ overlay
    hwnd = win32gui.CreateWindowEx(
        win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT,
        "Static",
        "SecurityOverlay",
        win32con.WS_POPUP,
        0, 0,
        win32api.GetSystemMetrics(0),
        win32api.GetSystemMetrics(1),
        None, None, None, None
    )
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

    # Biến trạng thái
    last_update = 0
    blur_active = False
    text_info = ""
    cooldown = 0.5  # Giây
    last_face_time = time.time()  # Thời điểm cuối cùng phát hiện mặt

    while cap.isOpened() and not stop_flag.is_set():
        success, frame = cap.read()
        if not success:
            continue

        # Giảm kích thước xử lý
        image = cv2.resize(frame, (320, 240))
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = face_mesh.process(image)
        image.flags.writeable = True
        
        # Kiểm tra các điều kiện
        conditions = {
            "khong_co_mat": False,
            "phat_hien_nguoi_khac": False,
            "quay_di": False,
            "occluded": False
        }

        # Phát hiện số lượng mặt và cập nhật thời gian
        current_time = time.time()
        face_count = len(results.multi_face_landmarks) if results.multi_face_landmarks else 0
        
        # Kiểm tra điều kiện dừng chương trình
        if face_count == 0:
            if current_time - last_face_time >= 10:
                print("Không phát hiện khuôn mặt trong 10 giây. Tự động dừng...")
                stop_flag.set()
                break
        else:
            last_face_time = current_time  # Reset bộ đếm nếu có mặt

        conditions["khong_co_mat"] = face_count == 0
        conditions["phat_hien_nguoi_khac"] = face_count > 1

        # Kiểm tra hướng mặt và che khuất
        if face_count == 1:
            landmarks = results.multi_face_landmarks[0].landmark
            img_h, img_w = image.shape[:2]

            # Tính toán góc quay đầu
            face_3d = []
            face_2d = []
            for idx in [33, 263, 1, 61, 291, 199]:
                lm = landmarks[idx]
                face_2d.append([lm.x * img_w, lm.y * img_h])
                face_3d.append([lm.x * img_w, lm.y * img_h, lm.z])

            cam_matrix = np.array([[img_w, 0, img_h/2], 
                                   [0, img_w, img_w/2], 
                                   [0, 0, 1]], dtype=np.float64)
            
            _, rot_vec, _ = cv2.solvePnP(
                np.array(face_3d, dtype=np.float64),
                np.array(face_2d, dtype=np.float64),
                cam_matrix,
                None
            )

            rmat, _ = cv2.Rodrigues(rot_vec)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
            x_angle = angles[0] * 360
            y_angle = angles[1] * 360

            conditions["quay_di"] = abs(y_angle) > 30 or abs(x_angle) > 25

            # Kiểm tra che khuất
            left_eye = (landmarks[33].x, landmarks[33].y)
            right_eye = (landmarks[263].x, landmarks[263].y)
            nose = (landmarks[1].x, landmarks[1].y)
            
            eye_dist = np.linalg.norm(np.array(left_eye) - np.array(right_eye))
            nose_dist = min(
                np.linalg.norm(np.array(nose) - np.array(left_eye)),
                np.linalg.norm(np.array(nose) - np.array(right_eye))
            )
            conditions["occluded"] = eye_dist < 0.1 or nose_dist < 0.07

        # Tổng hợp điều kiện
        should_blur = any(conditions.values())
        text_info = " | ".join([k for k, v in conditions.items() if v])

        # Xử lý làm mờ
        if should_blur and (current_time - last_update) > cooldown:
            try:
                screens = []
                for monitor in monitors:
                    screen = np.array(sct.grab(monitor))
                    blurred = cv2.GaussianBlur(screen, (55, 55), 30)
                    screens.append(blurred)
                
                # Hiển thị overlay
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                blur_active = True
                last_update = current_time
            except Exception as e:
                print(f"Lỗi làm mờ: {e}")

        elif not should_blur and blur_active:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                blur_active = False
            except Exception as e:
                print(f"Lỗi ẩn overlay: {e}")

        # Hiển thị thông tin
        debug_frame = cv2.resize(image, (640, 480))
        cv2.putText(debug_frame, text_info, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Face Monitor', debug_frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Dọn dẹp
    cap.release()
    cv2.destroyAllWindows()
    win32gui.DestroyWindow(hwnd)