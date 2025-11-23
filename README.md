# HỆ THỐNG PHÂN CÔNG CÔNG VIỆC USING CSP

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

| Tiêu chí | **Baseline** | **Mô hình Chính** |
|---------|------------|-------------------|
| **Mục đích** | Tìm lời giải hợp lệ | Tối ưu hóa lời giải |
| **Thuật toán chính** | Backtracking cơ bản | AC-3 + Backtracking + Heuristics |
| **Tiền xử lý** | Không | AC-3 cắt tỉa domain |
| **Heuristic biến** | Không | MRV (fail-fast) |
| **Heuristic giá trị** | Không | LCV + Soft constraints (succeed-first) |
| **Forward Checking** | Không | Có |
| **Ràng buộc mềm** | Không xử lý | Tích hợp + Tối ưu |
| **Trường hợp dùng** | Học tập, prototype | Production, thực tế |

### 💡 Khi nào dùng mỗi mô hình?

**Dùng Baseline (`baseline.py`):**
- 🎓 Học tập CSP cơ bản
- 🧪 Prototype nhanh
- 📚 Bài tập, kiểm tra
- 🔍 Debug logic ràng buộc

**Dùng Mô hình Chính (`main-solver.py`):**
- 🏢 Hệ thống production
- ⚡ Cần tốc độ cao
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

### MODEL 2: MÔ HÌNH CHÍNH (`main-solver.py`)

**Thuật toán:**
```
AC-3 (Tiền xử lý)
  ↓
Backtracking + MRV + LCV + Forward Checking
├── AC-3: Cắt tỉa domain
├── MRV: Chọn tác vụ có ít lựa chọn nhất (fail-fast)
├── Forward Checking: Cắt domain hàng xóm sau mỗi gán
├── LCV + Soft Constraints: Sắp xếp giá trị theo:
│   ├── Ít xung đột nhất (LCV)
│   ├── Priority cao → thực hiện sớm
│   └── Load Balance tốt
└── Backtrack (cực hiếm)
```

**Ưu điểm:**
- ✅ Nhanh
- ✅ Ít backtrack
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

## 🔧 ĐỊNH DẠNG DỮ LIỆU

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

### Console Output (Mô hình Chính):
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

## 💡 LỰA CHỌN MÔ HÌNH

### Nên dùng Baseline nếu:
- 🎓 Bạn đang học CSP
- 🔧 Cần debug và hiểu rõ logic
- 🧪 Dữ liệu nhỏ (< 15 tác vụ)
- 📝 Viết báo cáo khoa học

### Nên dùng Mô hình Chính nếu:
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
