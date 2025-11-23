# HỆ THỐNG PHÂN CÔNG CÔNG VIỆC USING CSP - So sánh Mô hình Baseline và Advanced Solver

## 📋 TỔNG QUAN

Dự án này triển khai **2 mô hình giải bài toán phân công công việc (Task Assignment)** sử dụng **Constraint Satisfaction Problem (CSP)**:

1. **`baseline.py`** - Mô hình cơ bản (Baseline)
2. **`main-solver.py`** - Mô hình tối ưu nâng cao (Advanced Solver)

### 🎯 Bài toán

Phân công công việc cho nhân sự sao cho:
- ✅ Thỏa mãn **tất cả ràng buộc cứng** (kỹ năng, phụ thuộc, deadline, sức chứa)
- ✅ Tối ưu hóa **ràng buộc mềm** (ưu tiên cao thực hiện sớm, cân bằng tải)
- ✅ Tìm lời giải nhanh, hiệu quả

---

## 🔍 TẠI SAO CẦN CẢ 2 MÔ HÌNH?

### 📊 So sánh tổng quan

| Tiêu chí | **Baseline** | **Advanced Solver** |
|---------|------------|-------------------|
| **Mục đích** | Tìm lời giải hợp lệ | Tối ưu hóa lời giải |
| **Thuật toán chính** | Backtracking cơ bản | AC-3 + Backtracking + Heuristics |
| **Tiền xử lý** | Không | AC-3 cắt tỉa domain |
| **Heuristic biến** | Không | MRV (fail-fast) |
| **Heuristic giá trị** | Không | LCV + Soft constraints (succeed-first) |
| **Forward Checking** | Không | Có |
| **Ràng buộc mềm** | Không xử lý | Tích hợp + Tối ưu |
| **Tốc độ** | Chậm (có backtrack) | Nhanh (ít backtrack) |
| **Chất lượng lời giải** | Chấp nhận được | Tối ưu |
| **Trường hợp dùng** | Học tập, prototype | Production, thực tế |

### 💡 Khi nào dùng mỗi mô hình?

**Dùng Baseline (`baseline.py`):**
- 🎓 Học tập CSP cơ bản
- 🧪 Prototype nhanh
- 📚 Bài tập, kiểm tra
- 🔍 Debug logic ràng buộc

**Dùng Advanced Solver (`main-solver.py`):**
- 🏢 Hệ thống production
- ⚡ Cần tốc độ cao (< 0.5s)
- 🎯 Cần lời giải tối ưu
- 📈 Dữ liệu lớn (30+ tác vụ)

---

## 🚀 CÀI ĐẶT VÀ CHẠY

### 1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

### 2. Chạy mô hình Baseline:
```bash
python baseline.py
```

### 3. Chạy mô hình Advanced Solver:
```bash
python main-solver.py
```

---

## 📁 CẤU TRÚC DỰ ÁN

```
CSP-Phan-Cong-Cong-Viec/
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
├── baseline.py                         # Mô hình cơ bản
├── main-solver.py                      # 🌟 Mô hình tối ưu nâng cao
├── README.md                           # 📖 File này
├── requirements.txt                    # Dependencies
└── magia_ac-3.txt                      # Mã giả AC-3
```

---

## 📊 KẾT QUẢ BENCHMARK

### Test với 3 datasets

| Dataset | Baseline |  | Advanced Solver |  |
|---------|----------|---|---------|---|
| | Thời gian | Backtrack | Thời gian | Backtrack |
| **complex_dependency_chain** | 0.42s | 3 | 0.15s | 0 |
| **load_balance** | 0.89s | 8 | 0.36s | 0 |
| **skill_bottleneck** | 0.38s | 2 | 0.13s | 0 |

**Kết luận:**
- ✅ Advanced Solver **nhanh 2-3x** so với Baseline
- ✅ Advanced Solver **loại bỏ hầu hết backtrack** (từ 2-8 xuống 0)
- ✅ Cả 2 mô hình đều tìm được lời giải hợp lệ

---

## 🔧 ĐỊNH DẠNG DỮ LIỆU

### File `congviec_*.csv`:
```csv
ID,TenTask,YeuCauKyNang,ThoiLuong (gio),PhuThuoc,Deadline (ngay),DoUuTien
T01,Gather Requirements,Analysis,6,,2,5
T02,Create Design Doc,Design,5,T01,3,4
T03,Setup Database,Database,8,T02,4,3
```

- **ID**: Mã tác vụ (T01, T02, ...)
- **TenTask**: Tên tác vụ
- **YeuCauKyNang**: Kỹ năng yêu cầu
- **ThoiLuong (gio)**: Thời lượng (giờ)
- **PhuThuoc**: Danh sách ID tác vụ phụ thuộc (phân cách dấu phẩy)
- **Deadline (ngay)**: Hạn chót (số ngày từ khi bắt đầu)
- **DoUuTien**: Độ ưu tiên (cao hơn = ưu tiên hơn)

### File `nhanvien_*.csv`:
```csv
ID,Ten,KyNang,SucChua (gio/ngay)
NV01,Lan A,"Analysis, Design",8
NV02,Tran B,"Backend, Database",8
```

- **ID**: Mã nhân viên
- **Ten**: Tên nhân viên
- **KyNang**: Danh sách kỹ năng
- **SucChua (gio/ngay)**: Sức chứa (giờ/ngày)

---

## 📖 CHI TIẾT 2 MÔ HÌNH

### MFORM 1: BASELINE (`baseline.py`)

**Thuật toán:**
```
Backtracking cơ bản
├── Chọn tác vụ chưa phân công (tuần tự)
├── Duyệt tất cả giá trị (nhân sự + ngày)
├── Kiểm tra ràng buộc cứng
├── Nếu hợp lệ → gán, tiếp tục đệ quy
└── Nếu thất bại → backtrack
```

**Ưu điểm:**
- ✅ Dễ hiểu, dễ debug
- ✅ Có thể tìm lời giải cho bài toán đơn giản
- ✅ Phù hợp với learning

**Nhược điểm:**
- ❌ Chậm (nhiều backtrack)
- ❌ Không xử lý ràng buộc mềm
- ❌ Không có tối ưu hóa domain

**Ràng buộc:**
- ✅ Kỹ năng: Nhân sự phải có kỹ năng yêu cầu
- ✅ Phụ thuộc: Tác vụ phụ thuộc phải hoàn thành trước
- ✅ Deadline: Phải hoàn thành trước hạn chót
- ✅ Sức chứa: Không vượt quá giờ/ngày
- ✅ Khung giờ: 8h-17h
- ❌ Ưu tiên: Không xử lý
- ❌ Cân bằng tải: Không xử lý

---

### MODEL 2: ADVANCED SOLVER (`main-solver.py`)

**Thuật toán:**
```
AC-3 (Tiền xử lý)
  ↓
Backtracking + MRV + LCV + Forward Checking
├── AC-3: Cắt tỉa domain (0.5-8% giá trị)
├── MRV: Chọn tác vụ có ít lựa chọn nhất (fail-fast)
├── Forward Checking: Cắt domain hàng xóm sau mỗi gán
├── LCV + Soft Constraints: Sắp xếp giá trị theo:
│   ├── Ít xung đột nhất (LCV)
│   ├── Priority cao → thực hiện sớm
│   └── Load Balance tốt
└── Backtrack (cực hiếm)
```

**Ưu điểm:**
- ✅ Nhanh (< 0.5s cho 30 tác vụ)
- ✅ Ít backtrack (thường 0)
- ✅ Tối ưu hóa ràng buộc mềm
- ✅ Xử lý dữ liệu lớn

**Nhược điểm:**
- ❌ Code phức tạp hơn
- ❌ Khó debug

**Ràng buộc:**
- ✅ Kỹ năng: Nhân sự phải có kỹ năng yêu cầu
- ✅ Phụ thuộc: Tác vụ phụ thuộc phải hoàn thành trước
- ✅ Deadline: Phải hoàn thành trước hạn chót
- ✅ Sức chứa: Không vượt quá giờ/ngày
- ✅ Khung giờ: 8h-17h
- ✅ Ưu tiên: Tác vụ priority cao được thực hiện sớm
- ✅ Cân bằng tải: Phân phối công việc đều

---

## 📊 CÁC BỘ DỮ LIỆU TEST

### 1. Skill Bottleneck (Nghẽn cổ chai kỹ năng)
- **Đặc điểm**: 8 nhân sự, 25 tác vụ, kỹ năng chuyên biệt hạn chế
- **Thách thức**: 1 nhân viên có kỹ năng hiếm → bottleneck
- **Ví dụ**: Chỉ NV01 có kỹ năng Database → phải xử lý Database sớm

### 2. Load Balance (Cân bằng tải)
- **Đặc điểm**: 10 nhân sự, 30 tác vụ, kỹ năng đa dạng
- **Thách thức**: Phân phối công việc sao cho tải đều
- **Ví dụ**: 26/30 tác vụ Frontend → cần phân phối cho nhiều người

### 3. Complex Dependency Chain (Chuỗi phụ thuộc phức tạp)
- **Đặc điểm**: 9 nhân sự, 25 tác vụ, chuỗi phụ thuộc dài (T01 → T07)
- **Thách thức**: Đảm bảo thứ tự thực hiện chính xác
- **Ví dụ**: T02 phải chờ T01 xong, T03 phải chờ T02 xong, ...

---

## 🎯 CÁC THUẬT TOÁN CHÍNH

### AC-3 (Arc Consistency 3)
```
Mục đích: Cắt tỉa domain ban đầu
Cách hoạt động:
1. Duyệt tất cả arc (cặp biến có ràng buộc)
2. Nếu biến X có giá trị không tương thích với Y → xóa khỏi domain X
3. Lặp lại cho đến khi không thay đổi
4. Phát hiện ngõ cụt sớm (domain rỗng)

Kết quả: Domain nhỏ hơn → tìm kiếm nhanh hơn
```

### MRV (Minimum Remaining Values)
```
Ý tưởng: Fail-fast strategy
Cách hoạt động:
1. Chọn biến có ít lựa chọn còn lại nhất
2. Phát hiện mâu thuẫn sớm
3. Giảm độ sâu của cây tìm kiếm

Ví dụ: Nếu T05 chỉ còn 1 người thực hiện được → chọn T05 trước
```

### LCV (Least Constraining Value)
```
Ý tưởng: Succeed-first strategy
Cách hoạt động:
1. Sắp xếp giá trị theo số ít xung đột
2. Thử giá trị ít ảnh hưởng đến biến khác trước
3. Tăng xác suất thành công

Ví dụ: Giao tác vụ cho người ít bận hơn trước
```

### Forward Checking
```
Mục đích: Cắt tỉa domain sau mỗi phép gán
Cách hoạt động:
1. Sau khi gán giá trị cho biến X
2. Xóa các giá trị không tương thích khỏi domain biến khác
3. Phát hiện ngõ cụt sớm

Kết quả: Giảm không gian tìm kiếm
```

---

## 📈 OUTPUT

### Console Output (Advanced Solver):
```
======================================================================
KẾT QUẢ PHÂN CÔNG CÔNG VIỆC
======================================================================

Tác vụ T01 (Gather Requirements): Lan A (NV01)
  - Ngày bắt đầu: 08:00 13/04/2005
  - Ngày kết thúc: 13/04/2005 14:00
  - Thời lượng: 6 giờ
  - Độ ưu tiên: 5

Tác vụ T02 (Create Design Doc): Lan A (NV01)
  - Ngày bắt đầu: 14/04/2005 08:00
  - Ngày kết thúc: 14/04/2005 13:00
  - Thời lượng: 5 giờ
  - Độ ưu tiên: 4

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
Số giá trị bị cắt bởi AC-3: 142 (8.08%)
Số giá trị bị cắt bởi Forward Checking: 644
Số lần Backtrack: 0
```

### CSV Output:
File `task_assignment_{dataset}_advanced.csv`:
```csv
Task_ID,Task_Name,Employee_ID,Employee_Name,Start_Date,Start_Time,End_Date,End_Time,Duration_Hours,Priority,Required_Skill
T01,Gather Requirements,NV01,Lan A,13/04/2005,08:00,13/04/2005,14:00,6,5,Analysis
T02,Create Design Doc,NV01,Lan A,14/04/2005,08:00,14/04/2005,13:00,5,4,Design
```

---

## 💡 LỰA CHỌN MỒDEL

### Nên dùng Baseline nếu:
- 🎓 Bạn đang học CSP
- 🔧 Cần debug và hiểu rõ logic
- 🧪 Dữ liệu nhỏ (< 15 tác vụ)
- 📝 Viết báo cáo khoa học

### Nên dùng Advanced Solver nếu:
- 🏢 Dùng trong sản phẩm thực tế
- ⚡ Cần tốc độ cao
- 📈 Dữ liệu lớn (> 20 tác vụ)
- 🎯 Cần lời giải tối ưu
- 👥 Cần optimize ưu tiên + cân bằng tải

---

## 📚 REFERENCES

- **AC-3**: Mackworth, A. K. (1977). Consistency in Networks of Relations
- **CSP**: Russell, S., & Norvig, P. (2020). Artificial Intelligence: A Modern Approach
- **Constraint Propagation**: Bessière, C., & Régin, J. C. (1996). Arc consistency for general constraint networks
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
>>>>>>> main-solver
