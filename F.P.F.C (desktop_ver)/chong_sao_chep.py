import win32clipboard as clipboard
import time
import logging

def chong_sao_chep(stop_flag):
    """
    Ngăn chặn sao chép bằng cách liên tục xóa clipboard.
    
    Args:
        stop_flag: Cờ tín hiệu để dừng vòng lặp xóa clipboard
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    def xoa():
        """Xóa nội dung clipboard hiện tại."""
        try:
            clipboard.OpenClipboard()
            clipboard.EmptyClipboard()
            clipboard.CloseClipboard()
            return True
        except Exception as e:
            logging.error(f"Lỗi khi thao tác clipboard: {e}")
            try:
                clipboard.CloseClipboard()
            except:
                pass  # Bỏ qua nếu clipboard đã đóng
            return False

    try:
        interval = 0.1  # Thời gian nghỉ giữa các lần xóa (giây)
        logging.info("Bắt đầu chống sao chép...")
        
        while not stop_flag.is_set():
            xoa()
            time.sleep(interval)
            
        logging.info("Đã dừng chống sao chép")
    except KeyboardInterrupt:
        logging.info("Ngắt bởi người dùng")
    except Exception as e:
        logging.error(f"Lỗi không mong đợi: {e}")
