from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
import os

def ma_hoa(key_dung_de_giai_ma, duong_dan):
    """
    Mã hóa file sử dụng thuật toán AES-256 với chế độ CBC.
    
    Args:
        key_dung_de_giai_ma: Khóa mã hóa dạng Base64
        duong_dan: Đường dẫn tới file cần mã hóa
    """
    try:
        # Giải mã Base64 thành bytes
        key = base64.b64decode(key_dung_de_giai_ma)
        
        if len(key) != 32:  # Đảm bảo rằng key là 32 bytes cho AES-256
            print("Khóa mã hóa phải có độ dài 32 bytes (256-bit).")
            return
            
        # Kiểm tra xem file đầu vào có tồn tại không
        if not os.path.exists(duong_dan):
            print(f"File {duong_dan} không tồn tại.")
            return
            
        # Tạo tên file output
        output_file = tao_ten_file_output(duong_dan)
        print(f"Tên file đã mã hóa: {output_file}")
        
        # Mã hóa file
        encrypt_file(duong_dan, output_file, key)
        
    except base64.binascii.Error:
        print("Lỗi: Khóa không phải định dạng Base64 hợp lệ.")
    except Exception as e:
        print(f"Lỗi khi mã hóa file: {e}")

def encrypt_file(input_file_path, output_file_path, key):
    """
    Mã hóa một file sử dụng AES-256-CBC.
    
    Args:
        input_file_path: Đường dẫn file đầu vào
        output_file_path: Đường dẫn file đầu ra
        key: Khóa mã hóa (32 bytes)
    """
    # Tạo một vector khởi tạo (IV) ngẫu nhiên cho chế độ mã hóa CBC
    iv = os.urandom(16)
    
    # Khởi tạo Cipher AES với chế độ CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Đọc dữ liệu file và mã hóa
    with open(input_file_path, 'rb') as input_file:
        file_data = input_file.read()
        
        # Sử dụng PKCS#7 padding (chuẩn hơn)
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(file_data) + padder.finalize()
        
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Ghi dữ liệu đã mã hóa vào file output
    with open(output_file_path, 'wb') as output_file:
        # Lưu IV vào đầu file mã hóa
        output_file.write(iv)
        output_file.write(encrypted_data)
    
    print(f"File đã được mã hóa và lưu tại {output_file_path}")

def tao_ten_file_output(input_file_path):
    """
    Tạo tên file output từ đường dẫn input.
    
    Args:
        input_file_path: Đường dẫn file đầu vào
        
    Returns:
        Đường dẫn file đầu ra
    """
    # Tách phần đường dẫn, tên file, và đuôi file
    base_dir = os.path.dirname(input_file_path)
    file_name, file_extension = os.path.splitext(os.path.basename(input_file_path))
    # Tạo tên file output với định dạng yêu cầu
    output_file_name = f"{file_name}({file_extension[1:]}).bin"
    return os.path.join(base_dir, output_file_name)
