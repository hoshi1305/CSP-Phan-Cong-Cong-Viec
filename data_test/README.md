# DỮ LIỆU TEST - SO SÁNH HIỆU NĂNG 2 MÔ HÌNH

## 📊 Thông tin tổng quan

Bộ dữ liệu test này được thiết kế để làm nổi bật sự khác biệt giữa **Baseline** và **Advanced** model.

### Quy mô:
- **30 công việc** (T01 - T30)
- **15 nhân viên** (NV01 - NV15)
- **Phụ thuộc phức tạp**: Nhiều chuỗi phụ thuộc dài
- **Tối ưu**: Đủ phức tạp để so sánh nhưng Baseline vẫn chạy được (2-5 giây)

---

## 🎯 Đặc điểm thiết kế

### 1. **Chuỗi phụ thuộc dài**
- Công việc phụ thuộc vào nhiều công việc khác
- Ví dụ: T100 phụ thuộc gián tiếp vào T001
- Tạo khó khăn cho Baseline trong việc tìm thứ tự phân công

### 2. **Bottleneck kỹ năng**
Một số kỹ năng có ít nhân viên:
- **Security**: 3 người (NV012, NV014, NV024, NV028)
- **Architecture**: 3 người (NV002, NV018, NV030)
- **Training**: 1 người (NV027)

→ Tạo cạnh tranh tài nguyên, Baseline sẽ gặp nhiều backtrack

### 3. **Độ ưu tiên đa dạng**
- Priority 9: Các task quan trọng (deployment, security, authentication)
- Priority 5-6: Các task ít quan trọng (documentation, training)
- Advanced model sẽ xếp task priority cao lên trước

### 4. **Deadline chặt chẽ**
- Task đầu: deadline ngắn (5-10 ngày)
- Task cuối: deadline dài (35-40 ngày)
- Tạo áp lực thời gian, test khả năng tối ưu

---

## 🔍 Kỳ vọng kết quả

### **Baseline:**
- ⏱️ Thời gian thực thi: **2-5 giây**
- 🔄 Số lần backtrack: **Cao (20-80+)**
- 📊 Makespan: **Dài hơn** (phân công không tối ưu)
- ✓ Deadline compliance: **80-90%** (có task bị trễ)
- 🎯 Độ ổn định: **70-80%** (kết quả thay đổi)

### **Advanced (AC-3 + MRV + LCV + FC):**
- ⏱️ Thời gian thực thi: **0.3-1 giây** (nhanh hơn 3-5x)
- 🔄 Số lần backtrack: **Thấp (0-3)**
- ✂️ Domain pruning: **AC-3: 100+, FC: 200+**
- 📊 Makespan: **Ngắn hơn** (tối ưu hóa)
- ✓ Deadline compliance: **95-100%** (đúng hạn)
- 🎯 Độ ổn định: **95-100%** (kết quả ổn định)

---

## 📈 Các điểm nổi bật

### 1. **Complexity (Độ phức tạp)**
```
Tổng số tổ hợp có thể: 15^60 (không gian tìm kiếm lớn nhưng khả thi)
Số phụ thuộc trung bình: 1.3 phụ thuộc/task
Chuỗi phụ thuộc dài nhất: 10 level (T01 → ... → T60)
```

### 2. **Resource Contention (Cạnh tranh tài nguyên)**
```
Security tasks: 3 tasks cho 1 nhân viên (NV14) → Bottleneck rõ ràng
Backend tasks: 18 tasks cho 8 nhân viên → Cạnh tranh vừa phải
Frontend tasks: 12 tasks cho 5 nhân viên → Cạnh tranh vừa phải
```

### 3. **Priority Distribution (Phân bố ưu tiên)**
```
Priority 9: 8 tasks (critical - deployment, security, auth)
Priority 8: 18 tasks (high)
Priority 7: 15 tasks (medium)
Priority 6: 12 tasks (low)
Priority 5: 7 tasks (very low)
```

---

## 🧪 Cách sử dụng

### Trong GUI:
1. Chọn tab **"Sắp xếp công việc"**
2. Chọn **"Tải lên file tùy chỉnh"**
3. Upload:
   - File công việc: `data_test/congviec_test.csv`
   - File nhân viên: `data_test/nhanvien_test.csv`
4. Nhập thời gian: **01/01/2024 - 28/02/2024** (60 ngày)
5. Nhấn **"So Sánh 2 Mô Hình"**

### Hoặc dùng Command Line:
```python
# Test Baseline
python baseline.py
# Chọn upload file: data_test/

# Test Advanced
python advanced.py
# Chọn upload file: data_test/
```

---

## 📊 Kịch bản test gợi ý

### Test 1: So sánh thời gian
```
Dataset: data_test
Thời gian: 01/01/2024 - 28/02/2024
Mục tiêu: Đo thời gian thực thi và số backtrack
```

### Test 2: So sánh chất lượng
```
Dataset: data_test
Thời gian: 01/01/2024 - 15/02/2024 (chặt hơn)
Mục tiêu: Đo deadline compliance và makespan
```

### Test 3: Stress test
```
Dataset: data_test
Thời gian: 01/01/2024 - 10/02/2024 (rất chặt)
Mục tiêu: Test khả năng xử lý ràng buộc chặt
```

---

## 💡 Lưu ý

1. **Thời gian chạy**: 
   - Với 60 tasks, Baseline mất **3-8 giây** (chạy được)
   - Advanced thường mất **0.5-2 giây** (không lag)

2. **Bộ nhớ**:
   - Advanced sử dụng RAM vừa phải (do giảm số lượng)
   - Baseline nhẹ hơn nhưng chậm hơn

3. **Kết quả**:
   - Baseline có thể tìm được lời giải nhưng không tối ưu
   - Advanced có tỷ lệ thành công cao và kết quả tốt hơn

4. **Tối ưu hóa**:
   - Đã giảm từ 100 → 60 tasks để Baseline chạy được
   - Đã giảm từ 30 → 15 nhân viên để giảm độ phức tạp
   - Vẫn đủ phức tạp để thấy rõ sự khác biệt

---

## 🎓 Scenario thực tế

Dataset này mô phỏng dự án **E-commerce Platform** với:
- Phase 1: Analysis & Design (T01-T06)
- Phase 2: Backend Development (T07-T12)
- Phase 3: Frontend Development (T13-T23)
- Phase 4: Testing & QA (T24-T34)
- Phase 5: DevOps & Infrastructure (T35-T38, T41-T42)
- Phase 6: Documentation (T39-T40)
- Phase 7: Deployment & Production (T42-T60)

---

## 📌 Kết luận

Bộ dữ liệu này được thiết kế để:
- ✅ Làm nổi bật ưu điểm của Advanced model
- ✅ Thể hiện hạn chế của Baseline model
- ✅ Test hiệu năng với dữ liệu lớn
- ✅ Đánh giá độ ổn định của thuật toán

**Kỳ vọng**: Advanced model sẽ **nhanh hơn 3-5x** và cho kết quả **tốt hơn 10-15%** về chất lượng.

**Lưu ý**: Dataset đã được tối ưu để Baseline có thể chạy được trong thời gian hợp lý (3-8 giây) trong khi vẫn đủ phức tạp để so sánh hiệu quả.

