import wmi
import hashlib
import platform
import uuid
import getpass
import base64
from tkinter import messagebox
import os
import win32crypt
import win32security
import logging
from typing import List, Optional

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
ghi_log = logging.getLogger(__name__)

def lay_thong_tin_phan_cung() -> List[str]:
    """
    Lấy thông tin phần cứng của máy tính.
    
    Returns:
        List[str]: Danh sách các thông tin phần cứng
    """
    thong_tin = []
    
    try:
        wmi_obj = wmi.WMI()
        
        # Lấy thông tin CPU
        for cpu in wmi_obj.Win32_Processor():
            if cpu.ProcessorId:
                thong_tin.append(cpu.ProcessorId.strip())
                
        # Lấy thông tin Mainboard
        for board in wmi_obj.Win32_BaseBoard():
            if board.SerialNumber:
                thong_tin.append(board.SerialNumber.strip())
                
        # Lấy thông tin ổ cứng
        for disk in wmi_obj.Win32_DiskDrive():
            if disk.SerialNumber:
                thong_tin.append(disk.SerialNumber.strip())
                
        # Lấy thông tin BIOS
        for bios in wmi_obj.Win32_BIOS():
            if bios.SerialNumber:
                thong_tin.append(bios.SerialNumber.strip())
                
        # Lấy thông tin Windows Product ID
        for os_info in wmi_obj.Win32_OperatingSystem():
            if os_info.SerialNumber:
                thong_tin.append(os_info.SerialNumber.strip())
                
    except Exception as e:
        ghi_log.error(f"Lỗi khi lấy thông tin phần cứng: {e}")
    
    # Thêm MAC address
    thong_tin.append(str(uuid.getnode()))
    
    return thong_tin

def luu_key(key: bytes) -> bool:
    """
    Lưu key an toàn sử dụng Windows DPAPI.
    
    Args:
        key: Key cần lưu (bytes)
        
    Returns:
        bool: True nếu lưu thành công, False nếu thất bại
    """
    try:
        # Tạo entropy từ thông tin phần cứng
        entropy = ''.join(lay_thong_tin_phan_cung()).encode()
        
        # Mã hóa key với DPAPI
        key_da_ma = win32crypt.CryptProtectData(
            key,
            "F.P.F.C Security Key",
            entropy,
            None,
            None,
            0
        )
        
        # Tạo thư mục nếu chưa tồn tại
        duong_dan = os.path.join(os.environ['LOCALAPPDATA'], 'F.P.F.C', 'security.key')
        os.makedirs(os.path.dirname(duong_dan), exist_ok=True)
        
        # Lưu key đã mã hóa
        with open(duong_dan, 'wb') as f:
            f.write(key_da_ma)
            
        ghi_log.info("Đã lưu key thành công")
        return True
        
    except Exception as e:
        ghi_log.error(f"Lỗi khi lưu key: {e}")
        return False

def tao_key() -> Optional[str]:
    """
    Tạo key dựa trên thông tin phần cứng.
    
    Returns:
        Optional[str]: Key dạng base64 nếu thành công, None nếu thất bại
    """
    try:
        thong_tin = lay_thong_tin_phan_cung()
        
        if not thong_tin:
            ghi_log.error("Không thể lấy thông tin phần cứng")
            return None
            
        # Kết hợp thông tin phần cứng
        thong_tin_hop = ''.join(thong_tin)
        
        # Tạo hash từ thông tin phần cứng
        hash_obj = hashlib.sha256(thong_tin_hop.encode())
        key = hash_obj.digest()
        
        # Đảm bảo key có độ dài 32 bytes
        if len(key) != 32:
            while len(key) < 32:
                key += hash_obj.digest()
            key = key[:32]
        
        # Lưu key an toàn
        if luu_key(key):
            return base64.b64encode(key).decode('utf-8')
            
        return None
        
    except Exception as e:
        ghi_log.error(f"Lỗi khi tạo key: {e}")
        return None

if __name__ == "__main__":
    key = tao_key()
    if key:
        ghi_log.info("Đã tạo và lưu key bảo mật")
        messagebox.showinfo("F.P.F.C", "Đã tạo và lưu key bảo mật")
    else:
        ghi_log.error("Không thể lưu key bảo mật")
        messagebox.showerror("F.P.F.C", "Không thể lưu key bảo mật")
