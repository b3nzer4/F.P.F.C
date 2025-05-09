"""
F.P.F.C - File Protection and File Conversion
Author: b3nzer4tz (bennyzzz1909@gmail.com)
4txinhvcl:))
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
                elif msg['type'] == 'info':
                    messagebox.showinfo("Thông báo", msg['message'])
                elif msg['type'] == 'progress':
                    progress_bar.set(msg['value'])
                    if msg['value'] >= 1.0:
                        progress_bar.stop()
                        progress_bar.pack_forget()
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
        drop_label.configure(text=f"Tệp: {os.path.basename(file_path)}",font=("Arial",14,"bold"))

        
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
        drop_label.configure(text="Nhấn để chọn tệp",font=("Arial", 20, 'bold'))

        open_button.configure(state="disabled")
        encrypt_button.configure(state="disabled")
        if image_label:
            image_label.destroy()
            image_label = None

    def open_file():
        if current_file and selected_format and not camera_running:
            progress_bar.pack(pady=10)
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
                    progress_bar.start()
                    run_in_thread(ma_hoa, key, current_file)
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

    # Giao diện
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = TkinterDnD.Tk()
    root.title("F.P.F.C")
    root.geometry("800x600")
    root.configure(bg="#5c5b5b")

    current_dir = os.path.dirname(os.path.abspath(__file__))  # Lấy thư mục chứa file Python hiện tại

    left_frame = ctk.CTkFrame(root, width=200, height=400, fg_color="#021638")
    left_frame.pack(side="left", fill="y", padx=10, pady=10)

    open_button = ctk.CTkButton(left_frame, text="Mở", state="disabled", command=open_file,
    font=("Arial", 25,"bold"), width=150, height=50, fg_color='#0b4389')
    open_button.pack(pady=20, padx=10)

    encrypt_button = ctk.CTkButton(left_frame, text="Mã Hoá", state="disabled", command=encrypt_file,
    font=("Arial", 25,"bold"), width=150, height=50,fg_color='#0b4389')
    encrypt_button.pack(pady=20, padx=10)

    right_frame = ctk.CTkFrame(root, width=400, height=400, fg_color="#021638")
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # Thêm vào đầu code
    bgg=current_dir+"/assets/background.png"
    bg_image = Image.open(bgg)
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Tạo label chứa ảnh nền
    bg_label = ctk.CTkLabel(root, image=bg_photo, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Đảm bảo các widget khác nằm trên nền
    left_frame.lift()
    right_frame.lift()


    # Nút "ẩn" cho toàn bộ vùng kéo file
    browse_button = ctk.CTkButton(
        right_frame,
        text="",
        width=400,
        height=400,
        fg_color="#021638",
        hover_color="#4e4e4e",hover=False,  
        command=browse_file,
        corner_radius=10
    )
    browse_button.place(relx=0.5, rely=0.5, anchor="center")

    copy_button = ctk.CTkButton(
        left_frame,
        text="C",  # Nội dung nút (chữ "C" đại diện cho "Copy")
        width=20,  # Chiều rộng nút
        height=20,  # Chiều cao nút
        font=("Arial", 16, "bold"),  # Font chữ của nội dung
        corner_radius=30,  # Góc bo tròn (giúp nút tròn)# Màu nền của nút
        text_color="white",  # Màu chữ  # Màu khi di chuột qua
        command=copy_text  # Gắn chức năng sao chép
    )
    copy_button.place(relx=0.06, rely=0.95, anchor="sw")

    drop_label = ctk.CTkLabel(left_frame, text="Sao chép key thiết bị", font=("Arial", 12, 'bold'))
    drop_label.place(relx=0.25, rely=0.95, anchor="sw")

    drop_label = ctk.CTkLabel(right_frame, text="Nhấn để chọn tệp", font=("Arial", 20, 'bold'))
    drop_label.place(relx=0.5, rely=0.2, anchor="center")

    clear_button = ctk.CTkButton(right_frame, text="X", width=30, height=30, font=("Arial", 12), fg_color="#5c5b5b", text_color="white", corner_radius=30, command=clear_file)
    clear_button.place(relx=0.95, rely=0.05, anchor="center")

    # Tải ảnh

    default_image = load_resized_image(current_dir+"/assets/icon.png", size=(150, 150))
    bin_image = load_resized_image(current_dir+"/assets/bin.png", size=(150, 150))

    select_label = ctk.CTkLabel(left_frame, text="Chọn định dạng tệp:", font=("Arial", 14))
    select_label.pack(pady=(7, 5), padx=10)

    # Định dạng file được phân nhóm
    file_formats_by_group = {
        "Văn bản": ["doc", "docx", "txt", "odt", "rtf", "md", "tex", "pdf"],
        "Bảng tính": ["xls", "xlsx", "csv", "ods"],
        "Trình chiếu": ["ppt", "pptx"],
        "Hình ảnh": ["png", "jpg", "jpeg", "gif", "bmp", "svg", "tiff", "webp"],
        "Video": ["mp4", "mkv", "mov", "avi", "flv", "wmv", "webm"],
        "Âm thanh": ["mp3", "wav", "aac", "flac", "ogg", "m4a"],
        "Nén": ["zip", "rar", "7z", "tar", "gz", "iso"],
        "Thực thi": ["bin", "exe", "dll", "apk", "deb", "dmg", "pkg", "msi"]
    }

    # Tạo danh sách phẳng chứa tất cả các định dạng
    all_file_formats = []
    for group, formats in file_formats_by_group.items():
        all_file_formats.extend(formats)

    # Frame chứa các nút nhóm định dạng
    format_groups_frame = ctk.CTkFrame(left_frame, fg_color="#021638")
    format_groups_frame.pack(pady=5, padx=10, fill="x")

    # Tạo các nút cho từng nhóm định dạng
    group_buttons = []
    for i, group_name in enumerate(["Tất cả", "Văn bản", "Hình ảnh", "Video"]):
        btn = ctk.CTkButton(
            format_groups_frame,
            text=group_name,
            font=("Arial", 12, "bold"),  # Tăng kích thước font từ 10 lên 12 và thêm bold
            width=70,  # Tăng kích thước nút theo chiều ngang từ 40 lên 70
            height=35,  # Tăng kích thước nút theo chiều dọc từ 25 lên 35
            fg_color="#0b4389",
            command=lambda name=group_name: show_format_group(name)
        )
        btn.grid(row=i//2, column=i%2, padx=4, pady=4, sticky="ew")  # Tăng padding để buttons có không gian rộng hơn
        group_buttons.append(btn)

    # Tạo select box
    select_box = ctk.CTkComboBox(
        left_frame,
        values=all_file_formats,
        font=("Arial", 14),
        command=on_combobox_select
    )
    select_box.pack(pady=5, padx=10)

    # Thêm nhãn hiển thị gợi ý bên dưới select box
    suggestion_label = ctk.CTkLabel(
        left_frame, 
        text="", 
        font=("Arial", 14, "bold"),  # Tăng font size từ 12 lên 14 và thêm bold
        text_color="#00ffff",  # Đổi màu từ #b3e5fc sang màu cyan sáng hơn
        justify="left",
        wraplength=180  # Giới hạn chiều rộng để tự động xuống dòng
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

    # Thêm nút "X" vào ô nhập key, với nền trong suốt và không có hiệu ứng hover
    # Thêm một frame để chứa ô nhập key và nút "X"
    key_frame = ctk.CTkFrame(left_frame, corner_radius=10, fg_color="#021638")
    key_frame.pack(pady=20, padx=10, fill="x")  # Đặt `fill="x"` để frame chiếm hết chiều rộng

    # Tạo ô nhập key
    key_entry = ctk.CTkEntry(key_frame, placeholder_text="Nhập Key tại đây", font=("Arial", 14), height=35)
    key_entry.pack(side="left", padx=(0,10), expand=True)  # Đặt ô nhập key bên trái và cho phép mở rộng

    # Tạo nút "X" để xóa nội dung trong ô nhập key
    clear_key_button = ctk.CTkButton(
        key_frame,
        text="x",  # Nội dung nút là chữ "X"
        width=30,
        height=30,
        font=("Arial", 16, "bold"),
        corner_radius=15,
        fg_color="transparent",  # Nền trong suốt
        text_color="black",  # Màu chữ là đen
        command=clear_key_entry  # Gắn hàm xóa nội dung khi nhấn nút
    )

    clear_key_button.pack(side="right")  # Đặt nút "X" bên phải ô nhập key

    # Thêm progress bar
    progress_bar = ctk.CTkProgressBar(left_frame, width=150)
    progress_bar.set(0)

    root.resizable(False, False)  # Ngừng thay đổi kích thước cửa sổ
    # Ẩn nút maximized 
    root.overrideredirect(False)  
    # Gắn sự kiện nhấn mở menu, giữ danh sách hoạt động song song nhập liệu
    select_box.bind("<Button-1>", prevent_dropdown_interruption)
    root.drop_target_register(DND_FILES)
    root.after(100, process_queue)  # Bắt đầu xử lý queue
    root.after(1000, check_threads)  # Bắt đầu kiểm tra thread
    root.mainloop()