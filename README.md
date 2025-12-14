# Phân Công Công Việc Tối Ưu Cho Nhóm Dự Án Phần Mềm

## 📋 Mô tả dự án

Dự án này triển khai giải pháp phân công công việc tối ưu cho nhóm dự án phần mềm sử dụng **Constraint Satisfaction Problem (CSP)**. Hệ thống hỗ trợ quản lý dự án bằng cách tự động phân bổ nhiệm vụ cho nhân sự một cách khoa học, đảm bảo cân bằng tải và tối ưu hóa hiệu suất.

## 👥 Thông tin nhóm

**Nhóm 02** - Môn học: Trí Tuệ Nhân Tạo

- **Giáo viên hướng dẫn**: Phùng Thế Bảo
- **Nhóm trưởng**: Trần Quốc Đạt - 2033230061
- **Thành viên**:
  - Trần Thị Kiều Diễm - 2033230036
  - Nguyễn Minh Tiến - 2033230259
  - Phạm Nhật Nam - 2001230531

## 🎯 Mục tiêu nghiên cứu

- Mô hình hóa bài toán phân công công việc dưới dạng CSP với đầy đủ 5 ràng buộc cốt lõi
- Xây dựng thuật toán giải quyết CSP sử dụng Backtracking kết hợp AC-3, Forward Checking, MRV, LCV
- Tối ưu hóa lời giải để thỏa mãn cả ràng buộc cứng và mềm
- Đánh giá hiệu quả của mô hình đề xuất so với phương pháp phân công thủ công

## 🏗️ Kiến trúc hệ thống

### Các thành phần chính:

#### 1. **Biến (Variables)**
- Mỗi tác vụ trong dự án là một biến
- Miền giá trị: cặp {Nhân sự, Thời gian bắt đầu}

#### 2. **Ràng buộc (Constraints)**

**Ràng buộc cứng:**
- **Kỹ năng**: Nhân sự phải có kỹ năng phù hợp với yêu cầu tác vụ
- **Phụ thuộc**: Tác vụ chỉ bắt đầu sau khi các tác vụ tiên quyết hoàn thành
- **Giờ làm việc**: Tác vụ phải thực hiện trong khung giờ 8h-17h
- **Không chồng chéo**: Cùng nhân sự không thực hiện nhiều tác vụ cùng lúc
- **Deadline**: Tác vụ phải hoàn thành trước hạn chót

**Ràng buộc mềm:**
- **Cân bằng tải**: Phân bổ khối lượng công việc đồng đều
- **Độ ưu tiên**: Ưu tiên thực hiện tác vụ quan trọng sớm hơn

#### 3. **Thuật toán giải quyết**

**Mô hình Baseline:**
- Thuật toán Backtracking thuần túy
- Tìm kiếm tuần tự không sử dụng heuristic

**Mô hình Advanced:**
- **Backtracking**: Thuật toán tìm kiếm chính
- **AC-3**: Tiền xử lý để cắt tỉa không gian tìm kiếm
- **Forward Checking**: Phát hiện sớm ngõ cụt
- **MRV (Minimum Remaining Values)**: Chọn biến khó nhất trước
- **LCV (Least Constraining Value)**: Chọn giá trị ít xung đột nhất

## 💻 Công nghệ sử dụng

- **Ngôn ngữ**: Python 3.12.x
- **IDE**: Visual Studio Code
- **Thư viện chính**:
  - `pandas`, `openpyxl`: Xử lý dữ liệu Excel/CSV
  - `tkinter`, `ttk`: Giao diện đồ họa
  - `matplotlib`: Vẽ biểu đồ
  - `datetime`, `collections.deque`: Xử lý thời gian và tối ưu thuật toán

## 🚀 Cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.12.x
- Windows 10/11 64-bit
- RAM: 8GB trở lên

### Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Chạy chương trình
```bash
python gui_app.py
```

### Đóng gói thành file .exe
```bash
pyinstaller --onefile --windowed --icon=icon.ico gui_app.py
```

## 📊 Kết quả thực nghiệm

Thực nghiệm trên bộ dữ liệu **Medium Project** (14 nhân viên, 32 công việc):

| Chỉ số | Baseline | Advanced | Cải thiện |
|--------|----------|----------|-----------|
| Thời gian chạy | 0.0568s | 2.7296s | - |
| % Ràng buộc thỏa mãn | 98.4% | 100% | +1.6% |
| Độ lệch chuẩn Workload | 8.84h | 3.93h | **+55.5%** |
| Makespan | 5.2 ngày | 5.2 ngày | = |

### Hiệu quả kỹ thuật:
- **AC-3**: Cắt tỉa 19.48% không gian tìm kiếm (1267/6504 giá trị)
- **Forward Checking**: Phát hiện sớm 229 xung đột
- **Heuristics**: Giảm đáng kể số lần backtrack

## 🎨 Giao diện người dùng

### Tab Sắp xếp công việc
- Chạy mô hình đơn (Baseline hoặc Advanced)
- Hiển thị kết quả phân công dạng bảng
- Xuất kết quả ra file Excel/CSV

### Tab So sánh hiệu năng
- Chạy song song cả hai mô hình
- Hiển thị biểu đồ so sánh chi tiết
- Thống kê thời gian thực thi và chất lượng lời giải

## 📁 Cấu trúc thư mục

```
├── datasets/              # Bộ dữ liệu đầu vào
├── data_test/            # Dữ liệu kiểm thử
├── baseline/             # Module Baseline (Backtracking thuần)
├── advanced/             # Module Advanced (CSP tối ưu)
├── gui_app.py            # Giao diện chính
├── requirements.txt      # Dependencies
└── README.md            # Tài liệu này
```

## 🔬 Phạm vi áp dụng

- **Quy mô**: 4-10 thành viên, 20-50 tác vụ
- **Lĩnh vực**: Dự án phần mềm quy mô vừa và nhỏ
- **Dữ liệu đầu vào**:
  - Danh sách nhân sự (kỹ năng, thời gian rảnh)
  - Danh sách tác vụ (yêu cầu, deadline, phụ thuộc)

## 🚀 Hướng phát triển

### 1. Cải thiện hiệu năng
- Song song hóa thuật toán AC-3
- Tối ưu hóa cấu trúc dữ liệu
- Lưu cache kết quả tính toán

### 2. Mở rộng ràng buộc
- Ràng buộc về nghỉ ngơi, ngày lễ
- Đa kỹ năng với mức độ thành thạo
- Ưu tiên động dựa trên tiến độ

### 3. Tích hợp Machine Learning
- Dự đoán thời gian hoàn thành thực tế
- Học heuristic từ dữ liệu lịch sử
- Phân tích rủi ro dự án

### 4. Giao diện nâng cao
- Dashboard trực quan theo dõi tiến độ
- Tùy chỉnh ràng buộc động
- Báo cáo tự động chi tiết

## 📚 Tài liệu tham khảo

1. S. J. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Pearson, 2021.
2. G. N. Yannakakis and J. Togelius, *Artificial Intelligence and Games*. Springer, 2018.
3. R. Akerkar, *Artificial Intelligence for Business*. Springer, 2019.
4. A. P. Castaño, *Practical Artificial Intelligence*. Apress, 2018.

---

*Đồ án môn học Trí Tuệ Nhân Tạo - Trường Đại học Công Thương TP.HCM - 2025*
