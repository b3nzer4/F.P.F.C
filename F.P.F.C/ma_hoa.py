from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os

def ma_hoa(key_dung_de_giai_ma, duong_dan):
    # Khóa mã hóa cố định (32 bytes cho AES-256) và đã được mã hóa thành Base64
    key_base64 = key_dung_de_giai_ma  # Khóa Base64 giả lập

    # Giải mã Base64 thành bytes
    key = base64.b64decode(key_base64)

    # Hàm mã hóa file
    def encrypt_file(input_file_path, output_file_path):
        if len(key) != 32:  # Đảm bảo rằng key là 32 bytes cho AES-256
            print("Khóa mã hóa phải có độ dài 32 bytes (256-bit).")
            return

        # Kiểm tra xem file đầu vào có tồn tại không
        if not os.path.exists(input_file_path):
            print(f"File {input_file_path} không tồn tại.")
            return

        # Tạo một vector khởi tạo (IV) ngẫu nhiên cho chế độ mã hóa CBC
        iv = os.urandom(16)

        # Khởi tạo Cipher AES với chế độ CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Đọc dữ liệu file và mã hóa
        with open(input_file_path, 'rb') as input_file:
            file_data = input_file.read()

            # Đảm bảo dữ liệu có độ dài là bội số của block size (AES block size = 16 bytes)
            padding_length = 16 - len(file_data) % 16
            padded_data = file_data + bytes([padding_length]) * padding_length

            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Ghi dữ liệu đã mã hóa vào file output
        with open(output_file_path, 'wb') as output_file:
            # Lưu IV vào đầu file mã hóa
            output_file.write(iv)
            output_file.write(encrypted_data)

        print(f"File đã được mã hóa và lưu tại {output_file_path}")

    # Hàm tạo tên file output từ đường dẫn input
    def tao_ten_file_output(input_file_path):
        # Tách phần đường dẫn, tên file, và đuôi file
        base_dir = os.path.dirname(input_file_path)
        file_name, file_extension = os.path.splitext(os.path.basename(input_file_path))
        # Tạo tên file output với định dạng yêu cầu
        output_file_name = f"{file_name}({file_extension[1:]}).bin"
        return os.path.join(base_dir, output_file_name)

    # Chạy mã hóa file
    input_file = duong_dan  # Đường dẫn tới file bạn muốn mã hóa
    output_file = tao_ten_file_output(input_file)  # Đường dẫn lưu file đã mã hóa

    print(f"Tên file đã mã hóa: {output_file}")
    encrypt_file(input_file, output_file)
