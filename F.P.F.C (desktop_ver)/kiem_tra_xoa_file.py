import psutil

def kiem_tra_xoa_file(file_name):
    """
    Kiểm tra và kết thúc các tiến trình đang sử dụng file được chỉ định.
    
    Args:
        file_name (str): Tên file cần kiểm tra
    """
    # Tìm các tiến trình đang sử dụng file
    target = file_name.lower()
    
    try:
        # Sử dụng list comprehension để tìm các tiến trình
        pids = [
            proc.pid for proc in psutil.process_iter(['pid', 'cmdline'])
            if proc.info['cmdline'] and target in " ".join(proc.info['cmdline']).lower()
        ]
        
        if pids:
            # Kết thúc các tiến trình
            for pid in pids:
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()
                    print(f"Terminated process with PID {pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    print(f"Error terminating PID {pid}: {e}")
        else:
            print("No processes found using the file.")
            
    except Exception as e:
        print(f"Error while searching for processes: {e}")
