from nhan_dien_mat import nhan_dien_mat
from theo_doi_luu_file import theo_doi_luu_file
from theo_doi_file_dang_chay import theo_doi_file_dang_chay
from chong_sao_chep import chong_sao_chep
import threading
import time
from multiprocessing import Process, Event
from giai_ma import *
import os
from tkinter import messagebox
import cv2
import queue

# Tạo queue để giao tiếp với main
message_queue = queue.Queue()

def kiem_tra_webcam():
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        co_webcam = True
    else:
        co_webcam = False
    cap.release()
    return co_webcam

def chay_file(current_file, selected_format):
    # Sử dụng multiprocessing.Event thay vì threading.Event
    stop_event = Event()

    # Tạo các thread cho các tác vụ khác
    thread_theo_doi_file_dang_chay = threading.Thread(
        target=theo_doi_file_dang_chay, 
        args=(stop_event, current_file, selected_format)
    )
    thread_theo_doi_luu_file = threading.Thread(
        target=theo_doi_luu_file, 
        args=(stop_event,)
    )
    thread_chong_sao_chep = threading.Thread(
        target=chong_sao_chep, 
        args=(stop_event,)
    )

    if kiem_tra_webcam():
        # Gửi thông báo camera đang chạy
        message_queue.put({'type': 'camera_status', 'status': True})
        
        # Tạo Process cho nhận diện mặt (thay vì Thread)
        process_nhan_dien_mat = Process(
            target=nhan_dien_mat,
            args=(stop_event,)
        )
        
        # Khởi chạy Process nhận diện mặt
        process_nhan_dien_mat.start()
        
        # Khởi chạy các thread khác
        thread_theo_doi_file_dang_chay.start()
        thread_theo_doi_luu_file.start()
        thread_chong_sao_chep.start()

        try:
            while True:
                # Kiểm tra nếu thread theo dõi file đang chạy dừng
                if not thread_theo_doi_file_dang_chay.is_alive():
                    print("Một thread đã dừng, gửi tín hiệu dừng cho tất cả.")
                    stop_event.set()
                    break
                time.sleep(0.1)  # Giảm CPU usage
        except KeyboardInterrupt:
            print("Người dùng dừng chương trình.")
            stop_event.set()
    else:
        messagebox.showerror("Lỗi", "Không thể mở file do thiết bị không có webcam")

    # Đảm bảo dọn dẹp các tiến trình và luồng
    thread_theo_doi_file_dang_chay.join()
    thread_theo_doi_luu_file.join()
    thread_chong_sao_chep.join()
    
    if kiem_tra_webcam():
        # Kết thúc process nhận diện mặt
        process_nhan_dien_mat.terminate()
        process_nhan_dien_mat.join()
        
        # Gửi thông báo camera đã dừng
        message_queue.put({'type': 'camera_status', 'status': False})