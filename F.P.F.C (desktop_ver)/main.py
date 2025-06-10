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
    hang_doi = queue.Queue()
    luong_dang_chay = []
    camera_dang_chay = False

    mau_chinh = "#1a237e"
    mau_phu = "#0d47a1"
    mau_nhan = "#2196f3"
    mau_nen = "#121212"
    mau_chu = "#ffffff"

    # Định nghĩa các hàm tiện ích không phụ thuộc vào các đối tượng UI được tạo sau
    def dieu_chinh_cua_so(root):
        man_hinh_rong = root.winfo_screenwidth()
        man_hinh_cao = root.winfo_screenheight()
        
        rong_toi_da = int(man_hinh_rong * 0.8)
        cao_cua_so = int(rong_toi_da * 3/4)
        
        if cao_cua_so > man_hinh_cao * 0.8:
            cao_cua_so = int(man_hinh_cao * 0.8)
            rong_toi_da = int(cao_cua_so * 4/3)
        
        rong_cua_so = max(rong_toi_da, 800)
        cao_cua_so = max(cao_cua_so, 600)
        
        rong_cua_so = min(rong_cua_so, 1600)
        cao_cua_so = min(cao_cua_so, 1200)
        
        vi_tri_x = (man_hinh_rong - rong_cua_so) // 2
        vi_tri_y = (man_hinh_cao - cao_cua_so) // 2
        
        geometry_str = f"{rong_cua_so}x{cao_cua_so}+{vi_tri_x}+{vi_tri_y}"
        root.geometry(geometry_str)
        
        return rong_cua_so, cao_cua_so

    def hieu_ung_nut(nut, mau_goc, mau_hover):
        def khi_vao(e):
            nut.configure(fg_color=mau_hover)
        def khi_ra(e):
            nut.configure(fg_color=mau_goc)
        nut.bind("<Enter>", khi_vao)
        nut.bind("<Leave>", khi_ra)

    def hieu_ung_tien_trinh():
        if thanh_tien_trinh.winfo_ismapped():
            gia_tri_hien_tai = thanh_tien_trinh.get()
            if gia_tri_hien_tai < 1.0:
                gia_tri_moi = min(gia_tri_hien_tai + 0.01, 1.0)
                thanh_tien_trinh.set(gia_tri_moi)
                root.after(50, hieu_ung_tien_trinh)

    def xu_ly_hang_doi():
        try:
            while True:
                tin_nhan = hang_doi.get_nowait()
                if tin_nhan['loai'] == 'loi':
                    messagebox.showerror("Lỗi", tin_nhan['noi_dung'])
                    thanh_tien_trinh.pack_forget()
                elif tin_nhan['loai'] == 'thong_bao':
                    messagebox.showinfo("Thông báo", tin_nhan['noi_dung'])
                    thanh_tien_trinh.pack_forget()
                elif tin_nhan['loai'] == 'tien_trinh':
                    thanh_tien_trinh.set(tin_nhan['gia_tri'])
                    if tin_nhan['gia_tri'] >= 1.0:
                        thanh_tien_trinh.stop()
                        thanh_tien_trinh.pack_forget()
                elif tin_nhan['loai'] == 'trang_thai_camera':
                    global camera_dang_chay
                    camera_dang_chay = tin_nhan['trang_thai']
                    cap_nhat_trang_thai_nut_mo()
        except queue.Empty:
            pass
        root.after(100, xu_ly_hang_doi)

    def kiem_tra_luong():
        luong_dang_chay[:] = [t for t in luong_dang_chay if t.is_alive()]
        root.after(1000, kiem_tra_luong)

    def chay_trong_luong(ham_muc_tieu, *args):
        def bao_luong():
            try:
                ham_muc_tieu(*args)
            except Exception as e:
                hang_doi.put({'loai': 'loi', 'noi_dung': str(e)})
            finally:
                hang_doi.put({'loai': 'tien_trinh', 'gia_tri': 1.0})
                thanh_tien_trinh.pack_forget()
        
        luong = threading.Thread(target=bao_luong)
        luong.daemon = True
        luong.start()
        luong_dang_chay.append(luong)
        return luong

    def sao_chep_van_ban():
        van_ban = key_giai_maa
        pyperclip.copy(van_ban)
        print(f"Đã sao chép: {van_ban}")

    def tai_anh_thu_nho(duong_dan, kich_thuoc=(150, 150)):
        anh = Image.open(duong_dan)
        anh = anh.resize(kich_thuoc, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(anh)
    
    # Khởi tạo các biến toàn cục cho các đối tượng UI
    tep_hien_tai = None
    nhan_anh = None
    dinh_dang_da_chon = ""
    key_giai_maa = "" # Assuming this is meant to be global and might be set elsewhere
    all_file_formats = [] # Assuming this is populated elsewhere
    file_formats_by_group = {} # Assuming this is populated elsewhere

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = TkinterDnD.Tk()
    root.title("F.P.F.C")
    
    rong_cua_so, cao_cua_so = dieu_chinh_cua_so(root)
    
    root.configure(bg="#5c5b5b")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    rong_khung_trai = max(200, int(rong_cua_so * 0.25))
    
    khung_trai = ctk.CTkFrame(root, width=rong_khung_trai, height=cao_cua_so-20, fg_color="#021638")
    khung_trai.pack(side="left", fill="y", padx=10, pady=10)

    button_width = max(150, int(rong_khung_trai * 0.8))
    button_height = max(50, int(cao_cua_so * 0.08))
    button_font_size = max(20, int(cao_cua_so * 0.035))

    nut_mo = ctk.CTkButton(khung_trai, text="Mở", state="disabled", command=None, # Command set later
    font=("Arial", button_font_size, "bold"), width=button_width, height=button_height, fg_color='#0b4389')
    nut_mo.pack(pady=20, padx=10)

    nut_ma_hoa = ctk.CTkButton(khung_trai, text="Mã Hoá", state="disabled", command=None, # Command set later
    font=("Arial", button_font_size, "bold"), width=button_width, height=button_height, fg_color='#0b4389')
    nut_ma_hoa.pack(pady=20, padx=10)

    khung_phai = ctk.CTkFrame(root, width=rong_cua_so-rong_khung_trai-30, height=cao_cua_so-20, fg_color="#021638")
    khung_phai.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    bgg=current_dir+"/assets/background.png"
    bg_image_original = Image.open(bgg)
    
    resized_bg = bg_image_original.resize((rong_cua_so, cao_cua_so), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(resized_bg)
    
    bg_label = ctk.CTkLabel(root, image=bg_photo, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    khung_trai.lift()
    khung_phai.lift()

    browse_button = ctk.CTkButton(
        khung_phai,
        text="",
        width=rong_cua_so-rong_khung_trai-50,
        height=cao_cua_so-100,
        fg_color="#021638",
        hover_color="#4e4e4e",hover=False,  
        command=None, # Command set later
        corner_radius=10
    )
    browse_button.place(relx=0.5, rely=0.5, anchor="center")

    main_font_size = max(14, int(cao_cua_so * 0.025))
    title_font_size = max(20, int(cao_cua_so * 0.033))
    small_font_size = max(12, int(cao_cua_so * 0.02))
    
    copy_button = ctk.CTkButton(
        khung_trai,
        text="C",
        width=max(20, int(rong_cua_so * 0.015)),
        height=max(20, int(rong_cua_so * 0.015)),
        font=("Arial", main_font_size, "bold"),
        corner_radius=30,
        text_color="white",
        command=sao_chep_van_ban
    )
    copy_button.place(relx=0.06, rely=0.95, anchor="sw")

    nhan_thong_tin_key = ctk.CTkLabel(khung_trai, text="Sao chép key thiết bị", font=("Arial", small_font_size, 'bold'))
    nhan_thong_tin_key.place(relx=0.25, rely=0.95, anchor="sw")

    nhan_keo = ctk.CTkLabel(
        khung_phai, 
        text="Nhấn để chọn tệp", 
        font=("Arial", 24, 'bold'),
        wraplength=rong_cua_so-rong_khung_trai-100,
        justify="center",
        text_color="#ffffff"
    )
    nhan_keo.place(relx=0.5, rely=0.2, anchor="center")

    clear_button_size = max(30, int(rong_cua_so * 0.02))
    clear_button = ctk.CTkButton(khung_phai, text="X", width=clear_button_size, height=clear_button_size, 
                                font=("Arial", small_font_size), fg_color="#5c5b5b", text_color="white", 
                                corner_radius=clear_button_size//2, command=None) # Command set later
    clear_button.place(relx=0.95, rely=0.05, anchor="center")

    image_size = max(250, int(cao_cua_so * 0.35))
    anh_mac_dinh = tai_anh_thu_nho(current_dir+"/assets/icon.png", size=(image_size, image_size))
    anh_bin = tai_anh_thu_nho(current_dir+"/assets/bin.png", size=(image_size, image_size))

    select_label = ctk.CTkLabel(khung_trai, text="Chọn định dạng tệp:", font=("Arial", main_font_size))
    select_label.pack(pady=(7, 5), padx=10)

    format_groups_frame = ctk.CTkFrame(khung_trai, fg_color="#021638")
    format_groups_frame.pack(pady=5, padx=10, fill="x")

    all_file_formats = [ # Re-defining here to ensure it's available after UI is created
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf",
        ".txt", ".odt", ".rtf", ".md", ".tex",
        ".csv", ".ods",
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg",
        ".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm",
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a",
        ".zip", ".rar", ".7z", ".tar", ".gz", ".iso",
        ".bin", ".exe", ".dll", ".apk", ".deb", ".dmg", ".pkg", ".msi"
    ]

    file_formats_by_group = { # Re-defining here to ensure it's available after UI is created
        "Văn bản": [".doc", ".docx", ".txt", ".odt", ".rtf", ".md", ".tex"],
        "Bảng tính": [".xls", ".xlsx", ".csv", ".ods"],
        "Trình chiếu": [".ppt", ".pptx"],
        "PDF": [".pdf"],
        "Ảnh": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"],
        "Video": [".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm"],
        "Âm thanh": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
        "Nén & ISO": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
        "Chương trình": [".bin", ".exe", ".dll", ".apk", ".deb", ".dmg", ".pkg", ".msi"],
        "Tất cả": all_file_formats
    }

    # Creating group buttons
    group_button_width = max(70, int(rong_khung_trai * 0.45))
    group_button_height = max(35, int(cao_cua_so * 0.05))

    for group_name in file_formats_by_group.keys():
        group_btn = ctk.CTkButton(format_groups_frame, text=group_name,
                                font=("Arial", small_font_size),
                                command=lambda name=group_name: show_format_group(name),
                                width=group_button_width, height=group_button_height,
                                fg_color='#0b4389')
        group_btn.pack(side="left", padx=5, pady=5)
        hieu_ung_nut(group_btn, '#0b4389', '#1a237e') # Áp dụng hiệu ứng hover

    select_box = ctk.CTkComboBox(
        khung_trai,
        values=all_file_formats,
        font=("Arial", main_font_size),
        height=max(35, int(cao_cua_so * 0.05)),
        command=None # Command set later
    )
    select_box.pack(pady=5, padx=10, fill="x")

    suggestion_label = ctk.CTkLabel(
        khung_trai, 
        text="", 
        font=("Arial", main_font_size, "bold"),
        text_color="#00ffff",
        wraplength=rong_khung_trai-20
    )
    suggestion_label.pack(pady=(0, 10), padx=10, fill="x")

    key_frame = ctk.CTkFrame(khung_trai, corner_radius=10, fg_color="#021638")
    key_frame.pack(pady=20, padx=10, fill="x")

    nhap_key = ctk.CTkEntry(
        key_frame, 
        placeholder_text="Nhập Key tại đây", 
        font=("Arial", main_font_size), 
        height=max(35, int(cao_cua_so * 0.05))
    )
    nhap_key.pack(side="left", padx=(0,10), expand=True)

    clear_key_size = max(30, int(rong_cua_so * 0.018))
    clear_key_button = ctk.CTkButton(
        key_frame,
        text="X",
        width=clear_key_size,
        height=clear_key_size,
        font=("Arial", small_font_size),
        fg_color="#5c5b5b",
        text_color="black",
        corner_radius=clear_key_size//2,
        command=None # Command set later
    )
    clear_key_button.pack(side="right")
    hieu_ung_nut(clear_key_button, "#5c5b5b", "#8a8a8a")

    thanh_tien_trinh = ctk.CTkProgressBar(khung_trai, width=max(150, rong_khung_trai-40))
    thanh_tien_trinh.set(0)

    # Định nghĩa các hàm phụ thuộc vào các đối tượng UI đã được tạo
    def cap_nhat_trang_thai_nut_mo():
        if camera_dang_chay:
            nut_mo.configure(state="disabled", text="Đang chạy camera...")
            nut_mo.configure(fg_color="#424242")
        else:
            if tep_hien_tai and dinh_dang_da_chon:
                nut_mo.configure(state="normal", text="Mở")
                nut_mo.configure(fg_color=mau_chinh)
            else:
                nut_mo.configure(state="disabled", text="Mở")
                nut_mo.configure(fg_color="#424242")

    def chon_tep():
        global tep_hien_tai, nhan_anh
        duong_dan = askopenfilename()
        if not duong_dan:
            return
        
        tep_hien_tai = duong_dan
        mau_chu_tep = "#90caf9" if duong_dan.endswith('.bin') else "#90ee90"
        
        nhan_keo.configure(
            text=f"Tệp: {os.path.basename(duong_dan)}",
            font=("Arial", 24, "bold"),
            text_color=mau_chu_tep,
            wraplength=rong_cua_so-rong_khung_trai-100,
            justify="center"
        )
        
        if not nhan_anh:
            nhan_anh = ctk.CTkLabel(khung_phai, text="")
            nhan_anh.place(relx=0.5, rely=0.5, anchor="center")
        
        if duong_dan.endswith('.bin'):
            nhan_anh.configure(image=anh_bin)
            nut_mo.configure(state="normal")
            nut_ma_hoa.configure(state="disabled")
        else:
            nhan_anh.configure(image=anh_mac_dinh)
            nut_mo.configure(state="disabled")
            nut_ma_hoa.configure(state="normal")

    def xoa_tep():
        global tep_hien_tai, nhan_anh
        tep_hien_tai = None
        nhan_keo.configure(
            text="Nhấn để chọn tệp",
            font=("Arial", 24, 'bold'),
            text_color="#ffffff",
            wraplength=rong_cua_so-rong_khung_trai-100,
            justify="center"
        )

        nut_mo.configure(state="disabled")
        nut_ma_hoa.configure(state="disabled")
        if nhan_anh:
            nhan_anh.destroy()
            nhan_anh = None

    def mo_tep():
        if tep_hien_tai and dinh_dang_da_chon and not camera_dang_chay:
            thanh_tien_trinh.pack(pady=10)
            thanh_tien_trinh.set(0)
            thanh_tien_trinh.start()
            chay_trong_luong(chay_file, tep_hien_tai, dinh_dang_da_chon)
        elif camera_dang_chay:
            messagebox.showwarning("Cảnh báo", "Chỉ được mở một cửa sổ duy nhất!")
        elif dinh_dang_da_chon == "":
            messagebox.showerror("Lỗi", "Vui lòng chọn định dạng file")

    def ma_hoa_tep():
        if tep_hien_tai:
            key = nhap_key.get()
            try:
                test = base64.b64decode(key)
                hop_le = True
            except:
                hop_le = False
            
            if key:
                if hop_le:
                    thanh_tien_trinh.pack(pady=10)
                    thanh_tien_trinh.set(0)
                    thanh_tien_trinh.start()
                    
                    def callback_ma_hoa():
                        try:
                            ket_qua = ma_hoa(key, tep_hien_tai)
                            hang_doi.put({'loai': 'thong_bao', 'noi_dung': f"Tệp đã được mã hóa thành công với key: {key}"})
                        except Exception as e:
                            hang_doi.put({'loai': 'loi', 'noi_dung': str(e)})
                    
                    chay_trong_luong(callback_ma_hoa)
                else:
                    messagebox.showerror("Lỗi", "Key không hợp lệ!")
            else:
                messagebox.showerror("Lỗi", "Vui lòng nhập Key trước khi mã hóa!")

    def update_suggestions(event=None):
        user_input = select_box.get().lower()
        
        if not user_input:
            select_box.configure(values=all_file_formats)
            suggestion_label.configure(text="")
            return
        
        filtered_formats = [fmt for fmt in all_file_formats if user_input in fmt.lower()]
        
        select_box.configure(values=filtered_formats)
        
        if filtered_formats:
            display_suggestions = filtered_formats[:5]
            if len(filtered_formats) > 5:
                display_suggestions.append("...")
            
            suggestion_text = "Gợi ý: " + ", ".join(display_suggestions)
            suggestion_label.configure(text=suggestion_text)
            
            select_box.event_generate('<Down>')
        else:
            suggestion_label.configure(text="Không tìm thấy định dạng phù hợp")
            select_box.configure(values=[])

    def on_combobox_select(event=None):
        global dinh_dang_da_chon
        dinh_dang_da_chon = select_box.get()
        print(f"Đã chọn định dạng tệp: {dinh_dang_da_chon}")

    def show_format_group(group_name):
        if group_name == "Tất cả":
            select_box.configure(values=all_file_formats)
        else:
            select_box.configure(values=file_formats_by_group.get(group_name, []))

    def update_background_image(width, height):
        global bg_photo, bg_image_original
        resized_bg = bg_image_original.resize((width, height), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(resized_bg)
        bg_label.configure(image=bg_photo)

    def prevent_dropdown_interruption(event):
        select_box.focus()

    def clear_key_entry():
        nhap_key.delete(0, 'end')

    def on_window_resize(event):
        global rong_cua_so, cao_cua_so
        
        if abs(event.width - rong_cua_so) > 50 or abs(event.height - cao_cua_so) > 50:
            rong_cua_so = event.width
            cao_cua_so = event.height
            
            update_background_image(rong_cua_so, cao_cua_so)
            
            rong_khung_trai_moi = max(200, int(rong_cua_so * 0.25))
            khung_trai.configure(width=rong_khung_trai_moi)
            browse_button.configure(
                width=rong_cua_so-rong_khung_trai_moi-50,
                height=cao_cua_so-100
            )
            thanh_tien_trinh.configure(width=max(150, rong_khung_trai_moi-40))
            nhan_keo.configure(wraplength=rong_cua_so-rong_khung_trai_moi-100)
            suggestion_label.configure(wraplength=rong_khung_trai_moi-20)
            nut_mo.configure(width=max(150, int(rong_khung_trai_moi * 0.8)))
            nut_ma_hoa.configure(width=max(150, int(rong_khung_trai_moi * 0.8)))

    # Liên kết các lệnh với nút sau khi các hàm đã được định nghĩa
    nut_mo.configure(command=mo_tep)
    nut_ma_hoa.configure(command=ma_hoa_tep)
    browse_button.configure(command=chon_tep)
    clear_button.configure(command=xoa_tep)
    select_box.configure(command=on_combobox_select)
    clear_key_button.configure(command=clear_key_entry)

    # Đăng ký sự kiện
    root.bind("<Configure>", on_window_resize)
    select_box.bind("<KeyRelease>", update_suggestions)
    select_box.bind("<Button-1>", prevent_dropdown_interruption)
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', lambda event: chon_tep()) # Assuming dnd_bind can call chon_tep directly

    root.after(100, xu_ly_hang_doi)
    root.after(1000, kiem_tra_luong)
    root.mainloop()