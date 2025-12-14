# Mô hình tối ưu: Backtracking + MRV + LCV + Forward Checking + AC-3 + Soft Constraints
import csv
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Set
import os
import sys
from collections import deque

# Thiết lập mã hóa UTF-8 cho đầu ra (tránh lỗi font trên Windows)
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

class TacVu:
    def __init__(self, task_id: str, name: str, required_skill: str, duration: int, 
                 dependencies: List[str], deadline: int, priority: int):
        self.id = task_id
        self.name = name
        self.required_skill = required_skill
        self.duration = duration  # thời lượng (giờ)
        self.dependencies = dependencies if dependencies else []
        self.deadline = deadline  # hạn chót (số ngày kể từ khi dự án bắt đầu)
        self.priority = priority  # số càng lớn = độ ưu tiên càng cao

class NhanSu:
    def __init__(self, emp_id: str, name: str, skills: List[str], daily_capacity: int):
        self.id = emp_id
        self.name = name
        self.skills = skills
        self.daily_capacity = daily_capacity  # số giờ làm việc mỗi ngày
        self.work_schedule = []  # danh sách (thời gian bắt đầu, kết thúc) cho các tác vụ được gán

class CSPAssignment:
    def __init__(self, nhansu: NhanSu, start_time: datetime):
        self.nhansu = nhansu
        self.start_time = start_time
        self.end_time = None  # sẽ được tính khi biết thời lượng tác vụ

class CSP:
    def __init__(self, cac_tacvu: List[TacVu], cac_nhansu: List[NhanSu], 
                 project_start_date: datetime, project_end_date: datetime):
        self.cac_tacvu = cac_tacvu
        self.cac_nhansu = cac_nhansu
        self.project_start_date = project_start_date
        self.project_end_date = project_end_date
        self.assignment: Dict[str, CSPAssignment] = {}  # ánh xạ task_id -> CSPAssignment
        self.solution_found = False
        # domains: task_id -> list of possible CSPAssignment
        self.domains: Dict[str, List[CSPAssignment]] = {}
        # Thống kê để đánh giá
        self.ac3_pruned_count = 0  # Số giá trị bị cắt bởi AC-3
        self.fc_pruned_count = 0   # Số giá trị bị cắt bởi Forward Checking
        self.backtrack_count = 0    # Số lần backtrack
        # Pre-compute neighbor map để tránh tính lại nhiều lần
        self.neighbor_map: Dict[str, List[TacVu]] = self._build_neighbor_map()
    
    def _build_neighbor_map(self) -> Dict[str, List[TacVu]]:
        """Xây dựng bản đồ hàng xóm một lần duy nhất khi khởi tạo CSP"""
        neighbor_map = {}
        for tacvu in self.cac_tacvu:
            neighbors = set()
            
            # 1. Tác vụ phụ thuộc VÀO tacvu
            for other_task in self.cac_tacvu:
                if tacvu.id in other_task.dependencies:
                    neighbors.add(other_task)
            
            # 2. Tác vụ mà tacvu phụ thuộc VÀO
            for dep_id in tacvu.dependencies:
                dep_task = next((t for t in self.cac_tacvu if t.id == dep_id), None)
                if dep_task:
                    neighbors.add(dep_task)
            
            # 3. Tác vụ cùng kỹ năng yêu cầu (cạnh tranh nhân sự)
            for other_task in self.cac_tacvu:
                if (other_task.required_skill == tacvu.required_skill and 
                    other_task.id != tacvu.id and 
                    other_task.required_skill):  # Chỉ xét nếu có yêu cầu kỹ năng
                    neighbors.add(other_task)
            
            neighbor_map[tacvu.id] = list(neighbors)
        
        return neighbor_map

def load_data(dataset_folder: str) -> Tuple[List[TacVu], List[NhanSu]]:
    """Tải dữ liệu tác vụ và nhân sự từ các tệp CSV trong thư mục chỉ định"""
    # Xác định tên file phù hợp dựa theo thư mục dữ liệu
    if "small_project" in dataset_folder or "medium_project" in dataset_folder or "large_project" in dataset_folder or "uploaded_temp" in dataset_folder:
        # Bộ dữ liệu: small, medium, large project hoặc uploaded
        tasks_file = os.path.join(dataset_folder, "congviec.csv")
        employees_file = os.path.join(dataset_folder, "nhanvien.csv")
    else:
        raise ValueError(f"Không nhận dạng được thư mục dữ liệu: {dataset_folder}")
    
    # Đọc danh sách các tác vụ
    cac_tacvu = []
    with open(tasks_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'ID' in row and row['ID'].strip():  # bỏ qua dòng trống
                dependencies = []
                if 'PhuThuoc' in row and row['PhuThuoc'].strip():
                    dependencies = [dep.strip() for dep in row['PhuThuoc'].split(',')]
                
                tacvu = TacVu(
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
            if 'ID' in row and row['ID'].strip():  # bỏ qua dòng trống
                skills = [skill.strip() for skill in row.get('KyNang','').split(',') if skill.strip()]
                nhansu = NhanSu(
                    emp_id=row['ID'].strip(),
                    name=row.get('Ten','').strip(),
                    skills=skills,
                    daily_capacity=int(row.get('SucChua (gio/ngay)', '8'))
                )
                cac_nhansu.append(nhansu)
    
    return cac_tacvu, cac_nhansu

def is_consistent(tacvu: TacVu, assignment: CSPAssignment, csp: CSP) -> bool:
    """Kiểm tra xem việc gán tác vụ cho nhân sự tại thời điểm này có hợp lệ (thỏa mãn ràng buộc) không"""
    # 1. Ràng buộc kỹ năng
    if tacvu.required_skill and tacvu.required_skill not in assignment.nhansu.skills:
        return False
    
    # 2. Ràng buộc phụ thuộc giữa các tác vụ
    for dep_task_id in tacvu.dependencies:
        if dep_task_id in csp.assignment:
            dep_assignment = csp.assignment[dep_task_id]
            dep_task = next(t for t in csp.cac_tacvu if t.id == dep_task_id)
            dep_end_time = dep_assignment.start_time + timedelta(hours=dep_task.duration)
            if assignment.start_time < dep_end_time:
                return False
    
    # 3. Ràng buộc lịch làm việc (không được trùng thời gian)
    task_end_time = assignment.start_time + timedelta(hours=tacvu.duration)
    
    for assigned_task_id, assigned_assignment in csp.assignment.items():
        if assigned_assignment.nhansu.id == assignment.nhansu.id:
            assigned_task = next(t for t in csp.cac_tacvu if t.id == assigned_task_id)
            assigned_end_time = assigned_assignment.start_time + timedelta(hours=assigned_task.duration)
            if (assignment.start_time < assigned_end_time and 
                task_end_time > assigned_assignment.start_time):
                return False
    
    # 4. Ràng buộc hạn chót của tác vụ
    project_deadline = csp.project_start_date + timedelta(days=tacvu.deadline)
    if task_end_time > project_deadline:
        return False
    
    # 5. Ràng buộc trong khung thời gian dự án
    if assignment.start_time < csp.project_start_date or task_end_time > csp.project_end_date:
        return False
    
    return True

def get_domain_values(tacvu: TacVu, csp: CSP) -> List[CSPAssignment]:
    """Lấy tất cả các phương án gán hợp lệ cho một tác vụ (dựa trên trạng thái csp hiện tại)"""
    domain = []
    
    # Tìm nhân sự có kỹ năng phù hợp
    suitable_employees = [emp for emp in csp.cac_nhansu 
                         if (not tacvu.required_skill) or tacvu.required_skill in emp.skills]
    
    if not suitable_employees:
        return domain
    
    # Tính thời gian bắt đầu sớm nhất dựa theo các phụ thuộc
    earliest_start = csp.project_start_date
    for dep_task_id in tacvu.dependencies:
        if dep_task_id in csp.assignment:
            dep_assignment = csp.assignment[dep_task_id]
            dep_task = next(t for t in csp.cac_tacvu if t.id == dep_task_id)
            dep_end_time = dep_assignment.start_time + timedelta(hours=dep_task.duration)
            earliest_start = max(earliest_start, dep_end_time)
    
    # Sinh các khoảng thời gian khả thi bắt đầu từ earliest_start
    current_time = earliest_start
    
    # Làm tròn tới giờ kế tiếp nếu không tròn giờ
    if current_time.minute > 0 or current_time.second > 0:
        current_time = current_time.replace(minute=0, second=0) + timedelta(hours=1)
    
    while current_time < csp.project_end_date:
        # Bỏ qua ngoài giờ làm việc (8h - 17h)
        if current_time.hour < 8 or current_time.hour >= 17:
            current_time = current_time.replace(hour=8, minute=0, second=0) + timedelta(days=1)
            continue
        
        task_end_time = current_time + timedelta(hours=tacvu.duration)
        
        # Bỏ qua nếu tác vụ kết thúc sau 17h
        if task_end_time.hour > 17:
            current_time = current_time.replace(hour=8, minute=0, second=0) + timedelta(days=1)
            continue
        
        # Bỏ qua nếu vượt quá thời hạn dự án
        if task_end_time > csp.project_end_date:
            break
            
        # Bỏ qua nếu vượt quá hạn chót tác vụ
        project_deadline = csp.project_start_date + timedelta(days=tacvu.deadline)
        if task_end_time > project_deadline:
            break
        
        # Thử gán cho từng nhân sự phù hợp
        for nhansu in suitable_employees:
            assignment = CSPAssignment(nhansu, current_time)
            if is_consistent(tacvu, assignment, csp):
                domain.append(assignment)
        
        # Chuyển sang giờ tiếp theo
        current_time += timedelta(hours=1)
    
    return domain

def initialize_domains(csp: CSP):
    """Tạo miền ban đầu cho mỗi tác vụ dựa trên trạng thái assignment hiện tại (ban đầu rỗng)"""
    csp.domains = {}
    for tacvu in csp.cac_tacvu:
        if tacvu.id in csp.assignment:
            csp.domains[tacvu.id] = []
        else:
            csp.domains[tacvu.id] = get_domain_values(tacvu, csp)

def get_neighbors(tacvu: TacVu, csp: CSP) -> List[TacVu]:
    """
    Lấy danh sách hàng xóm của tác vụ từ neighbor_map đã được tính trước
    
    Hàng xóm bao gồm:
    1. Tác vụ phụ thuộc VÀO tacvu
    2. Tác vụ mà tacvu phụ thuộc VÀO
    3. Tác vụ cùng kỹ năng yêu cầu (cạnh tranh nhân sự)
    """
    return csp.neighbor_map.get(tacvu.id, [])

def check_conflict_between_assignments(task1: TacVu, assignment1: CSPAssignment, 
                                       task2: TacVu, assignment2: CSPAssignment, 
                                       csp: CSP) -> bool:
    """
    Kiểm tra xung đột giữa 2 assignment
    Logic tương tự is_consistent() nhưng cho 2 cặp (task, assignment)
    
    Returns:
        True nếu CÓ XUNG ĐỘT
        False nếu KHÔNG XUNG ĐỘT
    """
    end_time_1 = assignment1.start_time + timedelta(hours=task1.duration)
    end_time_2 = assignment2.start_time + timedelta(hours=task2.duration)
    
    # KIỂM TRA 1: Cùng nhân sự + thời gian trùng lặp?
    if assignment1.nhansu.id == assignment2.nhansu.id:
        if (assignment1.start_time < end_time_2 and end_time_1 > assignment2.start_time):
            return True  # CÓ XUNG ĐỘT
    
    # KIỂM TRA 2: Phụ thuộc không thỏa mãn?
    if task2.id in task1.dependencies:
        if assignment1.start_time < end_time_2:
            return True  # CÓ XUNG ĐỘT
    
    if task1.id in task2.dependencies:
        if assignment2.start_time < end_time_1:
            return True  # CÓ XUNG ĐỘT
    
    # KIỂM TRA 3: Deadline bị vượt?
    task1_deadline = csp.project_start_date + timedelta(days=task1.deadline)
    if end_time_1 > task1_deadline:
        return True  # CÓ XUNG ĐỘT
    
    task2_deadline = csp.project_start_date + timedelta(days=task2.deadline)
    if end_time_2 > task2_deadline:
        return True  # CÓ XUNG ĐỘT
    
    # KIỂM TRA 4: Ngoài khung thời gian dự án?
    if assignment1.start_time < csp.project_start_date or end_time_1 > csp.project_end_date:
        return True  # CÓ XUNG ĐỘT
    
    if assignment2.start_time < csp.project_start_date or end_time_2 > csp.project_end_date:
        return True  # CÓ XUNG ĐỘT
    
    return False  # KHÔNG XUNG ĐỘT

# ==================== AC-3 IMPLEMENTATION ====================

def create_all_arcs(csp: CSP) -> List[Tuple[TacVu, TacVu]]:
    """
    Tạo danh sách tất cả các arc (cung) trong bài toán
    Arc = Cặp (task_i, task_j) có ràng buộc với nhau
    
    Returns:
        List of tuples: [(task_i, task_j), ...]
    """
    arcs = []
    
    for task_i in csp.cac_tacvu:
        # Tìm tất cả hàng xóm của task_i (sử dụng hàm đã có)
        neighbors = get_neighbors(task_i, csp)
        
        for task_j in neighbors:
            # Thêm arc (task_i, task_j)
            arcs.append((task_i, task_j))
    
    return arcs

def revise(task_i: TacVu, task_j: TacVu, csp: CSP) -> bool:
    """
    Kiểm tra Arc(task_i, task_j) có consistent không
    Nếu không, loại bỏ các giá trị không hợp lệ khỏi domain của task_i
    
    Returns:
        True nếu có thay đổi domain của task_i
        False nếu không có thay đổi
    """
    revised = False  # Cờ đánh dấu có thay đổi domain không
    domain_i = csp.domains.get(task_i.id, [])
    domain_j = csp.domains.get(task_j.id, [])
    
    # Danh sách giá trị cần loại bỏ
    to_remove = []
    
    # Duyệt qua từng giá trị trong domain của task_i
    for value_i in domain_i:
        # Kiểm tra xem có TỒN TẠI ít nhất 1 giá trị trong domain_j
        # sao cho (value_i, value_j) không xung đột không?
        
        found_consistent_value = False
        
        for value_j in domain_j:
            # Kiểm tra xung đột giữa 2 assignment (sử dụng hàm đã có)
            has_conflict = check_conflict_between_assignments(
                task_i, value_i,
                task_j, value_j,
                csp
            )
            
            # Nếu KHÔNG xung đột → Tìm được giá trị hợp lệ
            if not has_conflict:
                found_consistent_value = True
                break  # Không cần kiểm tra thêm
        
        # Nếu KHÔNG TÌM ĐƯỢC giá trị nào hợp lệ
        if not found_consistent_value:
            # Đánh dấu để loại bỏ value_i khỏi domain của task_i
            to_remove.append(value_i)
            revised = True
    
    # Cắt tỉa domain
    for value_to_remove in to_remove:
        csp.domains[task_i.id].remove(value_to_remove)
        csp.ac3_pruned_count += 1
    
    return revised  # True nếu có thay đổi, False nếu không

def ac3_preprocess(csp: CSP) -> bool:
    """
    Áp dụng AC-3 để cắt tỉa domain ban đầu trước khi tìm kiếm
    
    Returns:
        True nếu AC-3 thành công (không phát hiện ngõ cụt)
        False nếu phát hiện domain rỗng (bài toán không có lời giải)
    """
    # Tạo hàng đợi chứa tất cả các arc (cung)
    queue = deque(create_all_arcs(csp))
    # Sử dụng set để theo dõi các arc đã có trong queue (tránh trùng lặp)
    in_queue = set(queue)
    
    # Xử lý từng arc trong hàng đợi
    while queue:
        # Lấy một arc ra khỏi hàng đợi
        arc = queue.popleft()
        task_i, task_j = arc
        in_queue.discard(arc)  # Xóa khỏi set theo dõi
        
        # Kiểm tra và cắt tỉa domain của task_i dựa trên task_j
        revised = revise(task_i, task_j, csp)
        
        # Nếu domain của task_i bị thay đổi
        if revised:
            # Kiểm tra ngõ cụt
            if len(csp.domains[task_i.id]) == 0:
                return False  # Phát hiện ngõ cụt!
            
            # LAN TRUYỀN: Thêm tất cả arc (task_k, task_i) vào hàng đợi
            # (các hàng xóm của task_i cũng cần kiểm tra lại)
            neighbors = get_neighbors(task_i, csp)
            for task_k in neighbors:
                if task_k.id != task_j.id:
                    new_arc = (task_k, task_i)
                    # Chỉ thêm nếu chưa có trong queue (tránh trùng lặp)
                    if new_arc not in in_queue:
                        queue.append(new_arc)
                        in_queue.add(new_arc)
    
    # AC-3 hoàn thành mà không phát hiện ngõ cụt
    return True

# ==================== SOFT CONSTRAINTS OPTIMIZATION ====================

def calculate_workload(nhansu: NhanSu, csp: CSP) -> int:
    """Tính tổng số giờ làm việc đã được gán cho nhân sự"""
    total_hours = 0
    for task_id, assignment in csp.assignment.items():
        if assignment.nhansu.id == nhansu.id:
            task = next(t for t in csp.cac_tacvu if t.id == task_id)
            total_hours += task.duration
    return total_hours

def calculate_load_balance_score(csp: CSP) -> float:
    """
    Tính điểm cân bằng tải (Load Balance)
    Điểm càng cao = cân bằng càng tốt
    Sử dụng độ lệch chuẩn: độ lệch càng nhỏ = cân bằng càng tốt
    """
    if not csp.assignment:
        return 0.0
    
    workloads = [calculate_workload(nhansu, csp) for nhansu in csp.cac_nhansu]
    avg_workload = sum(workloads) / len(workloads)
    
    # Tính độ lệch chuẩn
    variance = sum((w - avg_workload) ** 2 for w in workloads) / len(workloads)
    std_dev = variance ** 0.5
    
    # Chuyển đổi thành điểm: độ lệch càng nhỏ = điểm càng cao
    # Sử dụng công thức: score = 1 / (1 + std_dev)
    score = 1.0 / (1.0 + std_dev)
    return score

def calculate_priority_score(csp: CSP) -> float:
    """
    Tính điểm ưu tiên (Priority)
    Ưu tiên các tác vụ có độ ưu tiên cao được thực hiện sớm
    
    Công thức: Tổng (priority × (1 - normalized_start_time))
    """
    if not csp.assignment:
        return 0.0
    
    total_score = 0.0
    project_duration = (csp.project_end_date - csp.project_start_date).total_seconds()
    
    for task_id, assignment in csp.assignment.items():
        task = next(t for t in csp.cac_tacvu if t.id == task_id)
        
        # Tính thời điểm bắt đầu chuẩn hóa (0 = bắt đầu dự án, 1 = kết thúc dự án)
        time_elapsed = (assignment.start_time - csp.project_start_date).total_seconds()
        normalized_time = time_elapsed / project_duration if project_duration > 0 else 0
        
        # Tác vụ ưu tiên cao thực hiện sớm → điểm cao
        task_score = task.priority * (1.0 - normalized_time)
        total_score += task_score
    
    # Chuẩn hóa điểm (chia cho tổng priority của tất cả tác vụ)
    total_priority = sum(t.priority for t in csp.cac_tacvu)
    normalized_score = total_score / total_priority if total_priority > 0 else 0
    
    return normalized_score

def evaluate_soft_constraints(assignment: CSPAssignment, tacvu: TacVu, csp: CSP) -> float:
    """
    Đánh giá mức độ thỏa mãn ràng buộc mềm cho một phép gán
    Trả về điểm: điểm càng cao = càng tốt
    
    Ràng buộc mềm bao gồm:
    1. Load Balance: Cân bằng tải giữa các nhân sự
    2. Priority: Ưu tiên tác vụ có độ ưu tiên cao thực hiện sớm
    """
    # Tính workload hiện tại của nhân sự này
    current_workload = calculate_workload(assignment.nhansu, csp)
    new_workload = current_workload + tacvu.duration
    
    # Tính workload trung bình
    total_assigned_hours = sum(calculate_workload(emp, csp) for emp in csp.cac_nhansu)
    avg_workload = total_assigned_hours / len(csp.cac_nhansu) if csp.cac_nhansu else 0
    
    # 1. Load Balance Score: Ưu tiên nhân sự có workload thấp hơn
    # Nếu new_workload gần avg_workload → điểm cao
    load_balance_diff = abs(new_workload - avg_workload)
    load_balance_score = 1.0 / (1.0 + load_balance_diff)
    
    # 2. Priority Score: Ưu tiên tác vụ có độ ưu tiên cao thực hiện sớm
    project_duration = (csp.project_end_date - csp.project_start_date).total_seconds()
    time_elapsed = (assignment.start_time - csp.project_start_date).total_seconds()
    normalized_time = time_elapsed / project_duration if project_duration > 0 else 0
    
    # Tác vụ ưu tiên cao thực hiện sớm → điểm cao
    max_priority = max((t.priority for t in csp.cac_tacvu), default=1)
    priority_score = (tacvu.priority / max_priority) * (1.0 - normalized_time)
    
    # Kết hợp 2 điểm (trọng số có thể điều chỉnh)
    LOAD_BALANCE_WEIGHT = 0.4
    PRIORITY_WEIGHT = 0.6
    
    total_score = (LOAD_BALANCE_WEIGHT * load_balance_score + 
                   PRIORITY_WEIGHT * priority_score)
    
    return total_score

# ==================== HEURISTICS ====================

def count_conflicts(assignment: CSPAssignment, tacvu: TacVu, csp: CSP) -> int:
    """
    Đếm số lượng xung đột (conflicts) mà assignment này gây ra cho các tác vụ chưa gán khác.
    Xung đột xảy ra khi assignment này làm giảm số lựa chọn hợp lệ của tác vụ khác.
    """
    conflicts = 0
    task_end_time = assignment.start_time + timedelta(hours=tacvu.duration)
    
    # Duyệt qua tất cả các tác vụ chưa được gán
    unassigned_tasks = [t for t in csp.cac_tacvu if t.id not in csp.assignment and t.id != tacvu.id]
    
    for other_task in unassigned_tasks:
        # Kiểm tra xem việc gán này có ảnh hưởng đến tác vụ khác không
        if other_task.required_skill in assignment.nhansu.skills:
            # Tìm thời gian bắt đầu sớm nhất cho other_task
            earliest_start = csp.project_start_date
            for dep_task_id in other_task.dependencies:
                if dep_task_id in csp.assignment:
                    dep_assignment = csp.assignment[dep_task_id]
                    dep_task = next(t for t in csp.cac_tacvu if t.id == dep_task_id)
                    dep_end_time = dep_assignment.start_time + timedelta(hours=dep_task.duration)
                    earliest_start = max(earliest_start, dep_end_time)
                elif dep_task_id == tacvu.id:
                    # Nếu other_task phụ thuộc vào tacvu hiện tại
                    earliest_start = max(earliest_start, task_end_time)
            
            other_end_time = earliest_start + timedelta(hours=other_task.duration)
            
            # Kiểm tra xung đột thời gian với nhân sự này
            if (assignment.start_time < other_end_time and 
                task_end_time > earliest_start):
                conflicts += 1
    
    return conflicts

def order_domain_values_with_lcv(tacvu: TacVu, domain_values: List[CSPAssignment], csp: CSP) -> List[CSPAssignment]:
    """
    LCV (Least Constraining Value) Heuristic + Soft Constraints Optimization
    Sắp xếp các giá trị miền, ưu tiên:
    1. Ít gây xung đột nhất (LCV)
    2. Thỏa mãn ràng buộc mềm tốt nhất (Priority + Load Balance)
    """
    if not domain_values:
        return domain_values
    
    # Tính điểm cho mỗi giá trị
    value_scores = []
    
    for assignment in domain_values:
        # 1. Đếm số xung đột (LCV)
        conflicts = count_conflicts(assignment, tacvu, csp)
        
        # 2. Đánh giá ràng buộc mềm
        soft_score = evaluate_soft_constraints(assignment, tacvu, csp)
        
        # Kết hợp điểm: ưu tiên ít xung đột + điểm ràng buộc mềm cao
        # Xung đột càng ít = điểm càng cao
        # Chuyển conflicts thành điểm âm để kết hợp
        conflict_score = -conflicts
        
        # Trọng số kết hợp (có thể điều chỉnh)
        LCV_WEIGHT = 0.7
        SOFT_WEIGHT = 0.3
        
        total_score = LCV_WEIGHT * conflict_score + SOFT_WEIGHT * soft_score
        
        value_scores.append((assignment, total_score))
    
    # Sắp xếp theo điểm giảm dần (điểm cao nhất trước)
    value_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Trả về danh sách assignments đã sắp xếp
    return [assignment for assignment, _ in value_scores]

def select_variable_with_mrv(csp: CSP, current_domains: Dict[str, List[CSPAssignment]]) -> Optional[TacVu]:
    """
    MRV (Minimum Remaining Values) Heuristic + Priority Tie-Breaking
    Chọn tác vụ có ít lựa chọn hợp lệ nhất (fail-fast strategy)
    Nếu có nhiều tác vụ cùng số lựa chọn, ưu tiên tác vụ có priority cao hơn
    """
    unassigned_tasks = [tacvu for tacvu in csp.cac_tacvu if tacvu.id not in csp.assignment]
    if not unassigned_tasks:
        return None
    
    # Lọc các tác vụ có đủ điều kiện (phụ thuộc đã hoàn thành)
    ready_tasks = []
    for tacvu in unassigned_tasks:
        dependencies_satisfied = all(dep in csp.assignment for dep in tacvu.dependencies)
        if dependencies_satisfied:
            ready_tasks.append(tacvu)
    
    if not ready_tasks:
        return None
    
    # Domain sizes để tránh tính lại nhiều lần
    domain_sizes = {tacvu.id: len(current_domains.get(tacvu.id, [])) 
                    for tacvu in ready_tasks}
    
    # Tìm tác vụ có ít lựa chọn hợp lệ nhất dựa trên current_domains
    min_choices = float('inf')
    candidates = []
    
    for tacvu in ready_tasks:
        num_choices = domain_sizes[tacvu.id]
        
        if num_choices < min_choices:
            min_choices = num_choices
            candidates = [tacvu]
        elif num_choices == min_choices:
            candidates.append(tacvu)
    
    # Nếu có nhiều tác vụ cùng số lựa chọn, chọn tác vụ có priority cao nhất
    if len(candidates) > 1:
        candidates.sort(key=lambda t: t.priority, reverse=True)
    
    return candidates[0] if candidates else None

# ==================== FORWARD CHECKING ====================

def forward_checking(csp: CSP, assigned_task_id: str) -> bool:
    """
    Thực hiện Forward Checking - cắt tỉa domain hàng xóm
    Mục đích: Phát hiện ngõ cụt sớm và giảm không gian tìm kiếm
    
    Returns:
        True nếu không phát hiện ngõ cụt, False nếu có domain trở thành rỗng
    """
    assigned_task = next(t for t in csp.cac_tacvu if t.id == assigned_task_id)
    assigned_assignment = csp.assignment[assigned_task_id]
    
    # Lấy tất cả hàng xóm của tác vụ vừa gán
    neighbors = get_neighbors(assigned_task, csp)
    
    # Duyệt qua các hàng xóm chưa được gán
    for neighbor_task in neighbors:
        if neighbor_task.id not in csp.assignment:
            original_domain = csp.domains.get(neighbor_task.id, [])
            new_domain = []
            
            # Kiểm tra từng giá trị trong domain của hàng xóm
            for neighbor_value in original_domain:
                # Kiểm tra xung đột giữa assignment vừa gán và giá trị này
                has_conflict = check_conflict_between_assignments(
                    assigned_task, assigned_assignment,
                    neighbor_task, neighbor_value,
                    csp
                )
                
                if not has_conflict:
                    # Không xung đột → giữ lại
                    new_domain.append(neighbor_value)
                else:
                    # Có xung đột → cắt bỏ
                    csp.fc_pruned_count += 1
            
            # CẬP NHẬT domain mới (đã cắt tỉa)
            csp.domains[neighbor_task.id] = new_domain
            
            # PHÁT HIỆN NGÕ CỤT SỚM (FAIL-FAST)
            if len(csp.domains[neighbor_task.id]) == 0:
                return False  # Báo hiệu ngõ cụt!
    
    # Cắt tỉa tất cả hàng xóm mà không ai bị rỗng
    return True  # Thành công, có thể tiếp tục

# ==================== BACKTRACKING ====================

def recursive_backtracking(csp: CSP, current_domains: Dict[str, List[CSPAssignment]]) -> bool:
    """
    Giải bằng thuật toán quay lui đệ quy (backtracking) với MRV + LCV + Forward Checking
    
    Args:
        csp: Đối tượng CSP chứa assignment và thông tin bài toán
        current_domains: Miền giá trị hiện tại của tầng đệ quy này (đã được cắt tỉa từ các tầng trước)
    """
    # Trường hợp cơ sở: tất cả tác vụ đã được gán
    if len(csp.assignment) == len(csp.cac_tacvu):
        csp.solution_found = True
        return True
    
    # Chọn biến chưa gán bằng MRV Heuristic (luôn dùng)
    tacvu = select_variable_with_mrv(csp, current_domains)
    
    if tacvu is None:
        # không còn task ready (có thể deadlock) -> thất bại ở nhánh này
        return False
    
    # Lấy các giá trị miền từ current_domains (đã được cắt tỉa)
    domain_values = current_domains.get(tacvu.id, [])
    if not domain_values:
        return False
    
    # Sắp xếp theo LCV + Soft Constraints (luôn dùng)
    domain_values = order_domain_values_with_lcv(tacvu, domain_values, csp)
    
    # Thử từng giá trị
    for assignment in list(domain_values):
        # 1. Thực hiện phép gán
        csp.assignment[tacvu.id] = assignment
        
        # 2. TẠO BẢN SAO DOMAIN ĐỂ CHUẨN BỊ "CẮT TỈA" (Deep Copy)
        new_domains = {}
        for task_id in current_domains.keys():
            new_domains[task_id] = current_domains[task_id].copy()
        
        # Đánh dấu task hiện tại đã gán (domain rỗng)
        new_domains[tacvu.id] = []
        
        # 3. Cập nhật csp.domains để is_consistent() và forward_checking() sử dụng
        csp.domains = new_domains
        
        # 4. THỰC HIỆN FORWARD CHECKING (luôn dùng)
        # Hàm này sẽ cắt tỉa new_domains và phát hiện ngõ cụt sớm
        forward_ok = forward_checking(csp, tacvu.id)
        
        # 5. Nếu Forward Check không phát hiện ngõ cụt
        if forward_ok:
            # Gọi đệ quy với new_domains đã bị cắt tỉa
            result = recursive_backtracking(csp, csp.domains)
            if result:
                return True
        
        # 6. QUAY LUI (Backtrack) - Xóa assignment hiện tại
        del csp.assignment[tacvu.id]
        csp.backtrack_count += 1
        # Vứt bỏ new_domains - vòng lặp tiếp theo dùng current_domains gốc
    
    # Nếu đã thử hết các giá trị mà không tìm được lời giải
    return False

# ==================== MAIN SOLVER ====================

def solve_csp(dataset_folder: str, project_start_date: datetime, project_end_date: datetime) -> CSP:
    """
    Hàm tổng hợp để giải bài toán CSP
    Sử dụng: AC-3 Preprocessing + Backtracking + MRV + LCV + Forward Checking + Soft Constraints
    
    Args:
        dataset_folder: Đường dẫn tới thư mục dữ liệu
        project_start_date: Ngày bắt đầu dự án
        project_end_date: Ngày kết thúc dự án
    """
    
    # Nạp dữ liệu
    cac_tacvu, cac_nhansu = load_data(dataset_folder)
    
    # Tạo đối tượng CSP
    csp = CSP(cac_tacvu, cac_nhansu, project_start_date, project_end_date)
    
    print("\n[BƯỚC 1] Khởi tạo miền ban đầu...")
    # Khởi tạo miền ban đầu
    initialize_domains(csp)
    initial_domain_size = sum(len(domain) for domain in csp.domains.values())
    print(f"  → Tổng số giá trị trong miền ban đầu: {initial_domain_size}")
    
    print("\n[BƯỚC 2] Tiền xử lý bằng AC-3...")
    # BƯỚC MỚI: Tiền xử lý bằng AC-3
    is_consistent = ac3_preprocess(csp)
    
    # Nếu AC-3 phát hiện domain rỗng → Không có lời giải
    if not is_consistent:
        print("  ✗ AC-3 phát hiện bài toán không có lời giải!")
        print("  → Domain của một hoặc nhiều tác vụ đã trở thành rỗng.")
        return csp
    
    after_ac3_size = sum(len(domain) for domain in csp.domains.values())
    print(f"  ✓ AC-3 hoàn thành thành công!")
    print(f"  → Tổng số giá trị sau AC-3: {after_ac3_size}")
    print(f"  → Số giá trị bị cắt bởi AC-3: {csp.ac3_pruned_count}")
    print(f"  → Tỷ lệ cắt giảm: {(initial_domain_size - after_ac3_size) / initial_domain_size * 100:.2f}%")
    
    print("\n[BƯỚC 3] Bắt đầu Backtracking với MRV + LCV + Forward Checking...")
    # Tạo bản sao initial_domains đã được AC-3 cắt tỉa
    initial_domains = {}
    for task_id in csp.domains:
        initial_domains[task_id] = csp.domains[task_id].copy()
    
    # Gọi hàm đệ quy với domain đã được tối ưu
    recursive_backtracking(csp, initial_domains)
    
    return csp

def display_solution(csp: CSP):
    """Hiển thị kết quả phân công"""
    if not csp.solution_found:
        print("\n✗ Không tìm thấy giải pháp!")
        return
    
    sorted_assignments = sorted(csp.assignment.items(), 
                              key=lambda x: x[1].start_time)
    
    print("\n" + "="*70)
    print("KẾT QUẢ PHÂN CÔNG CÔNG VIỆC")
    print("="*70 + "\n")
    
    for task_id, assignment in sorted_assignments:
        tacvu = next(t for t in csp.cac_tacvu if t.id == task_id)
        start_time = assignment.start_time
        end_time = start_time + timedelta(hours=tacvu.duration)
        
        print(f"Tác vụ {tacvu.id} ({tacvu.name}): {assignment.nhansu.name} ({assignment.nhansu.id})")
        print(f"  - Ngày bắt đầu: {start_time.strftime('%H:%M %d/%m/%Y')}")
        print(f"  - Ngày kết thúc: {end_time.strftime('%H:%M %d/%m/%Y')}")
        print(f"  - Thời lượng: {tacvu.duration} giờ")
        print(f"  - Độ ưu tiên: {tacvu.priority}\n")
    
    # Hiển thị điểm ràng buộc mềm
    print("="*70)
    print("ĐÁNH GIÁ RÀNG BUỘC MỀM")
    print("="*70)
    
    load_balance_score = calculate_load_balance_score(csp)
    priority_score = calculate_priority_score(csp)
    
    print(f"\n1. Load Balance Score: {load_balance_score:.4f}")
    print("   (Điểm càng cao = cân bằng tải càng tốt)")
    
    print(f"\n2. Priority Score: {priority_score:.4f}")
    print("   (Điểm càng cao = tác vụ ưu tiên cao được thực hiện sớm hơn)")
    
    print(f"\n3. Tổng thể: {(load_balance_score + priority_score) / 2:.4f}")
    
    # Hiển thị workload của từng nhân sự
    print("\n" + "="*70)
    print("PHÂN BỐ CÔNG VIỆC THEO NHÂN SỰ")
    print("="*70 + "\n")
    
    for nhansu in csp.cac_nhansu:
        workload = calculate_workload(nhansu, csp)
        tasks_assigned = [task_id for task_id, assignment in csp.assignment.items() 
                         if assignment.nhansu.id == nhansu.id]
        print(f"{nhansu.name} ({nhansu.id}): {workload} giờ ({len(tasks_assigned)} tác vụ)")

def export_to_csv(csp: CSP, filename: str = "task_assignment.csv"):
    """Xuất kết quả ra file CSV"""
    if not csp.solution_found:
        print("Không có giải pháp để xuất!")
        return
    
    csv_data = []
    for task_id, assignment in csp.assignment.items():
        tacvu = next(t for t in csp.cac_tacvu if t.id == task_id)
        start_time = assignment.start_time
        end_time = start_time + timedelta(hours=tacvu.duration)
        
        csv_data.append({
            'Task_ID': tacvu.id,
            'Task_Name': tacvu.name,
            'Employee_ID': assignment.nhansu.id,
            'Employee_Name': assignment.nhansu.name,
            'Start_Date': start_time.strftime('%d/%m/%Y'),
            'Start_Time': start_time.strftime('%H:%M'),
            'End_Date': end_time.strftime('%d/%m/%Y'),
            'End_Time': end_time.strftime('%H:%M'),
            'Duration_Hours': tacvu.duration,
            'Priority': tacvu.priority,
            'Required_Skill': tacvu.required_skill
        })
    
    csv_data.sort(key=lambda x: datetime.strptime(f"{x['Start_Date']} {x['Start_Time']}", '%d/%m/%Y %H:%M'))
    
    df = pd.DataFrame(csv_data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n✓ Kết quả đã được xuất ra file: {filename}")
    
    print("\n" + "="*70)
    print("BẢNG PHÂN CÔNG CÔNG VIỆC")
    print("="*70)
    print(df.to_string(index=False))

def main():
    """Chương trình chính để chạy bộ giải CSP"""
    print("="*70)
    print("HỆ THỐNG PHÂN CÔNG CÔNG VIỆC SỬ DỤNG CSP - MÔ HÌNH TỐI ƯU")
    print("="*70)
    print("\nCác thuật toán được tích hợp:")
    print("  • AC-3 Preprocessing (Arc Consistency)")
    print("  • Backtracking với MRV + LCV Heuristics")
    print("  • Forward Checking")
    print("  • Soft Constraints Optimization (Priority + Load Balance)")
    print("="*70 + "\n")
    
    print("Chọn bộ dữ liệu:")
    print("\n=== BỘ DỮ LIỆU CHÍNH (Đánh giá tổng quan) ===")
    print("1. small_project - Dự án nhỏ (5 NV, 20 tasks)")
    print("2. medium_project - Dự án vừa (14 NV, 32 tasks)")
    print("3. large_project - Dự án lớn (15 NV, 50 tasks)")
    
    choice = input("\nNhập lựa chọn (1-3): ").strip()
    
    dataset_map = {
        '1': 'small_project',
        '2': 'medium_project',
        '3': 'large_project'
    }
    
    if choice not in dataset_map:
        print("Lựa chọn không hợp lệ!")
        return
    
    dataset_folder = f"datasets/{dataset_map[choice]}"
    
    print("\nNhập thông tin dự án:")
    start_date_str = input("Ngày bắt đầu dự án (dd/mm/yyyy): ").strip()
    end_date_str = input("Ngày kết thúc dự án (dd/mm/yyyy): ").strip()
    
    try:
        project_start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
        project_end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
        project_start_date = project_start_date.replace(hour=8, minute=0, second=0)
        project_end_date = project_end_date.replace(hour=17, minute=0, second=0)
    except ValueError:
        print("Định dạng ngày không đúng! Vui lòng nhập theo dạng dd/mm/yyyy")
        return
    
    print(f"\n{'='*70}")
    print(f"Bộ dữ liệu: {dataset_folder}")
    print(f"Thời gian dự án: {project_start_date.strftime('%d/%m/%Y %H:%M')} - {project_end_date.strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*70}")
    
    import time
    start_time = time.time()
    
    csp = solve_csp(dataset_folder, project_start_date, project_end_date)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    if csp.solution_found:
        print(f"\n✓ Tìm thấy lời giải!")
    
    display_solution(csp)
    
    print(f"\n{'='*70}")
    print("THỐNG KÊ HIỆU SUẤT")
    print(f"{'='*70}")
    print(f"Thời gian thực thi: {execution_time:.4f} giây")
    print(f"Số giá trị bị cắt bởi AC-3: {csp.ac3_pruned_count}")
    print(f"Số giá trị bị cắt bởi Forward Checking: {csp.fc_pruned_count}")
    print(f"Số lần Backtrack: {csp.backtrack_count}")
    print(f"{'='*70}")
    
    if csp.solution_found:
        export_to_csv(csp, f"task_assignment_{dataset_map[choice]}_advanced.csv")

if __name__ == "__main__":
    main()

