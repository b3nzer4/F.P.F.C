import psutil

def kiem_tra_xoa_file(file_name):
    def find_processes(target):
        target = target.lower()
        pids = []
        for proc in psutil.process_iter():
            try:
                cmdline = " ".join(proc.cmdline()).lower()
                if target in cmdline:
                    pids.append(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return pids

    def terminate_processes(pids):
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                print(f"Terminated process with PID {pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                print(f"Error terminating PID {pid}: {e}")

    pids = find_processes(file_name)
    if pids:
        terminate_processes(pids)
    else:
        print("No processes found using the file.")
