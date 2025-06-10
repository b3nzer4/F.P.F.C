import psutil
import time
import os
from giai_ma import *

def theo_doi_file_dang_chay(stop_event, current_file, selected_format):
    def xoa_file(duong_dan):
        try:
            if os.path.exists(duong_dan):
                os.remove(duong_dan)
                print(f"Đã xóa tệp: {duong_dan}")
            else:
                print(f"Tệp không tồn tại: {duong_dan}")
        except Exception as e:
            print(f"Lỗi khi xóa tệp: {e}")

    lmao, file_name = giai_ma(current_file, selected_format)
    def check_file_process(target):
        target = target.lower()
        for proc in psutil.process_iter():
            try:
                cmdline = " ".join(proc.cmdline()).lower()
                if target in cmdline:
                    return True, proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False, None

    def theo_doi():
        print(f"Bắt đầu theo dõi file: '{file_name}'...")
        previous_status = False
        last_pid = None

        try:
            while not stop_event.is_set():
                current_status, pid = check_file_process(file_name)
                
                if current_status != previous_status:
                    if current_status:
                        last_pid = pid
                        print(f"[PHÁT HIỆN] File đang được mở bởi PID {pid}")
                        print(f"[CHI TIẾT] Ứng dụng: {psutil.Process(pid).name()}")
                    else:
                        print(f"[ĐÓNG FILE] Không còn hoạt động")
                        last_pid = None
                        break
                    previous_status = current_status

                time.sleep(0.5)  # Giảm CPU usage

        finally:
            # Xử lý dừng tiến trình khi nhận stop_event
            if last_pid is not None:
                try:
                    proc = psutil.Process(last_pid)
                    proc.terminate()
                    print(f"\n Đã dừng tiến trình {last_pid}")
                except psutil.NoSuchProcess:
                    print(f"\n Tiến trình {last_pid} không tồn tại")

    theo_doi()
    xoa_file(lmao)