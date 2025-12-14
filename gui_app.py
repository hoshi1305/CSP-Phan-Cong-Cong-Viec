# Giao diện ứng dụng phân công công việc sử dụng CSP
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pandas as pd
import time
import sys
import statistics

# Import matplotlib để vẽ biểu đồ
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Import các module solver
import baseline
import importlib.util
spec = importlib.util.spec_from_file_location("advanced", "advanced.py")
advanced = importlib.util.module_from_spec(spec)
spec.loader.exec_module(advanced)

class CSPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Phân Công Công Việc - CSP")
        self.root.geometry("1600x900")
        self.root.configure(bg='#f0f0f0')
        
        # Biến lưu trữ kết quả
        self.baseline_result = None
        self.advanced_result = None
        self.baseline_time = 0
        self.advanced_time = 0
        self.current_dataset = "medium_project"
        
        # Biến lưu trữ file upload (tab assignment)
        self.uploaded_tasks_file = None
        self.uploaded_employees_file = None
        self.use_uploaded_files = False
        
        # Biến lưu trữ file upload (tab compare)
        self.compare_uploaded_tasks_file = None
        self.compare_uploaded_employees_file = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        # ==================== THANH TIÊU ĐỀ ====================
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="HỆ THỐNG PHÂN CÔNG CÔNG VIỆC - CSP",
                              font=('Arial', 18, 'bold'), 
                              bg='#2c3e50', fg='white')
        title_label.pack(pady=15)
        
        # ==================== NOTEBOOK (TAB) ====================
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Sắp xếp công việc
        self.assignment_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.assignment_tab, text="📋 Sắp Xếp Công Việc")
        self.setup_assignment_tab()
        
        # Tab 2: So sánh hiệu năng
        self.compare_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.compare_tab, text="📊 So Sánh Hiệu Năng")
        self.setup_compare_tab()
        
        # ==================== THANH TRẠNG THÁI ====================
        self.status_bar = tk.Label(self.root, text="Sẵn sàng", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  font=('Arial', 9), bg='#e0e0e0')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_assignment_tab(self):
        """Thiết lập tab sắp xếp công việc (theo hình 1)"""
        # Khung chính - chia 2 cột
        main_container = tk.Frame(self.assignment_tab, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ==================== CỘT TRÁI: SẮP XẾP CÔNG VIỆC ====================
        left_frame = tk.Frame(main_container, bg='#ecf0f1', width=350, relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_frame.pack_propagate(False)
        
        tk.Label(left_frame, text="SẮP XẾP CÔNG VIỆC", 
                font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(pady=10)
        
        # Chọn file dữ liệu
        data_frame = tk.LabelFrame(left_frame, text="Chọn file dữ liệu", 
                                   font=('Arial', 10, 'bold'), bg='#ecf0f1', padx=10, pady=10)
        data_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Radio button cho datasets có sẵn
        self.data_source_var = tk.StringVar(value="predefined")
        tk.Radiobutton(data_frame, text="Sử dụng dữ liệu có sẵn", 
                      variable=self.data_source_var, value="predefined", 
                      bg='#ecf0f1', font=('Arial', 9, 'bold'),
                      command=self.on_data_source_change).pack(anchor='w', pady=2)
        
        self.dataset_var = tk.StringVar(value="medium_project")
        datasets = [
            ("  • Small Project (5 NV, 20 tasks)", "small_project"),
            ("  • Medium Project (14 NV, 32 tasks)", "medium_project"),
            ("  • Large Project (15 NV, 50 tasks)", "large_project")
        ]
        
        for text, value in datasets:
            tk.Radiobutton(data_frame, text=text, variable=self.dataset_var, 
                          value=value, bg='#ecf0f1', font=('Arial', 9),
                          command=self.on_dataset_change).pack(anchor='w', padx=20, pady=1)
        
        # Separator
        ttk.Separator(data_frame, orient='horizontal').pack(fill='x', pady=5)
        
        # Radio button cho upload file
        tk.Radiobutton(data_frame, text="Tải lên file tùy chỉnh", 
                      variable=self.data_source_var, value="upload", 
                      bg='#ecf0f1', font=('Arial', 9, 'bold'),
                      command=self.on_data_source_change).pack(anchor='w', pady=2)
        
        # Khung upload file
        self.upload_frame = tk.Frame(data_frame, bg='#ecf0f1')
        self.upload_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # File công việc
        tk.Label(self.upload_frame, text="File công việc:", 
                bg='#ecf0f1', font=('Arial', 8)).grid(row=0, column=0, sticky='w', pady=2)
        self.tasks_file_label = tk.Label(self.upload_frame, text="Chưa chọn file", 
                                         bg='#ecf0f1', font=('Arial', 8), 
                                         fg='gray', anchor='w', width=18)
        self.tasks_file_label.grid(row=0, column=1, sticky='w', pady=2, padx=2)
        self.upload_tasks_btn = tk.Button(self.upload_frame, text="📂 Chọn", 
                                         font=('Arial', 8), command=self.upload_tasks_file,
                                         state='disabled', width=8)
        self.upload_tasks_btn.grid(row=0, column=2, pady=2, padx=2)
        
        # File nhân viên
        tk.Label(self.upload_frame, text="File nhân viên:", 
                bg='#ecf0f1', font=('Arial', 8)).grid(row=1, column=0, sticky='w', pady=2)
        self.employees_file_label = tk.Label(self.upload_frame, text="Chưa chọn file", 
                                            bg='#ecf0f1', font=('Arial', 8), 
                                            fg='gray', anchor='w', width=18)
        self.employees_file_label.grid(row=1, column=1, sticky='w', pady=2, padx=2)
        self.upload_employees_btn = tk.Button(self.upload_frame, text="📂 Chọn", 
                                             font=('Arial', 8), command=self.upload_employees_file,
                                             state='disabled', width=8)
        self.upload_employees_btn.grid(row=1, column=2, pady=2, padx=2)
        
        # Chọn mô hình
        model_frame = tk.LabelFrame(left_frame, text="Chọn mô hình", 
                                    font=('Arial', 10, 'bold'), bg='#ecf0f1', padx=10, pady=10)
        model_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.model_var = tk.StringVar(value="Advanced")
        models = [
            ("Baseline (Backtracking cơ bản)", "Baseline"),
            ("Advanced (AC-3 + MRV + LCV + FC)", "Advanced")
        ]
        
        for text, value in models:
            tk.Radiobutton(model_frame, text=text, variable=self.model_var, 
                          value=value, bg='#ecf0f1', font=('Arial', 9)).pack(anchor='w', pady=2)
        
        # Thời gian thực hiện
        time_frame = tk.LabelFrame(left_frame, text="Thời gian thực hiện", 
                                   font=('Arial', 10, 'bold'), bg='#ecf0f1', padx=10, pady=10)
        time_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(time_frame, text="Ngày bắt đầu (dd/mm/yyyy):", 
                font=('Arial', 9), bg='#ecf0f1').pack(anchor='w', pady=2)
        self.start_date_entry = tk.Entry(time_frame, font=('Arial', 9), width=25)
        self.start_date_entry.pack(pady=2)
        self.start_date_entry.insert(0, "13/04/2005")
        
        tk.Label(time_frame, text="Ngày kết thúc (dd/mm/yyyy):", 
                font=('Arial', 9), bg='#ecf0f1').pack(anchor='w', pady=2)
        self.end_date_entry = tk.Entry(time_frame, font=('Arial', 9), width=25)
        self.end_date_entry.pack(pady=2)
        self.end_date_entry.insert(0, "30/04/2005")
        
        # Nút thực hiện
        self.solve_btn = tk.Button(left_frame, text="🚀 Giải Bài Toán", 
                                   font=('Arial', 11, 'bold'), bg='#27ae60', fg='white',
                                   command=self.solve_single_model, height=2)
        self.solve_btn.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút xuất
        self.export_single_btn = tk.Button(left_frame, text="📊 Xuất Kết Quả", 
                                          font=('Arial', 11, 'bold'), bg='#3498db', fg='white',
                                          command=self.export_single_result, height=2, state='disabled')
        self.export_single_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # ==================== CỘT PHẢI: HIỂN THỊ KẾT QUẢ ====================
        right_frame = tk.Frame(main_container, bg='white')
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(right_frame, text="HIỂN THỊ KẾT QUẢ ĐƯỢC SẮP XẾP", 
                font=('Arial', 12, 'bold'), bg='white').pack(pady=5)
        
        # Bảng kết quả
        table_frame = tk.Frame(right_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ('Task_ID', 'Task_Name', 'Employee', 'Start', 'End', 
                  'Duration', 'Priority')
        
        self.result_tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                       yscrollcommand=scrollbar_y.set,
                                       xscrollcommand=scrollbar_x.set, height=20)
        
        scrollbar_y.config(command=self.result_tree.yview)
        scrollbar_x.config(command=self.result_tree.xview)
        
        # Định nghĩa tiêu đề
        headers = {
            'Task_ID': 'Mã CV',
            'Task_Name': 'Tên Công Việc',
            'Employee': 'Nhân Viên',
            'Start': 'Bắt Đầu',
            'End': 'Kết Thúc',
            'Duration': 'T.Lượng',
            'Priority': 'Ưu Tiên'
        }
        
        for col in columns:
            self.result_tree.heading(col, text=headers[col])
            self.result_tree.column(col, width=100, anchor='center')
        
        self.result_tree.column('Task_Name', width=250, anchor='w')
        self.result_tree.column('Employee', width=150, anchor='w')
        
        self.result_tree.pack(fill=tk.BOTH, expand=True)
        
        # Style cho Treeview
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 9), rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 9, 'bold'))
        
    def setup_compare_tab(self):
        """Thiết lập tab so sánh hiệu năng với biểu đồ"""
        # Khung chính - chia 2 cột
        main_container = tk.Frame(self.compare_tab, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ==================== CỘT TRÁI: SO SÁNH HIỆU NĂNG ====================
        left_frame = tk.Frame(main_container, bg='#ecf0f1', width=350, relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_frame.pack_propagate(False)
        
        tk.Label(left_frame, text="SO SÁNH HIỆU NĂNG", 
                font=('Arial', 12, 'bold'), bg='#ecf0f1').pack(pady=10)
        
        # Chọn dataset
        data_frame = tk.LabelFrame(left_frame, text="Chọn file dữ liệu", 
                                   font=('Arial', 10, 'bold'), bg='#ecf0f1', padx=10, pady=10)
        data_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Radio button cho datasets có sẵn
        self.compare_data_source_var = tk.StringVar(value="predefined")
        tk.Radiobutton(data_frame, text="Sử dụng dữ liệu có sẵn", 
                      variable=self.compare_data_source_var, value="predefined", 
                      bg='#ecf0f1', font=('Arial', 9, 'bold')).pack(anchor='w', pady=2)
        
        self.compare_dataset_var = tk.StringVar(value="medium_project")
        datasets = [
            ("  • Small Project (5 NV, 20 tasks)", "small_project"),
            ("  • Medium Project (14 NV, 32 tasks)", "medium_project"),
            ("  • Large Project (15 NV, 50 tasks)", "large_project")
        ]
        
        for text, value in datasets:
            tk.Radiobutton(data_frame, text=text, variable=self.compare_dataset_var, 
                          value=value, bg='#ecf0f1', font=('Arial', 9)).pack(anchor='w', padx=20, pady=1)
        
        # Separator
        ttk.Separator(data_frame, orient='horizontal').pack(fill='x', pady=5)
        
        # Radio button cho upload file
        tk.Radiobutton(data_frame, text="Tải lên file tùy chỉnh", 
                      variable=self.compare_data_source_var, value="upload", 
                      bg='#ecf0f1', font=('Arial', 9, 'bold')).pack(anchor='w', pady=2)
        
        # Khung upload file cho compare tab
        self.compare_upload_frame = tk.Frame(data_frame, bg='#ecf0f1')
        self.compare_upload_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # File công việc
        tk.Label(self.compare_upload_frame, text="File công việc:", 
                bg='#ecf0f1', font=('Arial', 8)).grid(row=0, column=0, sticky='w', pady=2)
        self.compare_tasks_file_label = tk.Label(self.compare_upload_frame, text="Chưa chọn", 
                                         bg='#ecf0f1', font=('Arial', 8), 
                                         fg='gray', anchor='w', width=18)
        self.compare_tasks_file_label.grid(row=0, column=1, sticky='w', pady=2, padx=2)
        self.compare_upload_tasks_btn = tk.Button(self.compare_upload_frame, text="📂", 
                                         font=('Arial', 8), command=self.compare_upload_tasks_file,
                                         state='disabled', width=5)
        self.compare_upload_tasks_btn.grid(row=0, column=2, pady=2, padx=2)
        
        # File nhân viên
        tk.Label(self.compare_upload_frame, text="File nhân viên:", 
                bg='#ecf0f1', font=('Arial', 8)).grid(row=1, column=0, sticky='w', pady=2)
        self.compare_employees_file_label = tk.Label(self.compare_upload_frame, text="Chưa chọn", 
                                            bg='#ecf0f1', font=('Arial', 8), 
                                            fg='gray', anchor='w', width=18)
        self.compare_employees_file_label.grid(row=1, column=1, sticky='w', pady=2, padx=2)
        self.compare_upload_employees_btn = tk.Button(self.compare_upload_frame, text="📂", 
                                             font=('Arial', 8), command=self.compare_upload_employees_file,
                                             state='disabled', width=5)
        self.compare_upload_employees_btn.grid(row=1, column=2, pady=2, padx=2)
        
        # Bind event để enable/disable upload buttons
        self.compare_data_source_var.trace('w', self.on_compare_data_source_change)
        
        # Thời gian
        time_frame = tk.LabelFrame(left_frame, text="Thời gian thực hiện", 
                                   font=('Arial', 10, 'bold'), bg='#ecf0f1', padx=10, pady=10)
        time_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(time_frame, text="Ngày bắt đầu (dd/mm/yyyy):", 
                font=('Arial', 9), bg='#ecf0f1').pack(anchor='w', pady=2)
        self.compare_start_entry = tk.Entry(time_frame, font=('Arial', 9), width=25)
        self.compare_start_entry.pack(pady=2)
        self.compare_start_entry.insert(0, "13/04/2005")
        
        tk.Label(time_frame, text="Ngày kết thúc (dd/mm/yyyy):", 
                font=('Arial', 9), bg='#ecf0f1').pack(anchor='w', pady=2)
        self.compare_end_entry = tk.Entry(time_frame, font=('Arial', 9), width=25)
        self.compare_end_entry.pack(pady=2)
        self.compare_end_entry.insert(0, "30/04/2005")
        
        # Nút so sánh
        self.compare_btn = tk.Button(left_frame, text="⚡ So Sánh 2 Mô Hình", 
                                    font=('Arial', 11, 'bold'), bg='#e74c3c', fg='white',
                                    command=self.compare_models, height=2)
        self.compare_btn.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút xuất so sánh
        self.export_compare_btn = tk.Button(left_frame, text="📊 Xuất So Sánh (.xlsx)", 
                                           font=('Arial', 11, 'bold'), bg='#9b59b6', fg='white',
                                           command=self.export_comparison, height=2, state='disabled')
        self.export_compare_btn.pack(fill=tk.X, padx=10, pady=5)
        
        # Thông tin so sánh
        info_frame = tk.LabelFrame(left_frame, text="Kết quả so sánh", 
                                   font=('Arial', 10, 'bold'), bg='#ecf0f1', padx=10, pady=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.compare_info_text = tk.Text(info_frame, wrap=tk.WORD, 
                                         font=('Courier New', 8), height=10)
        self.compare_info_text.pack(fill=tk.BOTH, expand=True)
        
        # ==================== CỘT PHẢI: BIỂU ĐỒ ====================
        right_frame = tk.Frame(main_container, bg='white')
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(right_frame, text="BIỂU ĐỒ SO SÁNH", 
                font=('Arial', 12, 'bold'), bg='white').pack(pady=5)
        
        # Khung chứa biểu đồ
        self.chart_frame = tk.Frame(right_frame, bg='white')
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tạo figure matplotlib
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Vẽ biểu đồ mặc định (trống)
        self.draw_empty_chart()
        
    def draw_empty_chart(self):
        """Vẽ biểu đồ trống ban đầu"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Nhấn "So Sánh 2 Mô Hình"\nđể hiển thị biểu đồ', 
               ha='center', va='center', fontsize=14, color='gray')
        ax.axis('off')
        self.canvas.draw()
        
    def on_dataset_change(self):
        """Xử lý khi thay đổi dataset"""
        self.current_dataset = self.dataset_var.get()
        self.status_bar.config(text=f"Đã chọn dữ liệu: {self.current_dataset}")
    
    def on_data_source_change(self):
        """Xử lý khi thay đổi nguồn dữ liệu (có sẵn hoặc upload)"""
        if self.data_source_var.get() == "upload":
            # Kích hoạt nút upload
            self.upload_tasks_btn.config(state='normal')
            self.upload_employees_btn.config(state='normal')
            self.use_uploaded_files = True
            self.status_bar.config(text="Vui lòng tải lên 2 file: công việc và nhân viên")
        else:
            # Vô hiệu hóa nút upload
            self.upload_tasks_btn.config(state='disabled')
            self.upload_employees_btn.config(state='disabled')
            self.use_uploaded_files = False
            self.uploaded_tasks_file = None
            self.uploaded_employees_file = None
            self.tasks_file_label.config(text="Chưa chọn file", fg='gray')
            self.employees_file_label.config(text="Chưa chọn file", fg='gray')
            self.status_bar.config(text=f"Sử dụng dữ liệu có sẵn: {self.dataset_var.get()}")
    
    def validate_tasks_file(self, filepath):
        """
        Validate file công việc
        Yêu cầu: ID,TenTask,YeuCauKyNang,ThoiLuong (gio),PhuThuoc,Deadline (ngay),DoUuTien
        """
        try:
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            # Kiểm tra các cột bắt buộc
            required_columns = ['ID', 'TenTask', 'YeuCauKyNang', 'ThoiLuong (gio)', 
                              'PhuThuoc', 'Deadline (ngay)', 'DoUuTien']
            
            missing_columns = []
            for col in required_columns:
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                return False, f"Thiếu các cột: {', '.join(missing_columns)}"
            
            # Kiểm tra dữ liệu
            if len(df) == 0:
                return False, "File không có dữ liệu"
            
            # Kiểm tra ID không trống
            if df['ID'].isna().any() or (df['ID'] == '').any():
                return False, "Có ID công việc bị trống"
            
            # Kiểm tra ThoiLuong phải là số
            try:
                df['ThoiLuong (gio)'].astype(int)
            except:
                return False, "Cột 'ThoiLuong (gio)' phải là số nguyên"
            
            # Kiểm tra Deadline phải là số
            try:
                df['Deadline (ngay)'].astype(int)
            except:
                return False, "Cột 'Deadline (ngay)' phải là số nguyên"
            
            # Kiểm tra DoUuTien phải là số
            try:
                df['DoUuTien'].astype(int)
            except:
                return False, "Cột 'DoUuTien' phải là số nguyên"
            
            return True, "File hợp lệ"
            
        except Exception as e:
            return False, f"Lỗi đọc file: {str(e)}"
    
    def validate_employees_file(self, filepath):
        """
        Validate file nhân viên
        Yêu cầu: ID,Ten,KyNang,SucChua (gio/ngay)
        """
        try:
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            # Kiểm tra các cột bắt buộc
            required_columns = ['ID', 'Ten', 'KyNang', 'SucChua (gio/ngay)']
            
            missing_columns = []
            for col in required_columns:
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                return False, f"Thiếu các cột: {', '.join(missing_columns)}"
            
            # Kiểm tra dữ liệu
            if len(df) == 0:
                return False, "File không có dữ liệu"
            
            # Kiểm tra ID không trống
            if df['ID'].isna().any() or (df['ID'] == '').any():
                return False, "Có ID nhân viên bị trống"
            
            # Kiểm tra SucChua phải là số
            try:
                df['SucChua (gio/ngay)'].astype(int)
            except:
                return False, "Cột 'SucChua (gio/ngay)' phải là số nguyên"
            
            return True, "File hợp lệ"
            
        except Exception as e:
            return False, f"Lỗi đọc file: {str(e)}"
    
    def upload_tasks_file(self):
        """Upload và validate file công việc"""
        filepath = filedialog.askopenfilename(
            title="Chọn file công việc (CSV)",
            filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
        )
        
        if not filepath:
            return
        
        # Validate file
        is_valid, message = self.validate_tasks_file(filepath)
        
        if is_valid:
            self.uploaded_tasks_file = filepath
            # Hiển thị tên file (chỉ lấy tên, không lấy đường dẫn)
            filename = filepath.split('/')[-1].split('\\')[-1]
            self.tasks_file_label.config(text=filename[:18] + "..." if len(filename) > 18 else filename, 
                                        fg='green')
            self.status_bar.config(text=f"✓ Đã tải file công việc: {filename}")
            
            # Kiểm tra nếu đã có cả 2 file
            self.check_upload_complete()
        else:
            messagebox.showerror("Lỗi Định Dạng File", 
                               f"File công việc không đúng định dạng!\n\n{message}\n\n"
                               f"Yêu cầu:\n"
                               f"- Các cột: ID, TenTask, YeuCauKyNang, ThoiLuong (gio), "
                               f"PhuThuoc, Deadline (ngay), DoUuTien\n"
                               f"- ID không được trống\n"
                               f"- ThoiLuong, Deadline, DoUuTien phải là số")
            self.tasks_file_label.config(text="File không hợp lệ", fg='red')
    
    def upload_employees_file(self):
        """Upload và validate file nhân viên"""
        filepath = filedialog.askopenfilename(
            title="Chọn file nhân viên (CSV)",
            filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
        )
        
        if not filepath:
            return
        
        # Validate file
        is_valid, message = self.validate_employees_file(filepath)
        
        if is_valid:
            self.uploaded_employees_file = filepath
            # Hiển thị tên file
            filename = filepath.split('/')[-1].split('\\')[-1]
            self.employees_file_label.config(text=filename[:18] + "..." if len(filename) > 18 else filename, 
                                           fg='green')
            self.status_bar.config(text=f"✓ Đã tải file nhân viên: {filename}")
            
            # Kiểm tra nếu đã có cả 2 file
            self.check_upload_complete()
        else:
            messagebox.showerror("Lỗi Định Dạng File", 
                               f"File nhân viên không đúng định dạng!\n\n{message}\n\n"
                               f"Yêu cầu:\n"
                               f"- Các cột: ID, Ten, KyNang, SucChua (gio/ngay)\n"
                               f"- ID không được trống\n"
                               f"- SucChua phải là số")
            self.employees_file_label.config(text="File không hợp lệ", fg='red')
    
    def check_upload_complete(self):
        """Kiểm tra xem đã upload đủ 2 file chưa"""
        if self.uploaded_tasks_file and self.uploaded_employees_file:
            messagebox.showinfo("Thành Công", 
                              "✓ Đã tải đủ 2 file!\n\n"
                              "Bạn có thể bắt đầu giải bài toán.")
            self.status_bar.config(text="✓ Đã tải đủ file, sẵn sàng giải bài toán")
    
    def on_compare_data_source_change(self, *args):
        """Xử lý khi thay đổi nguồn dữ liệu ở tab so sánh"""
        if self.compare_data_source_var.get() == "upload":
            self.compare_upload_tasks_btn.config(state='normal')
            self.compare_upload_employees_btn.config(state='normal')
        else:
            self.compare_upload_tasks_btn.config(state='disabled')
            self.compare_upload_employees_btn.config(state='disabled')
            self.compare_tasks_file_label.config(text="Chưa chọn", fg='gray')
            self.compare_employees_file_label.config(text="Chưa chọn", fg='gray')
    
    def compare_upload_tasks_file(self):
        """Upload file công việc cho tab so sánh"""
        filepath = filedialog.askopenfilename(
            title="Chọn file công việc (CSV)",
            filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
        )
        
        if not filepath:
            return
        
        is_valid, message = self.validate_tasks_file(filepath)
        
        if is_valid:
            self.compare_uploaded_tasks_file = filepath
            filename = filepath.split('/')[-1].split('\\')[-1]
            self.compare_tasks_file_label.config(text=filename[:18] + "..." if len(filename) > 18 else filename, 
                                        fg='green')
            self.status_bar.config(text=f"✓ Đã tải file công việc: {filename}")
        else:
            messagebox.showerror("Lỗi Định Dạng File", 
                               f"File công việc không đúng định dạng!\n\n{message}")
            self.compare_tasks_file_label.config(text="File không hợp lệ", fg='red')
    
    def compare_upload_employees_file(self):
        """Upload file nhân viên cho tab so sánh"""
        filepath = filedialog.askopenfilename(
            title="Chọn file nhân viên (CSV)",
            filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
        )
        
        if not filepath:
            return
        
        is_valid, message = self.validate_employees_file(filepath)
        
        if is_valid:
            self.compare_uploaded_employees_file = filepath
            filename = filepath.split('/')[-1].split('\\')[-1]
            self.compare_employees_file_label.config(text=filename[:18] + "..." if len(filename) > 18 else filename, 
                                           fg='green')
            self.status_bar.config(text=f"✓ Đã tải file nhân viên: {filename}")
        else:
            messagebox.showerror("Lỗi Định Dạng File", 
                               f"File nhân viên không đúng định dạng!\n\n{message}")
            self.compare_employees_file_label.config(text="File không hợp lệ", fg='red')
        
    def solve_single_model(self):
        """Giải bài toán với 1 mô hình được chọn"""
        try:
            # Kiểm tra nếu dùng file upload
            if self.use_uploaded_files:
                if not self.uploaded_tasks_file or not self.uploaded_employees_file:
                    messagebox.showwarning("Thiếu File", 
                                         "Vui lòng tải lên đầy đủ 2 file:\n"
                                         "- File công việc\n"
                                         "- File nhân viên")
                    return
                
                # Tạo thư mục tạm để lưu file upload
                import os
                import shutil
                temp_folder = "datasets/uploaded_temp"
                os.makedirs(temp_folder, exist_ok=True)
                
                # Copy file vào thư mục tạm với tên chuẩn
                shutil.copy(self.uploaded_tasks_file, os.path.join(temp_folder, "congviec.csv"))
                shutil.copy(self.uploaded_employees_file, os.path.join(temp_folder, "nhanvien.csv"))
                
                dataset_folder = temp_folder
            else:
                dataset_folder = f"datasets/{self.dataset_var.get()}"
            
            # Lấy thông tin
            start_date_str = self.start_date_entry.get().strip()
            end_date_str = self.end_date_entry.get().strip()
            
            project_start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
            project_end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
            project_start_date = project_start_date.replace(hour=8, minute=0, second=0)
            project_end_date = project_end_date.replace(hour=17, minute=0, second=0)
            
            model = self.model_var.get()
            
            # Vô hiệu hóa nút
            self.solve_btn.config(state='disabled')
            self.status_bar.config(text=f"Đang giải bằng {model}...")
            self.root.update()
            
            # Giải bài toán
            start_time = time.time()
            if model == "Baseline":
                result = baseline.solve_csp(dataset_folder, project_start_date, project_end_date)
            else:
                result = advanced.solve_csp(dataset_folder, project_start_date, project_end_date)
            
            exec_time = time.time() - start_time
            
            if result.solution_found:
                self.display_single_result(result)
                self.export_single_btn.config(state='normal')
                self.status_bar.config(text=f"✓ Giải xong bằng {model} trong {exec_time:.4f} giây")
                
                # Lưu kết quả
                if model == "Baseline":
                    self.baseline_result = result
                    self.baseline_time = exec_time
                else:
                    self.advanced_result = result
                    self.advanced_time = exec_time
            else:
                messagebox.showwarning("Không Tìm Thấy Lời Giải", 
                                     f"{model} không tìm thấy lời giải cho bài toán này!")
                self.status_bar.config(text="✗ Không tìm thấy lời giải")
            
            self.solve_btn.config(state='normal')
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi:\n{str(e)}")
            self.solve_btn.config(state='normal')
            self.status_bar.config(text="✗ Lỗi khi giải bài toán")
    
    def solve_with_uploaded_files(self, solver_module, dataset_folder, 
                                  project_start_date, project_end_date):
        """Giải bài toán với file upload"""
        # Modify dataset_folder để load_data có thể tìm đúng file
        import os
        
        # Load data từ thư mục uploaded
        tasks_file = os.path.join(dataset_folder, "congviec_uploaded.csv")
        employees_file = os.path.join(dataset_folder, "nhanvien_uploaded.csv")
        
        # Gọi load_data với path tùy chỉnh
        cac_tacvu, cac_nhansu = self.load_custom_data(tasks_file, employees_file)
        
        # Tạo CSP object
        if solver_module == baseline:
            csp = baseline.CSP(cac_tacvu, cac_nhansu, project_start_date, project_end_date)
            baseline.recursive_backtracking(csp)
        else:
            csp = advanced.CSP(cac_tacvu, cac_nhansu, project_start_date, project_end_date)
            advanced.initialize_domains(csp)
            initial_domain_size = sum(len(domain) for domain in csp.domains.values())
            
            is_consistent = advanced.ac3_preprocess(csp)
            if not is_consistent:
                return csp
            
            initial_domains = {}
            for task_id in csp.domains:
                initial_domains[task_id] = csp.domains[task_id].copy()
            
            advanced.recursive_backtracking(csp, initial_domains)
        
        return csp
    
    def load_custom_data(self, tasks_file, employees_file):
        """Load dữ liệu từ file tùy chỉnh"""
        import csv
        
        # Đọc danh sách các tác vụ
        cac_tacvu = []
        with open(tasks_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'ID' in row and row['ID'].strip():
                    dependencies = []
                    if 'PhuThuoc' in row and row['PhuThuoc'].strip():
                        # Xử lý cả dấu phẩy và khoảng trắng
                        deps_str = row['PhuThuoc'].strip()
                        # Tách bằng cả dấu phẩy và khoảng trắng
                        deps_list = deps_str.replace(',', ' ').split()
                        dependencies = [dep.strip() for dep in deps_list if dep.strip()]
                    
                    tacvu = baseline.TacVu(
                        task_id=row['ID'].strip(),
                        name=row.get('TenTask','').strip(),
                        required_skill=row.get('YeuCauKyNang','').strip(),
                        duration=int(row.get('ThoiLuong (gio)', '0')),
                        dependencies=dependencies,
                        deadline=int(row.get('Deadline (ngay)', '0')),
                        priority=int(row.get('DoUuTien', '0'))
                    )
                    cac_tacvu.append(tacvu)
        
        # Đọc danh sách nhân sự
        cac_nhansu = []
        with open(employees_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'ID' in row and row['ID'].strip():
                    skills = [skill.strip() for skill in row.get('KyNang','').split(',') if skill.strip()]
                    nhansu = baseline.NhanSu(
                        emp_id=row['ID'].strip(),
                        name=row.get('Ten','').strip(),
                        skills=skills,
                        daily_capacity=int(row.get('SucChua (gio/ngay)', '8'))
                    )
                    cac_nhansu.append(nhansu)
        
        return cac_tacvu, cac_nhansu
            
    def display_single_result(self, result):
        """Hiển thị kết quả lên bảng"""
        # Xóa dữ liệu cũ
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # Thêm dữ liệu mới
        sorted_assignments = sorted(result.assignment.items(), 
                                   key=lambda x: x[1].start_time)
        
        for task_id, assignment in sorted_assignments:
            tacvu = next(t for t in result.cac_tacvu if t.id == task_id)
            start_time = assignment.start_time
            end_time = start_time + timedelta(hours=tacvu.duration)
            
            self.result_tree.insert('', 'end', values=(
                tacvu.id,
                tacvu.name,
                f"{assignment.nhansu.name} ({assignment.nhansu.id})",
                start_time.strftime('%d/%m %H:%M'),
                end_time.strftime('%d/%m %H:%M'),
                f"{tacvu.duration}h",
                tacvu.priority
            ))
            
    def compare_models(self):
        """So sánh cả 2 mô hình"""
        try:
            # Kiểm tra nếu dùng file upload
            if self.compare_data_source_var.get() == "upload":
                if not self.compare_uploaded_tasks_file or not self.compare_uploaded_employees_file:
                    messagebox.showwarning("Thiếu File", 
                                         "Vui lòng tải lên đầy đủ 2 file:\n"
                                         "- File công việc\n"
                                         "- File nhân viên")
                    return
                
                # Tạo thư mục tạm để lưu file upload
                import os
                import shutil
                temp_folder = "datasets/uploaded_temp"
                os.makedirs(temp_folder, exist_ok=True)
                
                # Copy file vào thư mục tạm với tên chuẩn
                shutil.copy(self.compare_uploaded_tasks_file, os.path.join(temp_folder, "congviec.csv"))
                shutil.copy(self.compare_uploaded_employees_file, os.path.join(temp_folder, "nhanvien.csv"))
                
                dataset_folder = temp_folder
                use_upload = True
            else:
                dataset_folder = f"datasets/{self.compare_dataset_var.get()}"
                use_upload = False
            
            # Lấy thông tin
            start_date_str = self.compare_start_entry.get().strip()
            end_date_str = self.compare_end_entry.get().strip()
            
            project_start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
            project_end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
            project_start_date = project_start_date.replace(hour=8, minute=0, second=0)
            project_end_date = project_end_date.replace(hour=17, minute=0, second=0)
            
            # Vô hiệu hóa nút
            self.compare_btn.config(state='disabled')
            self.status_bar.config(text="Đang so sánh 2 mô hình...")
            self.root.update()
            
            # Giải bằng Baseline
            self.status_bar.config(text="Đang giải bằng Baseline...")
            self.root.update()
            start_time = time.time()
            self.baseline_result = baseline.solve_csp(dataset_folder, project_start_date, project_end_date)
            self.baseline_time = time.time() - start_time
            
            # Giải bằng Advanced
            self.status_bar.config(text="Đang giải bằng Advanced...")
            self.root.update()
            start_time = time.time()
            self.advanced_result = advanced.solve_csp(dataset_folder, project_start_date, project_end_date)
            self.advanced_time = time.time() - start_time
            
            # Tính toán metrics và vẽ biểu đồ
            self.calculate_and_display_comparison()
            
            self.compare_btn.config(state='normal')
            self.export_compare_btn.config(state='normal')
            self.status_bar.config(text="✓ Hoàn thành so sánh")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi so sánh:\n{str(e)}")
            self.compare_btn.config(state='normal')
            self.status_bar.config(text="✗ Lỗi khi so sánh")
            
    def calculate_makespan(self, csp_result):
        """Tính thời gian hoàn thành dự án (ngày)"""
        if not csp_result.assignment:
            return 0
        
        max_end_time = None
        for task_id, assignment in csp_result.assignment.items():
            task = next(t for t in csp_result.cac_tacvu if t.id == task_id)
            end_time = assignment.start_time + timedelta(hours=task.duration)
            if max_end_time is None or end_time > max_end_time:
                max_end_time = end_time
        
        makespan = max_end_time - csp_result.project_start_date
        return makespan.total_seconds() / 86400  # Trả về số ngày
    
    def calculate_constraint_satisfaction(self, csp_result):
        """
        Tính % ràng buộc thỏa mãn
        Kiểm tra tất cả ràng buộc cứng: kỹ năng, phụ thuộc, deadline, sức chứa, khung giờ
        """
        if not csp_result.assignment:
            return 0.0
        
        total_constraints = 0
        satisfied_constraints = 0
        
        for task_id, assignment in csp_result.assignment.items():
            task = next(t for t in csp_result.cac_tacvu if t.id == task_id)
            start_time = assignment.start_time
            end_time = start_time + timedelta(hours=task.duration)
            
            # 1. Ràng buộc kỹ năng
            total_constraints += 1
            if task.required_skill in assignment.nhansu.skills:
                satisfied_constraints += 1
            
            # 2. Ràng buộc phụ thuộc
            for dep_id in task.dependencies:
                total_constraints += 1
                if dep_id in csp_result.assignment:
                    dep_assignment = csp_result.assignment[dep_id]
                    dep_task = next(t for t in csp_result.cac_tacvu if t.id == dep_id)
                    dep_end = dep_assignment.start_time + timedelta(hours=dep_task.duration)
                    if start_time >= dep_end:
                        satisfied_constraints += 1
            
            # 3. Ràng buộc deadline
            total_constraints += 1
            deadline = csp_result.project_start_date + timedelta(days=task.deadline)
            if end_time <= deadline:
                satisfied_constraints += 1
            
            # 4. Ràng buộc khung thời gian dự án
            total_constraints += 1
            if (start_time >= csp_result.project_start_date and 
                end_time <= csp_result.project_end_date):
                satisfied_constraints += 1
            
            # 5. Ràng buộc khung giờ làm việc (8h-17h)
            total_constraints += 1
            if (start_time.hour >= 8 and start_time.hour < 17 and
                end_time.hour >= 8 and end_time.hour <= 17):
                satisfied_constraints += 1
        
        # 6. Ràng buộc sức chứa (kiểm tra mỗi nhân viên mỗi ngày)
        for nhansu in csp_result.cac_nhansu:
            # Nhóm công việc theo ngày
            daily_workload = {}
            for task_id, assignment in csp_result.assignment.items():
                if assignment.nhansu.id == nhansu.id:
                    task = next(t for t in csp_result.cac_tacvu if t.id == task_id)
                    work_date = assignment.start_time.date()
                    if work_date not in daily_workload:
                        daily_workload[work_date] = 0
                    daily_workload[work_date] += task.duration
            
            # Kiểm tra mỗi ngày
            for work_date, total_hours in daily_workload.items():
                total_constraints += 1
                if total_hours <= nhansu.daily_capacity:
                    satisfied_constraints += 1
        
        return (satisfied_constraints / total_constraints * 100.0) if total_constraints > 0 else 0.0
    
    def calculate_workload_std_dev(self, csp_result):
        """
        Tính độ lệch chuẩn workload (Standard Deviation)
        Đo sự phân bố công việc giữa các nhân viên
        """
        if not csp_result.assignment:
            return 0.0
        
        # Tính workload cho mỗi nhân viên
        workloads = []
        for nhansu in csp_result.cac_nhansu:
            total_hours = 0
            for task_id, assignment in csp_result.assignment.items():
                if assignment.nhansu.id == nhansu.id:
                    task = next(t for t in csp_result.cac_tacvu if t.id == task_id)
                    total_hours += task.duration
            workloads.append(total_hours)
        
        if not workloads:
            return 0.0
        
        # Tính độ lệch chuẩn
        if len(workloads) > 1:
            std_dev = statistics.stdev(workloads)
        else:
            std_dev = 0.0
        
        return std_dev
    
    
    def calculate_and_display_comparison(self):
        """Tính toán metrics và hiển thị biểu đồ so sánh"""
        # Tính metrics cho Baseline
        baseline_makespan = self.calculate_makespan(self.baseline_result)
        baseline_constraint_satisfaction = self.calculate_constraint_satisfaction(self.baseline_result)
        baseline_workload_std = self.calculate_workload_std_dev(self.baseline_result)
        
        # Tính metrics cho Advanced
        advanced_makespan = self.calculate_makespan(self.advanced_result)
        advanced_constraint_satisfaction = self.calculate_constraint_satisfaction(self.advanced_result)
        advanced_workload_std = self.calculate_workload_std_dev(self.advanced_result)
        
        # Lưu để export
        self.comparison_data = {
            'Baseline': {
                'time': self.baseline_time,
                'makespan': baseline_makespan,
                'constraint_satisfaction': baseline_constraint_satisfaction,
                'workload_std_dev': baseline_workload_std,
                'backtrack': 0,  # Baseline không track
                'ac3_pruned': 0,
                'fc_pruned': 0
            },
            'Advanced': {
                'time': self.advanced_time,
                'makespan': advanced_makespan,
                'constraint_satisfaction': advanced_constraint_satisfaction,
                'workload_std_dev': advanced_workload_std,
                'backtrack': self.advanced_result.backtrack_count,
                'ac3_pruned': self.advanced_result.ac3_pruned_count,
                'fc_pruned': self.advanced_result.fc_pruned_count
            }
        }
        
        # Vẽ biểu đồ
        self.draw_comparison_chart()
        
        # Hiển thị thông tin text
        self.display_comparison_text()
        
    def draw_comparison_chart(self):
        """Vẽ biểu đồ so sánh 3 tiêu chí"""
        self.fig.clear()
        
        data = self.comparison_data
        
        # Tạo 3 subplots
        # 1. Makespan
        ax1 = self.fig.add_subplot(2, 2, 1)
        categories = ['Baseline', 'Advanced']
        makespan_values = [data['Baseline']['makespan'], data['Advanced']['makespan']]
        colors = ['#e74c3c', '#27ae60']
        
        bars1 = ax1.bar(categories, makespan_values, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Ngày', fontsize=10)
        ax1.set_title('Thời Gian Hoàn Thành Dự Án\n(Makespan - Càng thấp càng tốt)', 
                     fontsize=11, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Thêm giá trị lên cột
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f} ngày', ha='center', va='bottom', fontsize=9)
        
        # 2. % Ràng Buộc Thỏa
        ax2 = self.fig.add_subplot(2, 2, 2)
        constraint_values = [data['Baseline']['constraint_satisfaction'], 
                            data['Advanced']['constraint_satisfaction']]
        
        bars2 = ax2.bar(categories, constraint_values, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_ylabel('%', fontsize=10)
        ax2.set_title('% Ràng Buộc Thỏa\n(Càng cao càng tốt)', 
                     fontsize=11, fontweight='bold')
        ax2.set_ylim([0, 105])
        ax2.grid(axis='y', alpha=0.3)
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # 3. Độ Lệch Chuẩn Workload
        ax3 = self.fig.add_subplot(2, 2, 3)
        workload_std_values = [data['Baseline']['workload_std_dev'], 
                              data['Advanced']['workload_std_dev']]
        
        bars3 = ax3.bar(categories, workload_std_values, color=colors, alpha=0.7, edgecolor='black')
        ax3.set_ylabel('Giờ', fontsize=10)
        ax3.set_title('Độ Lệch Chuẩn Workload\n(Càng thấp càng tốt)', 
                     fontsize=11, fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        # 4. Thời Gian Chạy
        ax4 = self.fig.add_subplot(2, 2, 4)
        time_values = [data['Baseline']['time'], data['Advanced']['time']]
        
        bars4 = ax4.bar(categories, time_values, color=colors, alpha=0.7, edgecolor='black')
        ax4.set_ylabel('Giây', fontsize=10)
        ax4.set_title('Thời Gian Chạy\n(Càng thấp càng tốt)', 
                     fontsize=11, fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)
        
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}s', ha='center', va='bottom', fontsize=9)
        
        self.fig.tight_layout()
        self.canvas.draw()
        
    def display_comparison_text(self):
        """Hiển thị thông tin so sánh dạng text"""
        data = self.comparison_data
        
        # Tính speedup
        speedup = data['Baseline']['time'] / data['Advanced']['time'] if data['Advanced']['time'] > 0 else 0
        
        info_text = f"""
╔════════════════════════════════════════╗
║      KẾT QUẢ SO SÁNH                  ║
╠════════════════════════════════════════╣

📊 THỜI GIAN THỰC THI:
  • Baseline:  {data['Baseline']['time']:.4f}s
  • Advanced:  {data['Advanced']['time']:.4f}s
  • Tăng tốc:  {speedup:.2f}x

⏱️ THỜI GIAN HOÀN THÀNH:
  • Baseline:  {data['Baseline']['makespan']:.1f} ngày
  • Advanced:  {data['Advanced']['makespan']:.1f} ngày
  • Cải thiện:  {data['Baseline']['makespan'] - data['Advanced']['makespan']:.1f} ngày

✓ % RÀNG BUỘC THỎA:
  • Baseline:  {data['Baseline']['constraint_satisfaction']:.1f}%
  • Advanced:  {data['Advanced']['constraint_satisfaction']:.1f}%

📊 ĐỘ LỆCH CHUẨN WORKLOAD:
  • Baseline:  {data['Baseline']['workload_std_dev']:.2f} giờ
  • Advanced:  {data['Advanced']['workload_std_dev']:.2f} giờ
  • (Càng thấp = phân bố càng đều)

⚙️ THUẬT TOÁN:
  • Backtrack:  {data['Advanced']['backtrack']} lần
  • AC-3 Pruned: {data['Advanced']['ac3_pruned']}
  • FC Pruned:   {data['Advanced']['fc_pruned']}

╚════════════════════════════════════════╝
"""
        
        self.compare_info_text.delete('1.0', tk.END)
        self.compare_info_text.insert('1.0', info_text)
        
    def export_single_result(self):
        """Xuất kết quả 1 mô hình"""
        model = self.model_var.get()
        result = self.baseline_result if model == "Baseline" else self.advanced_result
        
        if not result or not result.solution_found:
            messagebox.showwarning("Cảnh Báo", "Chưa có kết quả để xuất!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Lưu Kết Quả",
            defaultextension=".xlsx",
            filetypes=[('Excel Files', '*.xlsx'), ('CSV Files', '*.csv')],
            initialfile=f"task_assignment_{self.dataset_var.get()}_{model}.xlsx"
        )
        
        if not filename:
            return
        
        try:
            csv_data = []
            for task_id, assignment in result.assignment.items():
                task = next(t for t in result.cac_tacvu if t.id == task_id)
                start_time = assignment.start_time
                end_time = start_time + timedelta(hours=task.duration)
                
                csv_data.append({
                    'Task_ID': task.id,
                    'Task_Name': task.name,
                    'Employee_ID': assignment.nhansu.id,
                    'Employee_Name': assignment.nhansu.name,
                    'Start_Date': start_time.strftime('%d/%m/%Y'),
                    'Start_Time': start_time.strftime('%H:%M'),
                    'End_Date': end_time.strftime('%d/%m/%Y'),
                    'End_Time': end_time.strftime('%H:%M'),
                    'Duration': task.duration,
                    'Priority': task.priority
                })
            
            df = pd.DataFrame(csv_data)
            
            if filename.endswith('.xlsx'):
                df.to_excel(filename, index=False, engine='openpyxl')
            else:
                df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            messagebox.showinfo("Thành Công", f"Đã xuất kết quả ra:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file:\n{str(e)}")
            
    def export_comparison(self):
        """Xuất file so sánh 2 mô hình"""
        if not hasattr(self, 'comparison_data'):
            messagebox.showwarning("Cảnh Báo", "Chưa có dữ liệu so sánh!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Lưu So Sánh",
            defaultextension=".xlsx",
            filetypes=[('Excel Files', '*.xlsx')],
            initialfile=f"comparison_{self.compare_dataset_var.get()}.xlsx"
        )
        
        if not filename:
            return
        
        try:
            # Tạo file Excel với nhiều sheet
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Sheet 1: Tổng quan so sánh
                data = self.comparison_data
                summary_data = {
                    'Tiêu Chí': [
                        '(1) Tổng thời gian hoàn thành - Makespan (ngày)',
                        '(2) Độ lệch chuẩn workload (giờ)',
                        '(3) % ràng buộc thỏa (%)',
                        '(4) Thời gian chạy (giây)',
                        'Số lần Backtrack',
                        'AC-3 Pruned',
                        'Forward Checking Pruned'
                    ],
                    'Baseline': [
                        f"{data['Baseline']['makespan']:.2f}",
                        f"{data['Baseline']['workload_std_dev']:.2f}",
                        f"{data['Baseline']['constraint_satisfaction']:.2f}",
                        f"{data['Baseline']['time']:.4f}",
                        data['Baseline']['backtrack'],
                        data['Baseline']['ac3_pruned'],
                        data['Baseline']['fc_pruned']
                    ],
                    'Advanced': [
                        f"{data['Advanced']['makespan']:.2f}",
                        f"{data['Advanced']['workload_std_dev']:.2f}",
                        f"{data['Advanced']['constraint_satisfaction']:.2f}",
                        f"{data['Advanced']['time']:.4f}",
                        data['Advanced']['backtrack'],
                        data['Advanced']['ac3_pruned'],
                        data['Advanced']['fc_pruned']
                    ]
                }
                
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Tổng Quan', index=False)
                
                # Sheet 2: Baseline chi tiết
                if self.baseline_result and self.baseline_result.solution_found:
                    baseline_data = []
                    for task_id, assignment in self.baseline_result.assignment.items():
                        task = next(t for t in self.baseline_result.cac_tacvu if t.id == task_id)
                        start = assignment.start_time
                        end = start + timedelta(hours=task.duration)
                        
                        baseline_data.append({
                            'Task_ID': task.id,
                            'Task_Name': task.name,
                            'Employee': f"{assignment.nhansu.name} ({assignment.nhansu.id})",
                            'Start': start.strftime('%d/%m/%Y %H:%M'),
                            'End': end.strftime('%d/%m/%Y %H:%M'),
                            'Duration': task.duration,
                            'Priority': task.priority
                        })
                    
                    df_baseline = pd.DataFrame(baseline_data)
                    df_baseline.to_excel(writer, sheet_name='Baseline', index=False)
                
                # Sheet 3: Advanced chi tiết
                if self.advanced_result and self.advanced_result.solution_found:
                    advanced_data = []
                    for task_id, assignment in self.advanced_result.assignment.items():
                        task = next(t for t in self.advanced_result.cac_tacvu if t.id == task_id)
                        start = assignment.start_time
                        end = start + timedelta(hours=task.duration)
                        
                        advanced_data.append({
                            'Task_ID': task.id,
                            'Task_Name': task.name,
                            'Employee': f"{assignment.nhansu.name} ({assignment.nhansu.id})",
                            'Start': start.strftime('%d/%m/%Y %H:%M'),
                            'End': end.strftime('%d/%m/%Y %H:%M'),
                            'Duration': task.duration,
                            'Priority': task.priority
                        })
                    
                    df_advanced = pd.DataFrame(advanced_data)
                    df_advanced.to_excel(writer, sheet_name='Advanced', index=False)
            
            messagebox.showinfo("Thành Công", f"Đã xuất so sánh ra:\n{filename}")
            self.status_bar.config(text=f"✓ Đã xuất file so sánh: {filename}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file:\n{str(e)}")

def main():
    """Hàm chính khởi chạy ứng dụng"""
    root = tk.Tk()
    app = CSPApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
