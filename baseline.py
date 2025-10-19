# Mô hình CSP cơ bản cho bài toán Phân công công việc

# Định nghĩa lớp cho Nhân sự và Tác vụ
class NhanSu:
    def __init__(self, ten, ky_nang, gioi_han_gio_lam):
        self.ten = ten
        self.ky_nang = ky_nang          
        self.gioi_han_gio_lam = gioi_han_gio_lam  

class TacVu:
    def __init__(self, ten, yeu_cau_ky_nang, thoi_luong, dieu_kien_truoc=None):
        self.ten = ten
        self.yeu_cau_ky_nang = yeu_cau_ky_nang
        self.thoi_luong = thoi_luong
        self.dieu_kien_truoc = dieu_kien_truoc or [] 

# Hàm kiểm tra ràng buộc cứng (is_consistent)
def is_consistent(tac_vu, gia_tri, assignment, csp):
    nhan_su, thoi_gian_bat_dau = gia_tri
    
    # 1. Kiểm tra kỹ năng: Nhân sự phải có kỹ năng yêu cầu của tác vụ
    if tac_vu.yeu_cau_ky_nang not in nhan_su.ky_nang:
        return False
    
    # 2. Kiểm tra điều kiện tiên quyết: Các tác vụ trước phải hoàn thành trước khi bắt đầu tác vụ này
    for tv_truoc in tac_vu.dieu_kien_truoc:
        if tv_truoc in assignment:
            thoi_gian_ket_thuc_truoc = assignment[tv_truoc][1] + tv_truoc.thoi_luong
            if thoi_gian_bat_dau < thoi_gian_ket_thuc_truoc:
                return False
        else:
            return False

    # 3. Kiểm tra ràng buộc sức chứa: Tổng giờ làm việc trong ngày không vượt quá giới hạn của nhân sự
    ngay_lam_viec = thoi_gian_bat_dau // 24  
    tong_gio = tac_vu.thoi_luong
    for t_vu, g_tri in assignment.items():
        if g_tri[0] == nhan_su and (g_tri[1] // 24) == ngay_lam_viec:
            tong_gio += t_vu.thoi_luong
    if tong_gio > nhan_su.gioi_han_gio_lam:
        return False
    
    # 4. Kiểm tra deadline: Thời gian kết thúc tác vụ không vượt quá deadline của dự án
    thoi_gian_ket_thuc = thoi_gian_bat_dau + tac_vu.thoi_luong
    if thoi_gian_ket_thuc > csp["deadline"]:
        return False
    return True

# ======================
# Thuật toán Backtracking cơ bản
# ======================
def recursive_backtracking(assignment, csp):
    tasks = csp["tasks"]

    # Nếu đã gán hết
    if len(assignment) == len(tasks):
        return assignment

    # Chọn biến chưa gán
    for tac_vu in tasks:
        if tac_vu not in assignment:
            break

    # Lặp qua các giá trị trong miền
    for value in csp["domains"][tac_vu]:
        if is_consistent(tac_vu, value, assignment, csp):
            assignment[tac_vu] = value
            result = recursive_backtracking(assignment, csp)
            if result is not None:
                return result
            del assignment[tac_vu] 

    return None

def backtracking_search_baseline(csp):
    return recursive_backtracking({}, csp)

# ======================
# Ví dụ dữ liệu đầu vào
# ======================
if __name__ == "__main__":
    # Tạo nhân sự
    devA = NhanSu("Dev A", ["API", "DB"], 8)
    devB = NhanSu("Dev B", ["UI", "API"], 8)

    # Tạo tác vụ
    T1 = TacVu("Thiết kế CSDL", "DB", 4)
    T2 = TacVu("Xây dựng API", "API", 4, [T1])
    T3 = TacVu("Thiết kế Giao diện", "UI", 4)

    # CSP components
    csp = {
        "tasks": [T1, T2, T3],
        "deadline": 24 * 2,  
        "domains": {
            T1: [(devA, 0), (devB, 0)],     
            T2: [(devA, 4), (devB, 4)],      
            T3: [(devA, 24), (devB, 24)]     
        }
    }
    solution = backtracking_search_baseline(csp)

    if solution:
        print("=== Kết quả phân công hợp lệ ===")
        for t, (nhan_su, tgbd) in solution.items():
            print(f"{t.ten}: {nhan_su.ten} bắt đầu lúc {tgbd}h")
    else:
        print("Không tìm thấy lời giải hợp lệ.")
