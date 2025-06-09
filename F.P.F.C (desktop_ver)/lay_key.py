import wmi
import hashlib
import platform
import uuid
import getpass
import base64
import os
import win32crypt
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

def get_stored_key() -> Optional[str]:
    """
    Lấy key đã lưu sử dụng Windows DPAPI.
    
    Returns:
        Optional[str]: Key dạng base64 nếu tìm thấy, None nếu không
    """
    try:
        key_file = os.path.join(os.environ['LOCALAPPDATA'], 'F.P.F.C', 'security.key')
        
        if not os.path.exists(key_file):
            return None
            
        with open(key_file, 'rb') as f:
            encrypted_key = f.read()
            
        entropy = ''.join(get_hardware_info()).encode()
        
        try:
            # Thử giải mã với entropy
            decrypted_key = win32crypt.CryptUnprotectData(
                encrypted_key,
                entropy,
                None,
                None,
                0
            )
        except Exception:
            # Nếu thất bại, thử giải mã không có entropy
            decrypted_key = win32crypt.CryptUnprotectData(
                encrypted_key,
                None,
                None,
                None,
                0
            )
        
        if decrypted_key and len(decrypted_key) > 1:
            return base64.b64encode(decrypted_key[1]).decode('utf-8')
        return None
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy key đã lưu: {e}")
        return None

def key_giai_ma() -> Optional[str]:
    """
    Lấy key dựa trên thông tin phần cứng.
    
    Returns:
        Optional[str]: Key dạng base64 nếu thành công, None nếu thất bại
    """
    try:
        # Thử lấy key đã lưu trước
        stored_key = get_stored_key()
        if stored_key:
            return stored_key

        # Nếu không tìm thấy key đã lưu, tạo key mới
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
        
        return base64.b64encode(hardware_key).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Lỗi khi tạo key từ thông tin phần cứng: {e}")
        return None

# Lấy key khi module được import
key_giai_maa = key_giai_ma()

