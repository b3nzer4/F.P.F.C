from flask import Flask, render_template, request, send_file, jsonify, session
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import base64
from werkzeug.utils import secure_filename
import urllib.parse

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_very_secret_key_fallback')

# Cấu hình upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Giới hạn kích thước file (25MB)
MAX_CONTENT_LENGTH = 25 * 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def is_valid_key(key):
    try:
        # Kiểm tra xem key có phải là base64 hợp lệ không
        decoded_key = base64.b64decode(key)
        # Thêm kiểm tra độ dài key cho AES-256
        return len(decoded_key) == 32
    except:
        return False

def encrypt_data(data, key):
    """Mã hóa dữ liệu sử dụng AES-256-CBC với PKCS7 padding và IV ngẫu nhiên"""
    # Tạo một vector khởi tạo (IV) ngẫu nhiên (16 bytes)
    iv = os.urandom(16)
    
    # Khởi tạo Cipher AES với chế độ CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Sử dụng PKCS#7 padding
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Kết hợp IV và dữ liệu mã hóa
    return iv + encrypted_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'file' not in request.files:
        return jsonify({'error': 'Không tìm thấy file'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Không có file được chọn'}), 400
    
    key_base64 = request.form.get('key', '')
    if not key_base64 or not is_valid_key(key_base64):
        return jsonify({'error': 'Key không hợp lệ. Key phải là chuỗi Base64 hợp lệ và giải mã ra 32 bytes.'}), 400
    
    try:
        # Giải mã key Base64 thành bytes (32 bytes)
        key = base64.b64decode(key_base64)
        
        # Lấy tên file gốc và đuôi file
        original_filename = file.filename
        name, extension = os.path.splitext(original_filename)
        extension = extension[1:]  # Bỏ dấu chấm ở đầu đuôi file
        
        # Tạo tên file mới với format: tênfile(đuôi).bin
        encrypted_filename = f"{name}({extension}).bin"
        
        # Tạo tên file an toàn cho việc lưu trữ trên server
        safe_filename = secure_filename(encrypted_filename)
        encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

        # Lưu tên file gốc vào session
        if 'original_filenames' not in session:
            session['original_filenames'] = {}
        session['original_filenames'][safe_filename] = encrypted_filename
        session.modified = True

        # Đọc dữ liệu từ file tải lên
        file_data = file.read()
        
        # Mã hóa dữ liệu
        encrypted_file_data = encrypt_data(file_data, key)

        # Lưu file đã mã hóa
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_file_data)

        return jsonify({'filename': safe_filename})

    except Exception as e:
        return jsonify({'error': f'Lỗi khi mã hóa file: {str(e)}'}), 500

@app.route('/download/<filename>')
def download(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Lấy tên file gốc từ session
        original_filename = session.get('original_filenames', {}).get(filename, filename)
        
        # Gửi file và xóa sau khi gửi xong
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=original_filename
        )
        
        # Thêm callback để xóa file sau khi gửi xong
        @response.call_on_close
        def delete_file():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Lỗi khi xóa file: {str(e)}") # In lỗi ra console nếu không xóa được
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Lỗi khi tải file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 