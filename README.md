# HỆ THỐNG PHÂN CÔNG CÔNG VIỆC TỐI ƯU - CSP SOLVER

## 📋 TỔNG QUAN

Hệ thống phân công công việc tự động sử dụng **Constraint Satisfaction Problem (CSP)** với các thuật toán tối ưu:

### ✅ Các thuật toán được tích hợp:
- **AC-3 (Arc Consistency 3)**: Tiền xử lý cắt tỉa domain trước khi tìm kiếm
- **Backtracking**: Thuật toán quay lui đệ quy với phát hiện ngõ cụt
- **MRV (Minimum Remaining Values)**: Heuristic chọn biến (fail-fast strategy)
- **LCV (Least Constraining Value)**: Heuristic sắp xếp giá trị (succeed-first strategy)
- **Forward Checking**: Cắt tỉa domain sau mỗi phép gán
- **Soft Constraints Optimization**: Tối ưu hóa Priority + Load Balance

### 🎯 Ràng buộc:
- **Ràng buộc cứng**: Kỹ năng, Phụ thuộc, Lịch làm việc, Deadline, Khung thời gian (8h-17h)
- **Ràng buộc mềm**: Priority (ưu tiên cao thực hiện sớm), Load Balance (cân bằng tải)

---

## 📁 CẤU TRÚC DỰ ÁN

```
CSP-Phan-Cong-Cong-Viec-main-solver/
├── datasets/                           # 3 bộ dữ liệu test
│   ├── complex_dependency_chain/      # Chuỗi phụ thuộc phức tạp
│   │   ├── congviec_dependency.csv
│   │   └── nhanvien_dependency.csv
│   ├── load_balance/                   # Cân bằng tải
│   │   ├── congviec_loadbalance.csv
│   │   └── nhanvien_loadbalance.csv
│   └── skill_bottleneck/               # Nghẽn cổ chai kỹ năng
│       ├── congviec_bottleneck.csv
│       └── nhanvien_bottleneck.csv
│
├── main-solver.py                     # 🌟 File chính - Hệ thống tối ưu
├── README.md                          # 📖 File này
├── magia_ac-3.txt                     # Mã giả AC-3
└── requirements.txt                   # Dependencies
```

---

## 🚀 CÀI ĐẶT VÀ CHẠY

### 1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

### 2. Chạy hệ thống:
```bash
python main-solver.py
```

### 3. Tương tác với chương trình:
```
=== HỆ THỐNG PHÂN CÔNG CÔNG VIỆC SỬ DỤNG CSP - MÔ HÌNH TỐI ƯU ===

Chọn bộ dữ liệu:
1. complex_dependency_chain - Chuỗi phụ thuộc phức tạp
2. load_balance - Cân bằng tải
3. skill_bottleneck - Nghẽn cổ chai kỹ năng

Nhập lựa chọn (1-3): 1

Nhập thông tin dự án:
Ngày bắt đầu dự án (dd/mm/yyyy): 13/04/2005
Ngày kết thúc dự án (dd/mm/yyyy): 23/04/2005
```

### 4. Xem kết quả:
- **Console**: Hiển thị kết quả phân công, đánh giá ràng buộc mềm, thống kê hiệu suất
- **CSV**: File `task_assignment_{dataset}_advanced.csv` chứa bảng phân công chi tiết

---

## 📊 KẾT QUẢ TEST

### Test với 3 datasets:

| Dataset | Tác vụ | Nhân sự | Thời gian | AC-3 cắt | FC cắt | Backtrack | Kết quả |
|---------|--------|---------|-----------|----------|--------|-----------|---------|
| **complex_dependency_chain** | 25 | 9 | 0.15s | 142 (8.08%) | 644 | 0 | ✅ PASS |
| **load_balance** | 30 | 10 | 0.36s | 18 (0.52%) | 1154 | 0 | ✅ PASS |
| **skill_bottleneck** | 25 | 8 | 0.13s | 55 (2.98%) | 450 | 0 | ✅ PASS |

**Tổng kết**: 3/3 datasets thành công (100%), không cần backtrack!

### Điểm nổi bật:
- ✅ **100% datasets thành công** (3/3)
- ✅ **0 backtrack** cho tất cả datasets
- ✅ **< 0.4 giây** thời gian thực thi
- ✅ **AC-3 cắt giảm 0.52%-8.08%** domain
- ✅ **Priority Score > 0.77** (tốt)
- ✅ **Forward Checking hiệu quả**: Cắt 450-1154 giá trị

---

## 🔄 LUỒNG XỬ LÝ TỔNG THỂ

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN()                                    │
│  - Chọn dataset                                             │
│  - Nhập thời gian dự án                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              SOLVE_CSP()                                    │
│  BƯỚC 1: load_data()           → Đọc CSV, tạo TacVu, NhanSu │
│  BƯỚC 2: initialize_domains()  → Tạo miền giá trị ban đầu  │
│  BƯỚC 3: ac3_preprocess()      → Tiền xử lý AC-3           │
│  BƯỚC 4: recursive_backtracking() → Tìm lời giải           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│        DISPLAY_SOLUTION()                                   │
│  - Hiển thị kết quả phân công                              │
│  - Đánh giá ràng buộc mềm                                  │
│  - Thống kê hiệu suất                                      │
└─────────────────────────────────────────────────────────────┘
```

### Chi tiết các bước:

#### BƯỚC 1: LOAD_DATA()
- Đọc file CSV từ thư mục dataset
- Tạo danh sách `TacVu` (tác vụ) và `NhanSu` (nhân sự)
- Xử lý dependencies và skills bằng split(',')

#### BƯỚC 2: INITIALIZE_DOMAINS()
- Tạo miền giá trị ban đầu cho mỗi tác vụ
- Sinh tất cả các `CSPAssignment` hợp lệ (nhân sự + thời gian)
- Kiểm tra ràng buộc: kỹ năng, phụ thuộc, deadline, khung thời gian

#### BƯỚC 3: AC3_PREPROCESS()
- **Mục đích**: Cắt tỉa domain ban đầu trước khi tìm kiếm
- **Cách hoạt động**:
  1. Tạo hàng đợi chứa tất cả các arc (cặp tác vụ có ràng buộc)
  2. Xử lý từng arc: Kiểm tra và cắt tỉa domain
  3. Lan truyền: Nếu domain thay đổi, thêm các arc liên quan vào hàng đợi
  4. Phát hiện ngõ cụt sớm: Nếu domain rỗng → không có lời giải
- **Kết quả**: Domain nhỏ hơn → Backtracking nhanh hơn

#### BƯỚC 4: RECURSIVE_BACKTRACKING()
- **MRV**: Chọn tác vụ có ít lựa chọn nhất (fail-fast)
- **LCV + Soft Constraints**: Sắp xếp giá trị theo:
  * Ít xung đột nhất (LCV)
  * Thỏa mãn ràng buộc mềm tốt nhất (Priority + Load Balance)
- **Forward Checking**: Sau mỗi phép gán, cắt tỉa domain của hàng xóm
- **Backtrack**: Nếu thất bại, quay lui và thử giá trị khác

---

## 🔧 ĐỊNH DẠNG DỮ LIỆU

### File `congviec_*.csv`:
```csv
ID,TenTask,YeuCauKyNang,ThoiLuong (gio),PhuThuoc,Deadline (ngay),DoUuTien
T01,Gather Requirements,Analysis,6,,2,5
T02,Create Design Doc,Design,5,T01,3,4
```

- **ID**: Mã tác vụ (T01, T02, ...)
- **TenTask**: Tên tác vụ
- **YeuCauKyNang**: Kỹ năng yêu cầu (Analysis, Design, Database, Frontend, ...)
- **ThoiLuong (gio)**: Thời lượng (giờ)
- **PhuThuoc**: Danh sách ID tác vụ phụ thuộc (phân cách bởi dấu phẩy, để trống nếu không có)
- **Deadline (ngay)**: Hạn chót (số ngày từ khi dự án bắt đầu)
- **DoUuTien**: Độ ưu tiên (số càng lớn = ưu tiên cao hơn)

### File `nhanvien_*.csv`:
```csv
ID,Ten,KyNang,SucChua (gio/ngay)
NV01,Lan A,"Analysis, Design",8
NV02,Tran B,"Backend, Database",8
```

- **ID**: Mã nhân viên (NV01, NV02, ...)
- **Ten**: Tên nhân viên
- **KyNang**: Danh sách kỹ năng (phân cách bởi dấu phẩy)
- **SucChua (gio/ngay)**: Sức chứa (giờ làm việc/ngày, thường là 8)

---

## 🎨 OUTPUT

### 1. Console Output:
```
======================================================================
KẾT QUẢ PHÂN CÔNG CÔNG VIỆC
======================================================================

Tác vụ T01 (Gather Requirements): Lan A (NV01)
  - Ngày bắt đầu: 08:00 13/04/2005
  - Ngày kết thúc: 14:00 13/04/2005
  - Thời lượng: 6 giờ
  - Độ ưu tiên: 5

...

======================================================================
ĐÁNH GIÁ RÀNG BUỘC MỀM
======================================================================

1. Load Balance Score: 0.0634
   (Điểm càng cao = cân bằng tải càng tốt)

2. Priority Score: 0.7715
   (Điểm càng cao = tác vụ ưu tiên cao được thực hiện sớm hơn)

3. Tổng thể: 0.4175

======================================================================
THỐNG KÊ HIỆU SUẤT
======================================================================
Thời gian thực thi: 0.1515 giây
Số giá trị bị cắt bởi AC-3: 142
Số giá trị bị cắt bởi Forward Checking: 644
Số lần Backtrack: 0
```

### 2. CSV Output:
File `task_assignment_{dataset}_advanced.csv`:
```csv
Task_ID,Task_Name,Employee_ID,Employee_Name,Start_Date,Start_Time,End_Date,End_Time,Duration_Hours,Priority,Required_Skill
T01,Gather Requirements,NV01,Lan A,13/04/2005,08:00,13/04/2005,14:00,6,5,Analysis
T02,Create Design Doc,NV01,Lan A,14/04/2005,08:00,14/04/2005,13:00,5,4,Design
...
```

---

## 🔍 CÁC TÍNH NĂNG CHÍNH

### 1. AC-3 Preprocessing
- Cắt tỉa domain ban đầu trước khi tìm kiếm
- Lan truyền ràng buộc qua nhiều tầng
- Phát hiện ngõ cụt sớm (nếu có)
- **Tuân thủ theo file `magia_ac-3.txt`**

### 2. MRV Heuristic
- Chọn tác vụ có ít lựa chọn nhất (fail-fast strategy)
- Tie-breaking: Nếu có nhiều tác vụ cùng số lựa chọn, ưu tiên tác vụ có priority cao hơn
- Giúp phát hiện ngõ cụt sớm

### 3. LCV Heuristic + Soft Constraints
- Sắp xếp giá trị theo:
  * **LCV**: Ít xung đột nhất (succeed-first strategy)
  * **Load Balance**: Ưu tiên nhân sự có workload gần trung bình
  * **Priority**: Ưu tiên tác vụ quan trọng thực hiện sớm
- Kết hợp với trọng số: 70% LCV + 30% Soft Constraints

### 4. Forward Checking
- Cắt tỉa domain của hàng xóm sau mỗi phép gán
- Phát hiện ngõ cụt ngay lập tức
- Giảm backtrack đáng kể

### 5. Soft Constraints Evaluation
- **Priority Score**: `(priority / max_priority) × (1 - normalized_time)`
  * Tác vụ ưu tiên cao thực hiện sớm → điểm cao
- **Load Balance Score**: `1 / (1 + |new_workload - avg_workload|)`
  * Workload gần trung bình → điểm cao

---

## 🛠️ MỞ RỘNG VÀ TÙY CHỈNH

### Điều chỉnh trọng số trong LCV + Soft Constraints:
Trong file `main-solver.py`, tìm hàm `order_domain_values_with_lcv()`:

```python
# Trọng số LCV vs Soft Constraints
LCV_WEIGHT = 0.7      # Độ quan trọng của LCV (ít xung đột)
SOFT_WEIGHT = 0.3     # Độ quan trọng của ràng buộc mềm

# Trọng số trong Soft Constraints
LOAD_BALANCE_WEIGHT = 0.4  # Độ quan trọng của Load Balance
PRIORITY_WEIGHT = 0.6      # Độ quan trọng của Priority
```

**Hướng dẫn điều chỉnh**:
- Tăng `LOAD_BALANCE_WEIGHT` nếu muốn cân bằng tải tốt hơn
- Tăng `PRIORITY_WEIGHT` nếu muốn ưu tiên tác vụ quan trọng
- Tăng `LCV_WEIGHT` nếu muốn giảm xung đột (ít backtrack hơn)

### Thêm ràng buộc mới:
1. **Ràng buộc cứng**: Thêm vào hàm `is_consistent()` và `check_conflict_between_assignments()`
2. **Ràng buộc mềm**: Thêm vào hàm `evaluate_soft_constraints()`

---

## ⚠️ HẠN CHẾ VÀ HƯỚNG CẢI THIỆN

### Hạn chế hiện tại:
1. **Load Balance chưa tối ưu**: Một số nhân sự bị quá tải (40 giờ), một số không được gán
2. **Trọng số cố định**: Chưa tự động điều chỉnh theo đặc điểm dataset
3. **Giờ làm việc cứng nhắc**: 8h-17h, không linh hoạt
4. **Không có giới hạn workload**: Nhân sự có thể bị gán > 8 giờ/ngày

### Hướng cải thiện:
1. Thêm ràng buộc workload: Giới hạn số giờ làm việc/ngày, /tuần
2. Điều chỉnh trọng số động: Tùy theo đặc điểm dataset (phụ thuộc/load_balance/bottleneck)
3. Tối ưu hóa toàn cục: Sử dụng Branch & Bound hoặc thuật toán di truyền
4. Xử lý giờ làm linh hoạt: Ca sáng, ca chiều, overtime
5. Thêm ràng buộc mềm khác: Chi phí, kỹ năng yêu cầu mềm, deadline mềm

---

## 📝 VÍ DỤ MINH HỌA

### Dataset: complex_dependency_chain
**Đặc điểm**: Chuỗi phụ thuộc dài T01→T02→...→T07, 25 tác vụ, 9 nhân sự

**Quá trình xử lý**:
1. **Initialize Domains**: 1757 giá trị ban đầu
2. **AC-3 Preprocessing**: Cắt giảm 142 giá trị (8.08%) → 1615 giá trị
3. **Backtracking**: 
   - MRV chọn T01 (ưu tiên cao, không phụ thuộc)
   - LCV + Soft Constraints chọn assignment tốt nhất
   - Forward Checking cắt tỉa domain của T02, T08-T25
   - Tiếp tục với các tác vụ khác
4. **Kết quả**: Tìm thấy lời giải trong 0.15s, 0 backtrack!

**Phân bố công việc**:
- Le C (NV03): 39 giờ (9 tác vụ)
- Ho H (NV08): 40 giờ (10 tác vụ)
- Lan A (NV01): 11 giờ (2 tác vụ)
- Bui F (NV06): 0 giờ (không được gán)

**Đánh giá**:
- Priority Score: 0.7715 (tốt - tác vụ ưu tiên cao được ưu tiên)
- Load Balance Score: 0.0634 (cần cải thiện - chưa cân bằng)

---

## 🎯 TÍNH NĂNG NỔI BẬT

File `main-solver.py` tích hợp đầy đủ các thuật toán tối ưu:
- ✅ **AC-3 Preprocessing**: Cắt tỉa domain ban đầu
- ✅ **MRV Heuristic**: Chọn biến thông minh (+ tie-breaking)
- ✅ **LCV + Soft Constraints**: Sắp xếp giá trị tối ưu
- ✅ **Forward Checking**: Phát hiện ngõ cụt sớm
- ✅ **Soft Constraints**: Priority + Load Balance
- ✅ **Hiệu suất cao**: 0 backtrack, < 0.4 giây

---

## ❓ VẤN ĐỀ THƯỜNG GẶP

**Q: Chương trình báo "Không tìm thấy giải pháp"?**
- A: Kiểm tra deadline quá chặt, hoặc kỹ năng không khớp. Tăng thời gian dự án hoặc giảm deadline.

**Q: Load Balance Score thấp?**
- A: Tăng `LOAD_BALANCE_WEIGHT` trong hàm `evaluate_soft_constraints()`.

**Q: Thời gian chạy quá lâu?**
- A: Giảm khoảng thời gian dự án, hoặc giảm số tác vụ.

**Q: AC-3 phát hiện ngõ cụt?**
- A: Bài toán không có lời giải. Kiểm tra lại ràng buộc (deadline, kỹ năng, phụ thuộc).

---

## 📝 CHANGELOG

### Version 2.0 (Advanced) - 2025-11-12
- ✅ Thêm AC-3 Preprocessing (tuân thủ theo `magia_ac-3.txt`)
- ✅ Thêm Soft Constraints Optimization (Priority + Load Balance)
- ✅ Cải thiện MRV với tie-breaking theo priority
- ✅ Cải thiện LCV với kết hợp soft constraints
- ✅ Thêm thống kê hiệu suất chi tiết
- ✅ Test thành công 100% datasets (3/3)

### Version 1.0 (Baseline) - 2025
- Backtracking + MRV + LCV + Forward Checking

---

## 📜 LICENSE

Dự án này được phát triển cho mục đích học tập và nghiên cứu.

---

**Phát triển bởi**: Nhóm CSP-TTNT  
**Ngày cập nhật**: 12/11/2025
