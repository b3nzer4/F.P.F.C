import os
import time
import psutil  
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from kiem_tra_xoa_file import *

def theo_doi_luu_file(co_dung):
    def tach_ten(s):
        idx = s.rfind('\\')
        if idx == -1:
            return s
        return s[idx + 1:]

    def xoa_file(duong_dan):
        try:
            duong_dan = os.path.normpath(duong_dan)
            if not ("C:\\data_F.P.F.C" in duong_dan) and os.path.exists(duong_dan):
                os.remove(duong_dan)
                print(f"Đã xóa: {duong_dan}")
        except Exception as e:
            print(f"Lỗi xóa file {duong_dan}: {str(e)}")

    DINH_DANG = {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".doc", ".docx",
        ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".png", ".jpg", ".jpeg", ".gif",
        ".bmp", ".svg", ".tiff", ".webp", ".mp4", ".mp3",
        ".txt", ".odt", ".rtf", ".md", ".tex",
        ".csv", ".ods",
        ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm",
        ".wav", ".aac", ".flac", ".ogg", ".m4a",
        ".zip", ".rar", ".7z", ".tar", ".gz", ".iso",
        ".bin", ".exe", ".dll", ".apk", ".deb", ".dmg", ".pkg", ".msi"
    }

    def hop_le(duong_dan):
        _, ext = os.path.splitext(duong_dan)
        return ext.lower() in DINH_DANG

    def xu_ly_moi(event):
        try:
            src = event.src_path
            if os.name == 'nt':
                if isinstance(src, bytes):
                    src = src.decode('utf-8', errors='replace')
                src = os.path.abspath(src)
            if not ("C:\\data_F.P.F.C" in src) and hop_le(src):
                print(f"Phát hiện file mới: {src}")
                ten = tach_ten(src)
                kiem_tra_xoa_file(ten)
                xoa_file(src)
        except UnicodeDecodeError:
            print(f"Lỗi decoding: {event.src_path}")
        except Exception as e:
            print(f"Lỗi xử lý file: {str(e)}")

    def o_dia():
        ds = []
        for p in psutil.disk_partitions():
            if os.name == 'nt':
                ds.append(p.device)
            else:
                ds.append(p.mountpoint)
        return ds

    def theo_doi_thu_muc(thu_muc):
        print(f"Theo dõi: {thu_muc}")
        obs = Observer()
        handler = FileSystemEventHandler()
        handler.on_created = xu_ly_moi
        obs.schedule(handler, thu_muc, recursive=True)
        obs.start()
        return obs

    try:
        ds_o = o_dia()
        obs = []
        for o in ds_o:
            ob = theo_doi_thu_muc(o)
            obs.append(ob)
        while not co_dung.is_set():
            time.sleep(2)
        for ob in obs:
            ob.stop()
        for ob in obs:
            ob.join()
    except KeyboardInterrupt:
        print("\nDừng theo dõi do ngắt từ bàn phím.")
        for ob in obs:
            ob.stop()
        for ob in obs:
            ob.join()
    except Exception as e:
        print(f"Lỗi không mong muốn: {str(e)}")
    finally:
        for ob in obs:
            if ob.is_alive():
                ob.stop()
                ob.join()