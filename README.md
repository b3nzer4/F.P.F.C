# F.P.F.C - File Protection From Copying

## Giới thiệu
F.P.F.C là một ứng dụng đa nền tảng được thiết kế để bảo vệ và chuyển đổi file, có sẵn ở hai phiên bản: Desktop và Web. Ứng dụng cung cấp các tính năng bảo mật mạnh mẽ và giao diện người dùng thân thiện.

## Phiên bản Desktop

### Giới thiệu
Phiên ban Desktop có khả năng mã hóa file và mở file đồng thời chống hành động sao chép đánh cắp dữ liệu.Có khả năng mã hóa file dung lượng lớn, và theo dõi hành động khi xem file

### Tính năng chính
- Mã hóa và giải mã file với AES-256
- Hỗ trợ nhiều định dạng file
- Giao diện người dùng hiện đại và thân thiện
- Tính năng kéo thả file (Drag & Drop)
- Bảo vệ file chống sao chép
- Theo dõi và quản lý file
- Hỗ trợ nhận diện khuôn mặt

### Yêu cầu hệ thống
- Python 3.7 trở lên
- Windows 10/11

### Cài đặt
1. Clone repository này về máy của bạn
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### Cấu trúc thư mục
- `main.py`: File chính của ứng dụng
- `ma_hoa.py`: Module xử lý mã hóa
- `giai_ma.py`: Module xử lý giải mã
- `lay_key.py`: Module quản lý khóa
- `tao_key.py`: Module tạo khóa
- `nhan_dien_mat.py`: Module nhận diện khuôn mặt
- `chong_sao_chep.py`: Module bảo vệ chống sao chép
- `theo_doi_luu_file.py`: Module theo dõi lưu file
- `theo_doi_file_dang_chay.py`: Module theo dõi file đang chạy
- `assets/`: Thư mục chứa tài nguyên (hình ảnh, icon)

### Sử dụng

#### Người gửi
1. Chạy file `main.py`
2. Nhận mã máy từ người nhận
3. Chọn file cần mã hóa bằng cách nhấn nút "Chọn file"
4. Nhập mã máy của người nhận vào ô nhập key
5. Nhấn nút "Mã hóa" để mã hóa file
6. Gửi file đã mã hóa cho người nhận

#### Người nhận
1. Chạy file `main.py`
2. Nhấn nút "Sao chép key máy" để lấy mã máy của mình
3. Gửi mã máy này cho người gửi
4. Khi nhận được file đã mã hóa:
   - Chọn file đã mã hóa trong phần mềm
   - Nhấn nút "Mở" để giải mã và mở file


### Bảo mật
- Sử dụng AES-256 cho mã hóa
- Khóa được lưu trữ an toàn
- Hỗ trợ xác thực bằng nhận diện khuôn mặt
- Bảo vệ chống sao chép trái phép

## Phiên bản Web

### Giới thiệu
Phiên bản Web của F.P.F.C cho phép người dùng mã hóa file trực tiếp trên nền tảng web

### Tính năng chính
- Mã hóa file với AES-256-CBC
- Hỗ trợ nhiều định dạng file
- Tự động xóa file sau khi tải xuống
- Giới hạn kích thước file (25MB)
- Bảo mật với Base64 key

### Yêu cầu hệ thống
- Python 3.7 trở lên
- Flask và các thư viện phụ thuộc
- Trình duyệt web hiện đại

### Cài đặt
1. Clone repository này về máy của bạn
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### Cấu trúc thư mục
- `app.py`: File chính của ứng dụng Flask
- `templates/`: Thư mục chứa các file HTML
- `static/`: Thư mục chứa CSS, JavaScript và các tài nguyên tĩnh
- `uploads/`: Thư mục lưu trữ tạm thời các file được tải lên

### Sử dụng
1. Chạy ứng dụng:
```bash
python app.py
```
2. Truy cập ứng dụng qua trình duyệt tại địa chỉ: `http://localhost:5000`
3. Chọn file cần mã hóa
4. Nhập khóa mã hóa (phải là chuỗi Base64 hợp lệ)
5. Nhấn nút mã hóa
6. Tải xuống file đã mã hóa

### Bảo mật
- Sử dụng AES-256-CBC cho mã hóa
- Tự động xóa file sau khi tải xuống
- Kiểm tra tính hợp lệ của khóa
- Giới hạn kích thước file
- Sử dụng secure_filename để ngăn chặn path traversal

### API Endpoints
- `GET /`: Trang chủ
- `POST /encrypt`: Mã hóa file
- `GET /download/<filename>`: Tải xuống file đã mã hóa

## Thông tin chung

### Tác giả
- berN4tz (bennyzzz1909@gmail.com) (4txinhvaio)

### Giấy phép
- Phiên bản 4.0

### Lưu ý
- Khuyến nghị sử dụng phiên bản Desktop cho cả tác vụ mã hóa và mở file đã mã hóa
- Phiên bản Web phù hợp cho việc mã hóa nhanh file có dung lượng không quá 25MB
