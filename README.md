# CSP-Phan-Cong-Cong-Viec - Baseline Model

## 1. Mô tả

Dự án này triển khai mô hình CSP baseline sử dụng thuật toán Backtracking để giải quyết bài toán phân công công việc. Mô hình tập trung vào việc tìm lời giải thỏa mãn **các ràng buộc cứng** (kỹ năng, phụ thuộc, sức chứa, deadline) từ các bộ dữ liệu được cung cấp. **Độ ưu tiên là ràng buộc mềm và không được xử lý trong mô hình baseline này.**

## 2. Cách sử dụng Datasets với Mô hình Baseline

### Cấu trúc Datasets

Datasets được tổ chức trong thư mục `datasets/` với 3 bộ dữ liệu chính:

```
datasets/
├── skill_bottleneck/          # Bộ dữ liệu nghẽn cổ chai
│   ├── congviec_bottleneck.csv
│   └── nhanvien_bottleneck.csv
├── load_balance/              # Bộ dữ liệu cân bằng tải
│   ├── congviec_loadbalance.csv
│   └── nhanvien_loadbalance.csv
└── complex_dependency_chain/  # Bộ dữ liệu phụ thuộc phức tạp
    ├── congviec_dependency.csv
    └── nhanvien_dependency.csv
```

### Chạy với Dataset cụ thể

Trong file `baseline.py`, chỉnh sửa biến `dataset` để chọn bộ dữ liệu:

```python
# Chọn bộ dữ liệu: "skill_bottleneck", "load_balance", "complex_dependency_chain"
dataset = "skill_bottleneck"  # Thay đổi ở đây
```

Sau đó chạy:

```bash
python baseline.py
```

### Định dạng File CSV

- **nhanvien_*.csv**: Chứa thông tin nhân sự
  - `Ten`: Tên nhân viên
  - `KyNang`: Danh sách kỹ năng (phân cách bởi dấu phẩy)
  - `SucChua (gio/ngay)`: Giới hạn giờ làm việc/ngày

- **congviec_*.csv**: Chứa thông tin tác vụ
  - `ID`: Mã tác vụ (T01, T02, ...)
  - `TenTask`: Tên tác vụ
  - `YeuCauKyNang`: Kỹ năng yêu cầu
  - `ThoiLuong (gio)`: Thời lượng thực hiện
  - `PhuThuoc`: Danh sách ID tác vụ phụ thuộc (phân cách bởi dấu phẩy)
  - `DoUuTien`: Độ ưu tiên của tác vụ (số nguyên, cao hơn = ưu tiên hơn)

## 3. Ứng dụng trên các bộ dữ liệu

### 3.1. Bộ dữ liệu Bottleneck

- **Đặc điểm**: Số lượng nhân sự ít (8 người), nhiều tác vụ yêu cầu kỹ năng chuyên biệt (như Database chỉ có Nguyen A thực hiện được), dễ dẫn đến tình trạng nghẽn cổ chai.
- **Biến**: 25 tác vụ (T01 đến T25).
- **Miền giá trị**:
  - Nhân sự: NV01 (Nguyen A), NV02 (Tran B), ..., NV08 (Ho H).
  - Thời gian bắt đầu: Từ ngày 1 đến ngày 10 (dựa trên deadline tối đa).
- **Ràng buộc**:
  - Kỹ năng: Ví dụ, T01 đến T05 yêu cầu Database, chỉ NV01 (Nguyen A) có thể thực hiện.
  - Phụ thuộc: T01 → T02 → T03 → T04 → T05 (chuỗi phụ thuộc).
  - Sức chứa: Mỗi nhân viên làm tối đa 8 giờ/ngày.
  - Deadline: T01 (ngày 2), T05 (ngày 10), v.v.
  - Độ ưu tiên: Mềm, một số tác vụ Database có độ ưu tiên cao (ví dụ T01 = 5), cần được xử lý sớm.
  - Cân bằng tải: Mềm, ưu tiên phân phối công việc đều hơn.

### 3.2. Bộ dữ liệu Loadbalance

- **Đặc điểm**: Nhiều nhân sự có kỹ năng đa dạng (10 người), nhiều tác vụ Frontend (26/30 tác vụ), tập trung vào cân bằng tải.
- **Biến**: 30 tác vụ (T01 đến T30).
- **Miền giá trị**:
  - Nhân sự: NV01 (Anh K), NV02 (Binh L), ..., NV10 (Minh T).
  - Thời gian bắt đầu: Từ ngày 1 đến ngày 7 (dựa trên deadline tối đa).
- **Ràng buộc**:
  - Kỹ năng: T01, T06-T30 yêu cầu Frontend; T02, T03 yêu cầu Backend, Testing.
  - Phụ thuộc: T02 → T03.
  - Sức chứa: 8 giờ/ngày cho mỗi nhân viên.
  - Deadline: T01 (ngày 3), T30 (ngày 7), v.v.
  - Độ ưu tiên: Mềm, tác vụ Frontend có độ ưu tiên cao hơn (ví dụ T01 = 4), cần ưu tiên giao cho nhân sự Frontend.
  - Cân bằng tải: Mềm, ưu tiên phân phối đều công việc.

### 3.3. Bộ dữ liệu Dependency

- **Đặc điểm**: Nhấn mạnh vào chuỗi phụ thuộc dài (T01 → T07).
- **Biến**: 25 tác vụ (T01 đến T25).
- **Miền giá trị**:
  - Nhân sự: NV01 (Lan A), NV02 (Tran B), ..., NV09 (Vu I).
  - Thời gian bắt đầu: Từ ngày 1 đến ngày 9 (dựa trên deadline tối đa).
- **Ràng buộc**:
  - Kỹ năng: T01 (Analysis), T02 (Design), T03 (Database), v.v.
  - Phụ thuộc: T01 → T02 → T03 → T04 → T05 → T06 → T07.
  - Sức chứa: 8 giờ/ngày cho mỗi nhân viên.
  - Deadline: T01 (ngày 2), T07 (ngày 9), v.v.
  - Độ ưu tiên: Mềm, tác vụ đầu chuỗi (T01) có độ ưu tiên cao nhất (ví dụ 5), giảm dần theo chuỗi.
  - Cân bằng tải: Mềm.

## 4. Lưu ý khi áp dụng mô hình

- **Bottleneck**: Thuật toán cần ưu tiên xử lý các tác vụ Database sớm (do chỉ có 1 nhân viên thực hiện), có thể gây chậm trễ nếu không sắp xếp hợp lý.
- **Loadbalance**: Với nhiều tác vụ Frontend và nhân sự có kỹ năng Frontend, thuật toán cần tập trung vào tối ưu hóa cân bằng tải để phân phối công việc đều.
- **Dependency**: Chuỗi phụ thuộc dài yêu cầu thuật toán phải đảm bảo thứ tự thực hiện chính xác, tránh vi phạm ràng buộc phụ thuộc.

Mô hình baseline sử dụng Backtracking có thể tìm lời giải hợp lệ, nhưng để cải thiện hiệu suất, các kỹ thuật như suy diễn ràng buộc (constraint propagation), heuristic chọn biến (MRV - Minimum Remaining Values), hoặc tối ưu hóa cân bằng tải có thể được áp dụng trong các phương pháp nâng cao.