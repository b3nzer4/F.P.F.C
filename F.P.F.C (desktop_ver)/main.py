"""
F.P.F.C - File Protection and File Conversion
Author: berN4tz (bennyzzz1909@gmail.com)
toi don gian la bi simp 4t
"""
from tkinter.filedialog import askopenfilename
import os
from tkinterdnd2 import TkinterDnD, DND_FILES
import customtkinter as ctk
from PIL import Image, ImageTk
from ma_hoa import *
import pyperclip
from lay_key import *
from tkinter import messagebox
from ma_hoa import *
from giai_ma import *
from chay_file import*
import threading
import queue
import time
import random

if __name__ == '__main__':
    # Queue để giao tiếp giữa các thread
    message_queue = queue.Queue()
    active_threads = []
    camera_running = False

    # Cài đặt theme và màu sắc
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Màu sắc tùy chỉnh
    PRIMARY_COLOR = "#1a237e"
    SECONDARY_COLOR = "#0d47a1"
    ACCENT_COLOR = "#2196f3"
    BACKGROUND_COLOR = "#121212"
    TEXT_COLOR = "#ffffff"

    def adjust_window_size(root):
        """Điều chỉnh kích thước cửa sổ với tỉ lệ 4:3"""
        # Lấy độ phân giải màn hình
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Tính toán kích thước cửa sổ với tỉ lệ 4:3
        # Lấy chiều rộng tối đa có thể (80% màn hình)
        max_width = int(screen_width * 0.8)
        # Tính chiều cao tương ứng với tỉ lệ 4:3
        window_height = int(max_width * 3/4)
        
        # Nếu chiều cao vượt quá 80% chiều cao màn hình, lấy chiều cao làm chuẩn
        if window_height > screen_height * 0.8:
            window_height = int(screen_height * 0.8)
            max_width = int(window_height * 4/3)
        
        # Giới hạn kích thước tối thiểu
        window_width = max(max_width, 800)
        window_height = max(window_height, 600)
        
        # Giới hạn kích thước tối đa
        window_width = min(window_width, 1600)
        window_height = min(window_height, 1200)
        
        # Tính toán vị trí để cửa sổ nằm giữa màn hình
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2
        
        # Cập nhật kích thước và vị trí cửa sổ
        geometry_str = f"{window_width}x{window_height}+{position_x}+{position_y}"
        root.geometry(geometry_str)
        
        return window_width, window_height

    def animate_button(button, original_color, hover_color):
        def on_enter(e):
            button.configure(fg_color=hover_color)
        def on_leave(e):
            button.configure(fg_color=original_color)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def animate_progress():
        if progress_bar.winfo_ismapped():
            current_value = progress_bar.get()
            if current_value < 1.0:
                new_value = min(current_value + 0.01, 1.0)
                progress_bar.set(new_value)
                root.after(50, animate_progress)

    def process_queue():
        try:
            while True:
                msg = message_queue.get_nowait()
                if msg['type'] == 'error':
                    messagebox.showerror("Lỗi", msg['message'])
                    progress_bar.pack_forget()  # Ẩn progress bar khi có lỗi
                elif msg['type'] == 'info':
                    messagebox.showinfo("Thông báo", msg['message'])
                    progress_bar.pack_forget()  # Ẩn progress bar khi hoàn thành
                elif msg['type'] == 'progress':
                    progress_bar.set(msg['value'])
                    if msg['value'] >= 1.0:
                        progress_bar.stop()
                        progress_bar.pack_forget()  # Ẩn progress bar khi đạt 100%
                elif msg['type'] == 'camera_status':
                    global camera_running
                    camera_running = msg['status']
                    update_open_button_state()
        except queue.Empty:
            pass
        root.after(100, process_queue)

    def update_open_button_state():
        if camera_running:
            open_button.configure(state="disabled", text="Đang chạy camera...")
            open_button.configure(fg_color="#424242")
        else:
            if current_file and selected_format:
                open_button.configure(state="normal", text="Mở")
                open_button.configure(fg_color=PRIMARY_COLOR)
            else:
                open_button.configure(state="disabled", text="Mở")
                open_button.configure(fg_color="#424242")

    def check_threads():
        active_threads[:] = [t for t in active_threads if t.is_alive()]
        root.after(1000, check_threads)

    def run_in_thread(target_func, *args):
        def thread_wrapper():
            try:
                target_func(*args)
            except Exception as e:
                message_queue.put({'type': 'error', 'message': str(e)})
            finally:
                message_queue.put({'type': 'progress', 'value': 1.0})
                progress_bar.pack_forget()  # Đảm bảo ẩn progress bar khi thread kết thúc
        
        thread = threading.Thread(target=thread_wrapper)
        thread.daemon = True
        thread.start()
        active_threads.append(thread)
        return thread

    def copy_text():
        text_to_copy = key_giai_maa
        pyperclip.copy(text_to_copy)
        print(f"Đã sao chép: {text_to_copy}")

    def load_resized_image(path, size=(150, 150)):
        """Tải và chỉnh kích thước ảnh PNG."""
        image = Image.open(path)
        image = image.resize(size, Image.Resampling.LANCZOS)  # Thay đổi kích thước ảnh
        return ImageTk.PhotoImage(image)

    # Hàm chọn file
    def browse_file():
        """Mở cửa sổ chọn file và xử lý file đã chọn."""
        global current_file, image_label
        file_path = askopenfilename()
        if not file_path:
            return  # Nếu người dùng hủy chọn file
        
        current_file = file_path
        # Xác định màu chữ dựa vào loại tệp
        text_color = "#90caf9" if file_path.endswith('.bin') else "#90ee90"  # Xanh dương nhạt cho .bin, xanh lá nhạt cho các tệp khác
        
        drop_label.configure(
            text=f"Tệp: {os.path.basename(file_path)}",
            font=("Arial", 24, "bold"),  # Tăng kích thước chữ lên 24
            text_color=text_color,
            wraplength=window_width-left_frame_width-100,
            justify="center"
        )
        
        # Hiển thị hình ảnh tương ứng với loại file
        if not image_label:
            image_label = ctk.CTkLabel(right_frame, text="")
            image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        if file_path.endswith('.bin'):
            image_label.configure(image=bin_image)  # Hiển thị ảnh cho file .bin
            open_button.configure(state="normal")
            encrypt_button.configure(state="disabled")
        else:
            image_label.configure(image=default_image)  # Hiển thị ảnh mặc định
            open_button.configure(state="disabled")
            encrypt_button.configure(state="normal")

    # Hàm xử lý nút "X"
    def clear_file():
        global current_file, image_label
        current_file = None
        drop_label.configure(
            text="Nhấn để chọn tệp",
            font=("Arial", 24, 'bold'),  # Tăng kích thước chữ lên 24
            text_color="#ffffff",  # Màu trắng cho text mặc định
            wraplength=window_width-left_frame_width-100,
            justify="center"
        )

        open_button.configure(state="disabled")
        encrypt_button.configure(state="disabled")
        if image_label:
            image_label.destroy()
            image_label = None

    def open_file():
        if current_file and selected_format and not camera_running:
            progress_bar.pack(pady=10)
            progress_bar.set(0)  # Reset progress bar về 0
            progress_bar.start()
            run_in_thread(chay_file, current_file, selected_format)
        elif camera_running:
            messagebox.showwarning("Cảnh báo", "Chỉ được mở một cửa sổ duy nhất!")
        elif selected_format == "":
            messagebox.showerror("Lỗi", "Vui lòng chọn định dạng file")

    def encrypt_file():
        if current_file:
            key = key_entry.get()
            try:
                test = base64.b64decode(key)
                kt = True
            except:
                kt = False
            
            if key:
                if kt:
                    progress_bar.pack(pady=10)
                    progress_bar.set(0)  # Reset progress bar về 0
                    progress_bar.start()
                    
                    # Add a success message for the queue
                    def encrypted_callback():
                        try:
                            result = ma_hoa(key, current_file)
                            message_queue.put({'type': 'info', 'message': f"Tệp đã được mã hóa thành công với key: {key}"})
                        except Exception as e:
                            message_queue.put({'type': 'error', 'message': str(e)})
                    
                    run_in_thread(encrypted_callback)
                else:
                    messagebox.showerror("Lỗi", "Key không hợp lệ!")
            else:
                messagebox.showerror("Lỗi", "Vui lòng nhập Key trước khi mã hóa!")

    def update_suggestions(event=None):
        # Lấy nội dung hiện tại trong entry của select_box
        user_input = select_box.get().lower()
        
        # Nếu người dùng xóa hết nội dung, hiển thị tất cả định dạng
        if not user_input:
            select_box.configure(values=all_file_formats)
            suggestion_label.configure(text="")
            return
        
        # Lọc danh sách định dạng phù hợp với nội dung nhập
        filtered_formats = [fmt for fmt in all_file_formats if user_input in fmt.lower()]
        
        # Cập nhật giá trị trong combobox
        select_box.configure(values=filtered_formats)
        
        # Hiển thị gợi ý dưới ô nhập
        if filtered_formats:
            # Giới hạn hiển thị tối đa 5 gợi ý
            display_suggestions = filtered_formats[:5]
            if len(filtered_formats) > 5:
                display_suggestions.append("...")
            
            suggestion_text = "Gợi ý: " + ", ".join(display_suggestions)
            suggestion_label.configure(text=suggestion_text)
            
            # Mở dropdown để hiển thị gợi ý
            select_box.event_generate('<Down>')
        else:
            suggestion_label.configure(text="Không tìm thấy định dạng phù hợp")
            select_box.configure(values=[])  # Xóa gợi ý nếu không có kết quả
            
    selected_format=""
    # Hàm xử lý khi chọn định dạng từ menu
    def on_combobox_select(event=None):
        global selected_format
        selected_format = select_box.get()  # Lưu kết quả vào biến toàn cục
        print(f"Đã chọn định dạng tệp: {selected_format}")

    # Hàm trợ giúp hiển thị danh sách định dạng theo nhóm
    def show_format_group(group_name):
        if group_name == "Tất cả":
            select_box.configure(values=all_file_formats)
        else:
            select_box.configure(values=file_formats_by_group.get(group_name, []))

    # Biến toàn cục
    current_file = None
    image_label = None
    window_width = 800
    window_height = 600

    # Giao diện
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = TkinterDnD.Tk()
    root.title("F.P.F.C")
    
    # Điều chỉnh kích thước cửa sổ theo độ phân giải màn hình
    window_width, window_height = adjust_window_size(root)
    
    root.configure(bg="#5c5b5b")

    current_dir = os.path.dirname(os.path.abspath(__file__))  # Lấy thư mục chứa file Python hiện tại

    # Tính toán kích thước khung bên trái dựa trên kích thước cửa sổ
    left_frame_width = max(200, int(window_width * 0.25))
    
    left_frame = ctk.CTkFrame(root, width=left_frame_width, height=window_height-20, fg_color="#021638")
    left_frame.pack(side="left", fill="y", padx=10, pady=10)

    # Tính toán kích thước nút dựa trên kích thước cửa sổ
    button_width = max(150, int(left_frame_width * 0.8))
    button_height = max(50, int(window_height * 0.08))
    button_font_size = max(20, int(window_height * 0.035))

    open_button = ctk.CTkButton(left_frame, text="Mở", state="disabled", command=open_file,
    font=("Arial", button_font_size, "bold"), width=button_width, height=button_height, fg_color='#0b4389')
    open_button.pack(pady=20, padx=10)

    encrypt_button = ctk.CTkButton(left_frame, text="Mã Hoá", state="disabled", command=encrypt_file,
    font=("Arial", button_font_size, "bold"), width=button_width, height=button_height, fg_color='#0b4389')
    encrypt_button.pack(pady=20, padx=10)

    right_frame = ctk.CTkFrame(root, width=window_width-left_frame_width-30, height=window_height-20, fg_color="#021638")
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # Thêm vào đầu code
    bgg=current_dir+"/assets/background.png"
    bg_image_original = Image.open(bgg)
    
    # Tạo ảnh nền ban đầu theo kích thước cửa sổ
    resized_bg = bg_image_original.resize((window_width, window_height), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(resized_bg)
    
    # Tạo label chứa ảnh nền
    bg_label = ctk.CTkLabel(root, image=bg_photo, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Tạo một hàm để cập nhật ảnh nền khi kích thước thay đổi
    def update_background_image(width, height):
        global bg_photo, bg_image_original
        # Resize ảnh nền theo kích thước cửa sổ
        resized_bg = bg_image_original.resize((width, height), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(resized_bg)
        bg_label.configure(image=bg_photo)

    # Đảm bảo các widget khác nằm trên nền
    left_frame.lift()
    right_frame.lift()


    # Nút "ẩn" cho toàn bộ vùng kéo file
    browse_button = ctk.CTkButton(
        right_frame,
        text="",
        width=window_width-left_frame_width-50,
        height=window_height-100,
        fg_color="#021638",
        hover_color="#4e4e4e",hover=False,  
        command=browse_file,
        corner_radius=10
    )
    browse_button.place(relx=0.5, rely=0.5, anchor="center")

    # Điều chỉnh kích thước font cho văn bản
    main_font_size = max(14, int(window_height * 0.025))
    title_font_size = max(20, int(window_height * 0.033))
    small_font_size = max(12, int(window_height * 0.02))
    
    copy_button = ctk.CTkButton(
        left_frame,
        text="C",
        width=max(20, int(window_width * 0.015)),
        height=max(20, int(window_width * 0.015)),
        font=("Arial", main_font_size, "bold"),
        corner_radius=30,
        text_color="white",
        command=copy_text
    )
    copy_button.place(relx=0.06, rely=0.95, anchor="sw")

    drop_label = ctk.CTkLabel(left_frame, text="Sao chép key thiết bị", font=("Arial", small_font_size, 'bold'))
    drop_label.place(relx=0.25, rely=0.95, anchor="sw")

    drop_label = ctk.CTkLabel(
        right_frame, 
        text="Nhấn để chọn tệp", 
        font=("Arial", 24, 'bold'),  # Tăng kích thước chữ lên 24
        wraplength=window_width-left_frame_width-100,
        justify="center",
        text_color="#ffffff"  # Màu trắng cho text mặc định
    )
    drop_label.place(relx=0.5, rely=0.2, anchor="center")

    # Điều chỉnh kích thước của nút X
    clear_button_size = max(30, int(window_width * 0.02))
    clear_button = ctk.CTkButton(right_frame, text="X", width=clear_button_size, height=clear_button_size, 
                               font=("Arial", small_font_size), fg_color="#5c5b5b", text_color="white", 
                               corner_radius=clear_button_size//2, command=clear_file)
    clear_button.place(relx=0.95, rely=0.05, anchor="center")

    # Tải ảnh với kích thước tương ứng với kích thước cửa sổ
    image_size = max(250, int(window_height * 0.35))  # Tăng kích thước ảnh lên
    default_image = load_resized_image(current_dir+"/assets/icon.png", size=(image_size, image_size))
    bin_image = load_resized_image(current_dir+"/assets/bin.png", size=(image_size, image_size))

    select_label = ctk.CTkLabel(left_frame, text="Chọn định dạng tệp:", font=("Arial", main_font_size))
    select_label.pack(pady=(7, 5), padx=10)

    # Định dạng file được phân nhóm
    file_formats_by_group = {
        "Văn bản": ["doc", "docx", "txt", "odt", "rtf", "md", "tex", "pdf"],
        "Bảng tính": ["xls", "xlsx", "csv", "ods"],
        "Trình chiếu": ["ppt", "pptx"],
        "Hình ảnh": ["png", "jpg", "jpeg", "gif", "bmp", "svg", "tiff", "webp"],
        "Video": ["mp4", "mkv", "mov", "avi", "flv", "wmv", "webm"],
        "Âm thanh": ["mp3", "wav", "aac", "flac", "ogg", "m4a"],
    }

    # Tạo danh sách phẳng chứa tất cả các định dạng
    all_file_formats = []
    for group, formats in file_formats_by_group.items():
        all_file_formats.extend(formats)

    # Frame chứa các nút nhóm định dạng
    format_groups_frame = ctk.CTkFrame(left_frame, fg_color="#021638")
    format_groups_frame.pack(pady=5, padx=10, fill="x")

    # Tính toán kích thước nút nhóm
    group_button_width = max(70, int(left_frame_width * 0.45))
    group_button_height = max(35, int(window_height * 0.05))
    
    # Tạo các nút cho từng nhóm định dạng
    group_buttons = []
    for i, group_name in enumerate(["Tất cả", "Văn bản", "Hình ảnh", "Video"]):
        btn = ctk.CTkButton(
            format_groups_frame,
            text=group_name,
            font=("Arial", small_font_size, "bold"),
            width=group_button_width,
            height=group_button_height,
            fg_color="#0b4389",
            command=lambda name=group_name: show_format_group(name)
        )
        btn.grid(row=i//2, column=i%2, padx=4, pady=4, sticky="ew")
        group_buttons.append(btn)

    # Tạo select box
    select_box = ctk.CTkComboBox(
        left_frame,
        values=all_file_formats,
        font=("Arial", main_font_size),
        height=max(35, int(window_height * 0.05)),
        command=on_combobox_select
    )
    select_box.pack(pady=5, padx=10)

    # Thêm nhãn hiển thị gợi ý bên dưới select box
    suggestion_label = ctk.CTkLabel(
        left_frame, 
        text="", 
        font=("Arial", main_font_size, "bold"),
        text_color="#00ffff",
        justify="left",
        wraplength=left_frame_width-20
    )
    suggestion_label.pack(pady=(0, 5), padx=10)

    # Cài đặt giá trị mặc định cho combo box
    select_box.set("")

    # Ràng buộc sự kiện nhập dữ liệu vào hộp chọn để gợi ý tự động
    select_box.bind("<KeyRelease>", update_suggestions)

    # **Cho phép nhập liệu khi danh sách mở rộng**
    # Ràng buộc sự kiện nhấn phím lên/ xuống để giữ lại khả năng nhập liệu
    def prevent_dropdown_interruption(event):
        select_box.event_generate("<KeyRelease>", when="tail")

    # Hàm xử lý khi nhấn nút "X" để xóa nội dung trong ô nhập key
    def clear_key_entry():
        key_entry.delete(0, 'end')  # Xóa hết nội dung trong ô nhập

    # Thêm một frame để chứa ô nhập key và nút "X"
    key_frame = ctk.CTkFrame(left_frame, corner_radius=10, fg_color="#021638")
    key_frame.pack(pady=20, padx=10, fill="x")  # Đặt `fill="x"` để frame chiếm hết chiều rộng

    # Tạo ô nhập key
    key_entry = ctk.CTkEntry(
        key_frame, 
        placeholder_text="Nhập Key tại đây", 
        font=("Arial", main_font_size), 
        height=max(35, int(window_height * 0.05))
    )
    key_entry.pack(side="left", padx=(0,10), expand=True)

    # Tạo nút "X" để xóa nội dung trong ô nhập key
    clear_key_size = max(30, int(window_width * 0.018))
    clear_key_button = ctk.CTkButton(
        key_frame,
        text="x",
        width=clear_key_size,
        height=clear_key_size,
        font=("Arial", main_font_size, "bold"),
        corner_radius=clear_key_size//2,
        fg_color="transparent",
        text_color="black",
        command=clear_key_entry
    )
    clear_key_button.pack(side="right")

    # Thêm progress bar
    progress_bar = ctk.CTkProgressBar(left_frame, width=max(150, left_frame_width-40))
    progress_bar.set(0)

    # Cho phép thay đổi kích thước cửa sổ (nếu muốn)
    root.resizable(False, False)  

    # Đăng ký sự kiện thay đổi kích thước cửa sổ
    def on_window_resize(event):
        # Khai báo biến toàn cục ngay từ đầu hàm
        global window_width, window_height
        
        # Chỉ xử lý sự kiện từ cửa sổ gốc, không xử lý sự kiện từ các widget con
        if event.widget != root:
            return
            
        # Chỉ cập nhật lại giao diện nếu sự thay đổi kích thước đủ lớn
        if abs(event.width - window_width) > 50 or abs(event.height - window_height) > 50:
            # Lưu lại kích thước mới
            window_width = event.width
            window_height = event.height
            
            # Cập nhật ảnh nền
            update_background_image(window_width, window_height)
            
            # Không gọi adjust_window_size ở đây để tránh vòng lặp vô hạn
            # Thay vào đó, chỉ cập nhật các thành phần UI khi cần
            
            # Cập nhật kích thước các widget
            left_frame_width = max(200, int(window_width * 0.25))
            browse_button.configure(
                width=window_width-left_frame_width-50,
                height=window_height-100
            )
            progress_bar.configure(width=max(150, left_frame_width-40))
            
            # Cập nhật wraplength cho nhãn gợi ý
            suggestion_label.configure(wraplength=left_frame_width-20)
            
    # Chỉ đăng ký sự kiện Configure cho cửa sổ chính, không cho các widget con
    root.bind("<Configure>", on_window_resize)

    # Ẩn nút maximized 
    root.overrideredirect(False)  
    # Gắn sự kiện nhấn mở menu, giữ danh sách hoạt động song song nhập liệu
    select_box.bind("<Button-1>", prevent_dropdown_interruption)
    root.drop_target_register(DND_FILES)
    root.after(100, process_queue)  # Bắt đầu xử lý queue
    root.after(1000, check_threads)  # Bắt đầu kiểm tra thread
    root.mainloop()