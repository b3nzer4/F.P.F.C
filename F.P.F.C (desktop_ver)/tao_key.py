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
logger = logging.getLogger(__name__)

def get_hardware_info() -> List[str]:
    """
    Lấy thông tin phần cứng của máy tính.
    
    Returns:
        List[str]: Danh sách các thông tin phần cứng
    """
    hardware_info = []
    
    try:
        c = wmi.WMI()
        
        # Lấy thông tin CPU
        for cpu in c.Win32_Processor():
            if cpu.ProcessorId:
                hardware_info.append(cpu.ProcessorId.strip())
                
        # Lấy thông tin Mainboard
        for board in c.Win32_BaseBoard():
            if board.SerialNumber:
                hardware_info.append(board.SerialNumber.strip())
                
        # Lấy thông tin ổ cứng
        for disk in c.Win32_DiskDrive():
            if disk.SerialNumber:
                hardware_info.append(disk.SerialNumber.strip())
                
        # Lấy thông tin BIOS
        for bios in c.Win32_BIOS():
            if bios.SerialNumber:
                hardware_info.append(bios.SerialNumber.strip())
                
        # Lấy thông tin Windows Product ID
        for os_info in c.Win32_OperatingSystem():
            if os_info.SerialNumber:
                hardware_info.append(os_info.SerialNumber.strip())
                
    except Exception as e:
        logger.error(f"Lỗi khi lấy thông tin phần cứng: {e}")
    
    # Thêm MAC address
    hardware_info.append(str(uuid.getnode()))
    
    return hardware_info

def store_key_securely(key: bytes) -> bool:
    """
    Lưu key an toàn sử dụng Windows DPAPI.
    
    Args:
        key: Key cần lưu (bytes)
        
    Returns:
        bool: True nếu lưu thành công, False nếu thất bại
    """
    try:
        # Tạo entropy từ thông tin phần cứng
        entropy = ''.join(get_hardware_info()).encode()
        
        # Mã hóa key với DPAPI
        encrypted_key = win32crypt.CryptProtectData(
            key,
            "F.P.F.C Security Key",
            entropy,
            None,
            None,
            0
        )
        
        # Tạo thư mục nếu chưa tồn tại
        key_file = os.path.join(os.environ['LOCALAPPDATA'], 'F.P.F.C', 'security.key')
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        
        # Lưu key đã mã hóa
        with open(key_file, 'wb') as f:
            f.write(encrypted_key)
            
        logger.info("Đã lưu key thành công")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi lưu key: {e}")
        return False

def generate_hardware_key() -> Optional[str]:
    """
    Tạo key dựa trên thông tin phần cứng.
    
    Returns:
        Optional[str]: Key dạng base64 nếu thành công, None nếu thất bại
    """
    try:
        hardware_info = get_hardware_info()
        
        if not hardware_info:
            logger.error("Không thể lấy thông tin phần cứng")
            return None
            
        # Kết hợp thông tin phần cứng
        combined_info = ''.join(hardware_info)
        
        # Tạo hash từ thông tin phần cứng
        hash_object = hashlib.sha256(combined_info.encode())
        hardware_key = hash_object.digest()
        
        # Đảm bảo key có độ dài 32 bytes
        if len(hardware_key) != 32:
            while len(hardware_key) < 32:
                hardware_key += hash_object.digest()
            hardware_key = hardware_key[:32]
        
        # Lưu key an toàn
        if store_key_securely(hardware_key):
            return base64.b64encode(hardware_key).decode('utf-8')
            
        return None
        
    except Exception as e:
        logger.error(f"Lỗi khi tạo key: {e}")
        return None

if __name__ == "__main__":
    key = generate_hardware_key()
    if key:
        logger.info("Đã tạo và lưu key bảo mật")
        messagebox.showinfo("F.P.F.C", "Đã tạo và lưu key bảo mật")
    else:
        logger.error("Không thể lưu key bảo mật")
        messagebox.showerror("F.P.F.C", "Không thể lưu key bảo mật")
