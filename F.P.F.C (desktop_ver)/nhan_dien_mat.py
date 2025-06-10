import numpy as np
import cv2
import mediapipe as mp
import time
import mss
import win32gui
import win32con
import win32api

def nhan_dien_mat(co_dung):
    mp_mat = mp.solutions.face_mesh
    mat = mp_mat.FaceMesh(
        max_num_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cam.set(cv2.CAP_PROP_FPS, 15)

    chup_man_hinh = mss.mss()
    man_hinh = chup_man_hinh.monitors[1:]

    cua_so = win32gui.CreateWindowEx(
        win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT,
        "Static",
        "SecurityOverlay",
        win32con.WS_POPUP,
        0, 0,
        win32api.GetSystemMetrics(0),
        win32api.GetSystemMetrics(1),
        None, None, None, None
    )
    win32gui.SetLayeredWindowAttributes(cua_so, 0, 255, win32con.LWA_ALPHA)

    lan_cap_nhat = 0
    dang_mo = False
    thong_tin = ""
    thoi_gian_cho = 0.5
    lan_cuoi_mat = time.time()

    while cam.isOpened() and not co_dung.is_set():
        thanh_cong, khung = cam.read()
        if not thanh_cong:
            continue

        anh = cv2.resize(khung, (320, 240))
        anh = cv2.cvtColor(cv2.flip(anh, 1), cv2.COLOR_BGR2RGB)
        anh.flags.writeable = False
        ket_qua = mat.process(anh)
        anh.flags.writeable = True
        
        dieu_kien = {
            "khong_co_mat": False,
            "phat_hien_nguoi_khac": False,
            "quay_di": False,
            "bi_che": False
        }

        thoi_gian = time.time()
        so_mat = len(ket_qua.multi_face_landmarks) if ket_qua.multi_face_landmarks else 0
        
        if so_mat == 0:
            if thoi_gian - lan_cuoi_mat >= 10:
                print("Không phát hiện khuôn mặt trong 10 giây. Tự động dừng...")
                co_dung.set()
                break
        else:
            lan_cuoi_mat = thoi_gian

        dieu_kien["khong_co_mat"] = so_mat == 0
        dieu_kien["phat_hien_nguoi_khac"] = so_mat > 1

        if so_mat == 1:
            diem = ket_qua.multi_face_landmarks[0].landmark
            cao, rong = anh.shape[:2]

            mat_3d = []
            mat_2d = []
            for idx in [33, 263, 1, 61, 291, 199]:
                lm = diem[idx]
                mat_2d.append([lm.x * rong, lm.y * cao])
                mat_3d.append([lm.x * rong, lm.y * cao, lm.z])

            ma_tran = np.array([[rong, 0, cao/2], 
                               [0, rong, rong/2], 
                               [0, 0, 1]], dtype=np.float64)
            
            _, vec_xoay, _ = cv2.solvePnP(
                np.array(mat_3d, dtype=np.float64),
                np.array(mat_2d, dtype=np.float64),
                ma_tran,
                None
            )

            ma_tran_xoay, _ = cv2.Rodrigues(vec_xoay)
            goc, _, _, _, _, _ = cv2.RQDecomp3x3(ma_tran_xoay)
            goc_x = goc[0] * 360
            goc_y = goc[1] * 360

            dieu_kien["quay_di"] = abs(goc_y) > 30 or abs(goc_x) > 25

            mat_trai = (diem[33].x, diem[33].y)
            mat_phai = (diem[263].x, diem[263].y)
            mui = (diem[1].x, diem[1].y)
            
            khoang_mat = np.linalg.norm(np.array(mat_trai) - np.array(mat_phai))
            khoang_mui = min(
                np.linalg.norm(np.array(mui) - np.array(mat_trai)),
                np.linalg.norm(np.array(mui) - np.array(mat_phai))
            )
            dieu_kien["bi_che"] = khoang_mat < 0.1 or khoang_mui < 0.07

        can_mo = any(dieu_kien.values())
        thong_tin = " | ".join([k for k, v in dieu_kien.items() if v])

        if can_mo and (thoi_gian - lan_cap_nhat) > thoi_gian_cho:
            try:
                man_hinh_mo = []
                for mon in man_hinh:
                    anh_man_hinh = np.array(chup_man_hinh.grab(mon))
                    anh_mo = cv2.GaussianBlur(anh_man_hinh, (55, 55), 30)
                    man_hinh_mo.append(anh_mo)
                
                win32gui.ShowWindow(cua_so, win32con.SW_SHOW)
                dang_mo = True
                lan_cap_nhat = thoi_gian
            except Exception as e:
                print(f"Lỗi làm mờ: {e}")

        elif not can_mo and dang_mo:
            try:
                win32gui.ShowWindow(cua_so, win32con.SW_HIDE)
                dang_mo = False
            except Exception as e:
                print(f"Lỗi ẩn overlay: {e}")

        khung_hien_thi = cv2.resize(anh, (640, 480))
        cv2.putText(khung_hien_thi, thong_tin, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Face Monitor', khung_hien_thi)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cam.release()
    cv2.destroyAllWindows()
    win32gui.DestroyWindow(cua_so)