# 🔒 F.P.F.C - File Protection From Copying

## 📝 Giới thiệu
F.P.F.C là một ứng dụng đa nền tảng được thiết kế để bảo vệ và chuyển đổi file, có sẵn ở hai phiên bản: Desktop và Web. Ứng dụng cung cấp các tính năng bảo mật mạnh mẽ và giao diện người dùng thân thiện.

## 💻 Phiên bản Desktop

### 🎯 Giới thiệu
Phiên bản Desktop là giải pháp bảo mật toàn diện với khả năng:
- Mã hóa và giải mã file với độ bảo mật cao
- Chống sao chép và đánh cắp dữ liệu trong thời gian thực
- Hỗ trợ xử lý file có dung lượng lớn
- Theo dõi và ghi log các hoạt động xem file
- Tích hợp công nghệ nhận diện khuôn mặt

### ⚡ Tính năng chính
- 🔐 Mã hóa và giải mã file với thuật toán AES-256
- 📁 Hỗ trợ đa dạng định dạng file (PDF, DOCX, XLSX, JPG, PNG, etc.)
- 🎨 Giao diện người dùng hiện đại với Material Design
- 🖱️ Tính năng kéo thả file (Drag & Drop) trực quan
- 🛡️ Bảo vệ file chống sao chép với cơ chế khóa màn hình
- 📊 Theo dõi và quản lý file với thống kê chi tiết
- 👤 Hỗ trợ nhận diện khuôn mặt với độ chính xác cao
- 🔄 Tự động cập nhật và kiểm tra phiên bản mới

### 💾 Yêu cầu hệ thống
- Python 3.7 trở lên
- Windows 7/10/11
- Webcam (cho tính năng nhận diện khuôn mặt)

### 🛠️ Cài đặt
1. Clone repository này về máy của bạn
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### 📂 Cấu trúc thư mục
- `main.py`: File chính của ứng dụng, xử lý giao diện và điều phối các module
- `ma_hoa.py`: Module xử lý mã hóa với AES-256
- `giai_ma.py`: Module xử lý giải mã và kiểm tra tính toàn vẹn
- `lay_key.py`: Module quản lý và xác thực khóa
- `tao_key.py`: Module tạo và lưu trữ khóa an toàn
- `nhan_dien_mat.py`: Module nhận diện khuôn mặt sử dụng OpenCV
- `chong_sao_chep.py`: Module bảo vệ chống sao chép với cơ chế khóa màn hình
- `theo_doi_luu_file.py`: Module theo dõi và ghi log hoạt động lưu file
- `theo_doi_file_dang_chay.py`: Module giám sát file đang được mở
- `assets/`: Thư mục chứa tài nguyên (hình ảnh, icon, font chữ)

### 📱 Sử dụng

#### 👤 Người gửi
1. Chạy file `main.py`
2. Nhận mã máy từ người nhận
3. Chọn file cần mã hóa bằng cách:
   - Nhấn nút "Chọn file"
   - Hoặc kéo thả file vào vùng quy định
4. Nhập mã máy của người nhận vào ô nhập key
5. Nhấn nút "Mã hóa" để mã hóa file
6. Gửi file đã mã hóa cho người nhận

#### 👥 Người nhận
1. Chạy file `main.py`
2. Nhấn nút "Sao chép key máy" để lấy mã máy của mình
3. Gửi mã máy này cho người gửi
4. Khi nhận được file đã mã hóa:
   - Chọn file đã mã hóa trong phần mềm
   - Nhấn nút "Mở" để giải mã và mở file
   - Xác thực bằng nhận diện khuôn mặt (nếu được yêu cầu)

### 🔒 Bảo mật
- Sử dụng AES-256 cho mã hóa với độ bảo mật cao
- Khóa được lưu trữ an toàn với mã hóa bổ sung
- Hỗ trợ xác thực hai yếu tố (2FA) bằng nhận diện khuôn mặt
- Bảo vệ chống sao chép trái phép với cơ chế khóa màn hình
- Ghi log chi tiết các hoạt động truy cập file

## 🌐 Phiên bản Web

### 🎯 Giới thiệu
Phiên bản Web của F.P.F.C cung cấp giải pháp mã hóa file nhanh chóng và tiện lợi thông qua trình duyệt web.

### ⚡ Tính năng chính
- 🔐 Mã hóa file với AES-256-CBC
- 📁 Hỗ trợ đa dạng định dạng file
- 🗑️ Tự động xóa file sau khi tải xuống
- 📏 Giới hạn kích thước file (25MB)
- 🔑 Bảo mật với Base64 key
- 🌈 Giao diện responsive, thân thiện với mobile

### 💾 Yêu cầu hệ thống
- Python 3.7 trở lên
- Flask và các thư viện phụ thuộc
- Trình duyệt web hiện đại (Chrome, Firefox, Edge)
- Kết nối internet ổn định

### 🛠️ Cài đặt
1. Clone repository này về máy của bạn
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### 📂 Cấu trúc thư mục
- `app.py`: File chính của ứng dụng Flask, xử lý routing và logic
- `templates/`: Thư mục chứa các file HTML với giao diện responsive
- `static/`: Thư mục chứa CSS, JavaScript và các tài nguyên tĩnh
- `uploads/`: Thư mục lưu trữ tạm thời các file được tải lên

### 📱 Sử dụng
1. Chạy ứng dụng:
```bash
python app.py
```
2. Truy cập ứng dụng qua trình duyệt tại địa chỉ: `http://localhost:5000`
3. Chọn file cần mã hóa (tối đa 25MB)
4. Nhập khóa mã hóa (phải là chuỗi Base64 hợp lệ)
5. Nhấn nút mã hóa
6. Tải xuống file đã mã hóa

### 🔒 Bảo mật
- Sử dụng AES-256-CBC cho mã hóa
- Tự động xóa file sau khi tải xuống
- Kiểm tra tính hợp lệ của khóa
- Giới hạn kích thước file
- Sử dụng secure_filename để ngăn chặn path traversal
- Bảo vệ chống CSRF và XSS

### 🔌 API Endpoints
- `GET /`: Trang chủ với giao diện người dùng
- `POST /encrypt`: Endpoint mã hóa file
- `GET /download/<filename>`: Endpoint tải xuống file đã mã hóa

## ℹ️ Thông tin chung

### 👨‍💻 Tác giả
- berN4tz (bennyzzz1909@gmail.com) (4txinhvaio)

### 📄 Giấy phép
- Phiên bản 4.0

### ⚠️ Lưu ý
- Khuyến nghị sử dụng phiên bản Desktop cho cả tác vụ mã hóa và mở file đã mã hóa
- Phiên bản Web phù hợp cho việc mã hóa nhanh file có dung lượng không quá 25MB
- Đảm bảo lưu trữ khóa mã hóa an toàn
- Thường xuyên cập nhật phần mềm để có các tính năng bảo mật mới nhất
