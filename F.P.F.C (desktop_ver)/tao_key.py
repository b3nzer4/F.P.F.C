from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.fernet import Fernet
import os
import base64
import winreg
import uuid
import getpass
from tkinter import messagebox

# Hàm tạo và lưu key vào Registry với bảo mật nâng cao
def generate_and_store_key():
    # Tạo đường dẫn registry phức tạp hơn và ít dự đoán hơn
    machine_id = str(uuid.getnode())  # Lấy MAC address làm machine ID
    username = getpass.getuser()
    
    # Tạo một registry path phức tạp hơn, khó đoán hơn
    registry_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run\\Services\\{machine_id[-6:]}"
    key_name = f"SystemService_{username[:2]}{len(username)}"

    # Kiểm tra xem key đã tồn tại trong Registry hay chưa
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_READ)
        encrypted_key, _ = winreg.QueryValueEx(reg_key, key_name)
        winreg.CloseKey(reg_key)
        
        # Giải mã key đã lưu
        machine_salt = machine_id.encode()
        decryption_key = derive_key_from_machine(machine_salt)
        fernet = Fernet(decryption_key)
        stored_key = fernet.decrypt(encrypted_key.encode()).decode('utf-8')
        
        print("Key đã tồn tại trong Registry")
        return stored_key
    except (FileNotFoundError, PermissionError, ValueError):
        pass  # Nếu không tìm thấy hoặc lỗi giải mã, tiếp tục tạo key mới

    # Tạo key ngẫu nhiên
    key = os.urandom(32)  # 32 bytes tương đương 256-bit key
    key_b64 = base64.b64encode(key).decode('utf-8')

    # Mã hóa key trước khi lưu
    machine_salt = machine_id.encode()
    encryption_key = derive_key_from_machine(machine_salt)
    fernet = Fernet(encryption_key)
    encrypted_key = fernet.encrypt(key_b64.encode()).decode('utf-8')

    # Lưu key đã mã hóa vào Registry
    try:
        # Tạo registry key nếu chưa tồn tại
        reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path)
        winreg.SetValueEx(reg_key, key_name, 0, winreg.REG_SZ, encrypted_key)
        winreg.CloseKey(reg_key)
        print("Key đã được tạo và lưu vào Registry an toàn")
    except Exception as e:
        print(f"Lỗi khi lưu key vào Registry: {e}")
        return None

    return key_b64

# Hàm tạo key từ thông tin máy tính
def derive_key_from_machine(salt):
    # Lấy thông tin cố định từ máy để tạo key
    username = getpass.getuser().encode()
    
    # Sử dụng HKDF để tạo key từ thông tin máy
    kdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=username
    )
    derived_key = kdf.derive(username)
    return base64.urlsafe_b64encode(derived_key)

# Gọi hàm tạo và lưu key
if __name__ == "__main__":
    generate_and_store_key()
    messagebox.showinfo("F.P.F.C","Đã tạo một key và lưu vào thiết bị an toàn")
