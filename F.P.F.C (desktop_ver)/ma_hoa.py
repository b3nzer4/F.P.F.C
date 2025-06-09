from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
import os
from typing import Optional, Tuple
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ma_hoa(key_dung_de_giai_ma: str, duong_dan: str) -> Optional[str]:
    """
    Mã hóa file sử dụng thuật toán AES-256 với chế độ CBC.
    
    Args:
        key_dung_de_giai_ma: Khóa mã hóa dạng Base64
        duong_dan: Đường dẫn tới file cần mã hóa
        
    Returns:
        Optional[str]: Đường dẫn file đã mã hóa nếu thành công, None nếu thất bại
    """
    try:
        # Giải mã Base64 thành bytes
        key = base64.b64decode(key_dung_de_giai_ma)
        
        if len(key) != 32:
            logger.error("Khóa mã hóa phải có độ dài 32 bytes (256-bit)")
            return None
            
        if not os.path.exists(duong_dan):
            logger.error(f"File {duong_dan} không tồn tại")
            return None
            
        output_file = tao_ten_file_output(duong_dan)
        logger.info(f"Tên file đã mã hóa: {output_file}")
        
        if encrypt_file(duong_dan, output_file, key):
            return output_file
        return None
        
    except base64.binascii.Error:
        logger.error("Khóa không phải định dạng Base64 hợp lệ")
        return None
    except Exception as e:
        logger.error(f"Lỗi khi mã hóa file: {e}")
        return None

def encrypt_file(input_file_path: str, output_file_path: str, key: bytes) -> bool:
    """
    Mã hóa một file sử dụng AES-256-CBC.
    
    Args:
        input_file_path: Đường dẫn file đầu vào
        output_file_path: Đường dẫn file đầu ra
        key: Khóa mã hóa (32 bytes)
        
    Returns:
        bool: True nếu mã hóa thành công, False nếu thất bại
    """
    try:
        # Tạo IV ngẫu nhiên
        iv = os.urandom(16)
        
        # Khởi tạo Cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Đọc và mã hóa file theo chunks để tiết kiệm bộ nhớ
        chunk_size = 1024 * 1024  # 1MB chunks
        
        with open(input_file_path, 'rb') as input_file, \
             open(output_file_path, 'wb') as output_file:
            
            # Lưu IV
            output_file.write(iv)
            
            # Khởi tạo padder
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            
            # Đọc và mã hóa từng chunk
            while True:
                chunk = input_file.read(chunk_size)
                if not chunk:
                    break
                    
                # Padding chunk cuối cùng
                if len(chunk) < chunk_size:
                    chunk = padder.update(chunk) + padder.finalize()
                else:
                    chunk = padder.update(chunk)
                    
                # Mã hóa chunk
                encrypted_chunk = encryptor.update(chunk)
                output_file.write(encrypted_chunk)
            
            # Finalize encryption
            output_file.write(encryptor.finalize())
            
        logger.info(f"File đã được mã hóa và lưu tại {output_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi mã hóa file: {e}")
        # Xóa file output nếu có lỗi
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        return False

def tao_ten_file_output(input_file_path: str) -> str:
    """
    Tạo tên file output từ đường dẫn input.
    
    Args:
        input_file_path: Đường dẫn file đầu vào
        
    Returns:
        str: Đường dẫn file đầu ra
    """
    base_dir = os.path.dirname(input_file_path)
    file_name, file_extension = os.path.splitext(os.path.basename(input_file_path))
    output_file_name = f"{file_name}({file_extension[1:]}).bin"
    return os.path.join(base_dir, output_file_name)
