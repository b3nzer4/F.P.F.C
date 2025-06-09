from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional, Tuple
import logging
import subprocess
from lay_key import key_giai_maa

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def giai_ma(file_giai_ma: str, dinh_dang_file: str) -> Optional[Tuple[str, str]]:
    """
    Giải mã file đã được mã hóa.
    
    Args:
        file_giai_ma: Đường dẫn file cần giải mã
        dinh_dang_file: Định dạng file sau khi giải mã
        
    Returns:
        Optional[Tuple[str, str]]: Tuple chứa (đường dẫn file đã giải mã, tên file) nếu thành công,
                                 None nếu thất bại
    """
    try:
        # Lấy key từ module lay_key
        key = base64.b64decode(key_giai_maa)
        
        # Tạo thư mục ẩn nếu chưa tồn tại
        dir_path = "C:/data_F.P.F.C"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            subprocess.run(["attrib", "+H", dir_path], check=True)
            logger.info(f"Đã tạo thư mục ẩn {dir_path}")
        
        # Tạo tên file output
        file_name = os.path.splitext(os.path.basename(file_giai_ma))[0] + "." + dinh_dang_file
        output_file = os.path.join(dir_path, file_name)
        
        # Giải mã file
        if decrypt_file(file_giai_ma, output_file, key):
            # Mở file sau khi giải mã
            os.startfile(output_file)
            return output_file, file_name
            
        return None
        
    except Exception as e:
        logger.error(f"Lỗi khi giải mã file: {e}")
        return None

def check_key(input_file_path: str, key: bytes) -> bool:
    """
    Kiểm tra tính hợp lệ của khóa bằng cách thử giải mã một phần file.
    
    Args:
        input_file_path: Đường dẫn file cần kiểm tra
        key: Khóa giải mã
        
    Returns:
        bool: True nếu khóa hợp lệ, False nếu không
    """
    try:
        with open(input_file_path, 'rb') as input_file:
            iv = input_file.read(16)
            encrypted_data = input_file.read(32)  # Chỉ đọc 32 bytes đầu tiên
            
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return len(decrypted_data) > 0
        
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra khóa: {e}")
        return False

def decrypt_file(input_file_path: str, output_file_path: str, key: bytes) -> bool:
    """
    Giải mã file sử dụng AES-256-CBC.
    
    Args:
        input_file_path: Đường dẫn file cần giải mã
        output_file_path: Đường dẫn file đầu ra
        key: Khóa giải mã
        
    Returns:
        bool: True nếu giải mã thành công, False nếu thất bại
    """
    try:
        if not check_key(input_file_path, key):
            logger.error("Khóa không chính xác! Không thể giải mã.")
            return False
            
        if not os.path.exists(input_file_path):
            logger.error(f"File {input_file_path} không tồn tại.")
            return False
            
        # Đọc file đã mã hóa
        with open(input_file_path, 'rb') as input_file:
            iv = input_file.read(16)
            encrypted_data = input_file.read()
            
        # Khởi tạo Cipher
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Giải mã theo chunks để tiết kiệm bộ nhớ
        chunk_size = 1024 * 1024  # 1MB chunks
        total_size = len(encrypted_data)
        
        with open(output_file_path, 'wb') as output_file:
            for i in range(0, total_size, chunk_size):
                chunk = encrypted_data[i:i + chunk_size]
                decrypted_chunk = decryptor.update(chunk)
                
                # Xử lý padding cho chunk cuối cùng
                if i + chunk_size >= total_size:
                    padding_length = decrypted_chunk[-1]
                    decrypted_chunk = decrypted_chunk[:-padding_length]
                    
                output_file.write(decrypted_chunk)
                
            # Finalize decryption
            output_file.write(decryptor.finalize())
            
        logger.info(f"File đã được giải mã và lưu tại {output_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi giải mã file: {e}")
        # Xóa file output nếu có lỗi
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        return False

def lay_sau_dau_slash(input_str):

    last_slash_index = input_str.rfind('/')
    if last_slash_index == -1:
        return ""  # Trả về chuỗi rỗng nếu không có dấu '/'
    return input_str[last_slash_index + 1:]

def kq(input_str):
    last_slash_index = input_str.rfind('.')
    if last_slash_index == -1:
        return input_str  # Trả về chuỗi gốc nếu không có dấu '/'
    return input_str[:last_slash_index]

def mo_file(file_path):
    os.startfile(file_path)
