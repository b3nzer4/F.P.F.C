import psutil
import time
import os
from giai_ma import *

def theo_doi_file_dang_chay(co_dung, tep_hien_tai, dinh_dang):
    def xoa_file(duong_dan):
        try:
            if os.path.exists(duong_dan):
                os.remove(duong_dan)
                print(f"Đã xóa tệp: {duong_dan}")
            else:
                print(f"Tệp không tồn tại: {duong_dan}")
        except Exception as e:
            print(f"Lỗi khi xóa tệp: {e}")

    tep_tam, ten_tep = giai_ma(tep_hien_tai, dinh_dang)
    def kiem_tra_tien_trinh(tep):
        tep = tep.lower()
        for tien_trinh in psutil.process_iter():
            try:
                lenh = " ".join(tien_trinh.cmdline()).lower()
                if tep in lenh:
                    return True, tien_trinh.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False, None

    def theo_doi():
        print(f"Bắt đầu theo dõi file: '{ten_tep}'...")
        trang_thai_truoc = False
        pid_cuoi = None

        try:
            while not co_dung.is_set():
                trang_thai_hien_tai, pid = kiem_tra_tien_trinh(ten_tep)
                
                if trang_thai_hien_tai != trang_thai_truoc:
                    if trang_thai_hien_tai:
                        pid_cuoi = pid
                        print(f"[PHÁT HIỆN] File đang được mở bởi PID {pid}")
                        print(f"[CHI TIẾT] Ứng dụng: {psutil.Process(pid).name()}")
                    else:
                        print(f"[ĐÓNG FILE] Không còn hoạt động")
                        pid_cuoi = None
                        break
                    trang_thai_truoc = trang_thai_hien_tai

                time.sleep(0.5)

        finally:
            if pid_cuoi is not None:
                try:
                    tien_trinh = psutil.Process(pid_cuoi)
                    tien_trinh.terminate()
                    print(f"\n Đã dừng tiến trình {pid_cuoi}")
                except psutil.NoSuchProcess:
                    print(f"\n Tiến trình {pid_cuoi} không tồn tại")

    theo_doi()
    xoa_file(tep_tam)