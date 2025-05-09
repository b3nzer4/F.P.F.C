import os
import time
import psutil  
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from kiem_tra_xoa_file import *

def theo_doi_luu_file(stop_flag):
    
    def tach_xau(s):
        last_backslash_index = s.rfind('\\')
        if last_backslash_index == -1:
            return s
        return s[last_backslash_index + 1:]

    def xoa_file(duong_dan):
        try:
            # Thêm bước chuẩn hóa đường dẫn
            duong_dan = os.path.normpath(duong_dan)
            if not ("C:\\data_F.P.F.C" in duong_dan) and os.path.exists(duong_dan):
                os.remove(duong_dan)
                print(f"Đã xóa thành công: {duong_dan}")
        except Exception as e:
            print(f"Lỗi khi xóa file {duong_dan}: {str(e)}")

    # Các định dạng file ảnh hợp lệ
    DINH_DANG_FILE = {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",".doc", ".docx",
        ".xls", ".xlsx",".ppt", ".pptx",".pdf", ".png", ".jpg", ".jpeg", ".gif",
        ".bmp", ".svg", ".tiff", ".webp",".mp4", ".mp3", # Hình ảnh
        ".txt", ".odt", ".rtf", ".md", ".tex",  # Văn bản
        ".csv", ".ods",  # Bảng tính
        ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm",  # Video
        ".wav", ".aac", ".flac", ".ogg", ".m4a",  # Âm thanh
        ".zip", ".rar", ".7z", ".tar", ".gz", ".iso",  # File nén
        ".bin", ".exe", ".dll", ".apk", ".deb", ".dmg", ".pkg", ".msi"
    }

    def check(path):
        _, extension = os.path.splitext(path)
        return extension.lower() in DINH_DANG_FILE

    def xu_ly_file_moi(event):
        try:
            src_path = event.src_path
            
            if os.name == 'nt':
                if isinstance(src_path, bytes):
                    src_path = src_path.decode('utf-8', errors='replace')
                src_path = os.path.abspath(src_path)
            
            if not ("C:\\data_F.P.F.C" in src_path) and check(src_path):
                print(f"Phát hiện file mới: {src_path}")
                ten_file=tach_xau(src_path)
                kiem_tra_xoa_file(ten_file)
                xoa_file(src_path)
                
        except UnicodeDecodeError:
            print(f"Lỗi decoding đường dẫn: {event.src_path}")
        except Exception as e:
            print(f"Lỗi xử lý file: {str(e)}")

    def lay_danh_sach_o_dia():
        o_dia = []
        for partition in psutil.disk_partitions():
            if os.name == 'nt':
                o_dia.append(partition.device)
            else:
                o_dia.append(partition.mountpoint)
        return o_dia

    def theo_doi_thu_muc(thu_muc_goc):
        print(f"Theo dõi thư mục: {thu_muc_goc}")
        observer = Observer()
        event_handler = FileSystemEventHandler()
        event_handler.on_created = xu_ly_file_moi
        observer.schedule(event_handler, thu_muc_goc, recursive=True)
        observer.start()
        return observer

    try:
        danh_sach_o_dia = lay_danh_sach_o_dia()
        observers = []
        for o_dia in danh_sach_o_dia:
            observer = theo_doi_thu_muc(o_dia)
            observers.append(observer)

        # Chờ đến khi stop_flag được set
        while not stop_flag.is_set():
            time.sleep(2)

        # Dừng tất cả Observer khi stop_flag được set
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()

    except KeyboardInterrupt:
        print("\nDừng theo dõi do ngắt từ bàn phím.")
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()
    except Exception as e:
        print(f"Lỗi không mong muốn: {str(e)}")
    finally:
        # Đảm bảo dọn dẹp ngay cả khi có lỗi
        for observer in observers:
            if observer.is_alive():
                observer.stop()
                observer.join()