import winreg
import uuid
import getpass
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.fernet import Fernet

def key_giai_ma():
    # Lấy thông tin máy để tạo đường dẫn registry giống như trong tao_key.py
    machine_id = str(uuid.getnode())
    username = getpass.getuser()
    
    # Sử dụng cùng đường dẫn registry phức tạp như trong tao_key.py
    registry_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run\\Services\\{machine_id[-6:]}"
    key_name = f"SystemService_{username[:2]}{len(username)}"

    try:
        # Mở Registry và lấy giá trị key đã mã hóa
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_READ)
        encrypted_key, _ = winreg.QueryValueEx(reg_key, key_name)
        winreg.CloseKey(reg_key)
        
        # Giải mã key
        machine_salt = machine_id.encode()
        decryption_key = derive_key_from_machine(machine_salt)
        fernet = Fernet(decryption_key)
        stored_key = fernet.decrypt(encrypted_key.encode()).decode('utf-8')
        
        return stored_key
    except FileNotFoundError:
        print("Không tìm thấy key trong Registry. Đảm bảo key đã được tạo trước đó.")
    except (PermissionError, ValueError) as e:
        print(f"Lỗi khi giải mã key: {e}")
    except Exception as e:
        print(f"Lỗi khi lấy key từ Registry: {e}")
    return None

# Hàm tạo key từ thông tin máy tính - giống như trong tao_key.py
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

# Sử dụng hàm để lấy key từ Registry
key_giai_maa = key_giai_ma()

