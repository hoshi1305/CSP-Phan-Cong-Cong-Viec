#Phương pháp truy tìm bằng thuật toán Heuristics (MRV + LCV)
import csv
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import os
import sys

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
        self.assignment = {}  # ánh xạ task_id -> CSPAssignment
        self.solution_found = False

def load_data(dataset_folder: str) -> Tuple[List[TacVu], List[NhanSu]]:
    """Tải dữ liệu tác vụ và nhân sự từ các tệp CSV trong thư mục chỉ định"""
    # Xác định tên file phù hợp dựa theo thư mục dữ liệu
    if "complex_dependency_chain" in dataset_folder:
        tasks_file = os.path.join(dataset_folder, "congviec_dependency.csv")
        employees_file = os.path.join(dataset_folder, "nhanvien_dependency.csv")
    elif "load_balance" in dataset_folder:
        tasks_file = os.path.join(dataset_folder, "congviec_loadbalance.csv")
        employees_file = os.path.join(dataset_folder, "nhanvien_loadbalance.csv")
    elif "skill_bottleneck" in dataset_folder:
        tasks_file = os.path.join(dataset_folder, "congviec_bottleneck.csv")
        employees_file = os.path.join(dataset_folder, "nhanvien_bottleneck.csv")
    else:
        raise ValueError(f"Không nhận dạng được thư mục dữ liệu: {dataset_folder}")
    
    # Đọc danh sách các tác vụ
    cac_tacvu = []
    with open(tasks_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'ID' in row and row['ID'].strip():  # bỏ qua dòng trống
                dependencies = []
                if row['PhuThuoc'].strip():
                    dependencies = [dep.strip() for dep in row['PhuThuoc'].split(',')]
                
                tacvu = TacVu(
                    task_id=row['ID'].strip(),
                    name=row['TenTask'].strip(),
                    required_skill=row['YeuCauKyNang'].strip(),
                    duration=int(row['ThoiLuong (gio)']),
                    dependencies=dependencies,
                    deadline=int(row['Deadline (ngay)']),
                    priority=int(row['DoUuTien'])
                )
                cac_tacvu.append(tacvu)
    
    # Đọc danh sách nhân sự
    cac_nhansu = []
    with open(employees_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'ID' in row and row['ID'].strip():  # bỏ qua dòng trống
                skills = [skill.strip() for skill in row['KyNang'].split(',')]
                nhansu = NhanSu(
                    emp_id=row['ID'].strip(),
                    name=row['Ten'].strip(),
                    skills=skills,
                    daily_capacity=int(row['SucChua (gio/ngay)'])
                )
                cac_nhansu.append(nhansu)
    
    return cac_tacvu, cac_nhansu

def is_consistent(tacvu: TacVu, assignment: CSPAssignment, csp: CSP) -> bool:
    """Kiểm tra xem việc gán tác vụ cho nhân sự tại thời điểm này có hợp lệ (thỏa mãn ràng buộc) không"""
    
    # 1. Ràng buộc kỹ năng
    if tacvu.required_skill not in assignment.nhansu.skills:
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

def select_next_unassigned_variable(csp: CSP) -> Optional[TacVu]:
    """Chọn tác vụ chưa được gán tiếp theo (baseline - không dùng heuristic)"""
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
    
    return ready_tasks[0]

def select_variable_with_mrv(csp: CSP) -> Optional[TacVu]:
    """
    MRV (Minimum Remaining Values) Heuristic
    Chọn tác vụ có ít lựa chọn hợp lệ nhất (fail-fast strategy)
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
    
    # Tìm tác vụ có ít lựa chọn hợp lệ nhất
    tac_vu_kho_nhat = None
    so_lua_chon_it_nhat = float('inf')
    
    for tacvu in ready_tasks:
        # Đếm số lựa chọn hợp lệ cho tác vụ này
        domain_values = get_domain_values(tacvu, csp)
        so_lua_chon = len(domain_values)
        
        # Nếu tìm thấy tác vụ "khó hơn" (ít lựa chọn hơn), cập nhật
        if so_lua_chon < so_lua_chon_it_nhat:
            so_lua_chon_it_nhat = so_lua_chon
            tac_vu_kho_nhat = tacvu
    
    return tac_vu_kho_nhat

def get_domain_values(tacvu: TacVu, csp: CSP) -> List[CSPAssignment]:
    """Lấy tất cả các phương án gán hợp lệ cho một tác vụ"""
    domain = []
    
    # Tìm nhân sự có kỹ năng phù hợp
    suitable_employees = [emp for emp in csp.cac_nhansu 
                         if tacvu.required_skill in emp.skills]
    
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
        
        # 1. Xung đột về nhân sự và thời gian: 
        # Nếu other_task cũng cần cùng nhân sự và có khoảng thời gian trùng lặp
        if other_task.required_skill in assignment.nhansu.skills:
            # Kiểm tra khoảng thời gian của assignment có ảnh hưởng không
            # Bằng cách thử tạo assignment cho other_task và xem có xung đột không
            
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
                # Có khả năng xung đột
                conflicts += 1
    
    return conflicts

def order_domain_values_with_lcv(tacvu: TacVu, domain_values: List[CSPAssignment], csp: CSP) -> List[CSPAssignment]:
    """
    LCV (Least Constraining Value) Heuristic
    Sắp xếp các giá trị miền, ưu tiên những giá trị ít gây xung đột nhất với các tác vụ khác (succeed-first strategy)
    """
    if not domain_values:
        return domain_values
    
    # Tính điểm "phá đám" cho mỗi giá trị
    value_conflict_scores = []
    
    for assignment in domain_values:
        # Đếm số xung đột mà assignment này gây ra
        conflicts = count_conflicts(assignment, tacvu, csp)
        value_conflict_scores.append((assignment, conflicts))
    
    # Sắp xếp theo số xung đột tăng dần (ít xung đột nhất trước)
    value_conflict_scores.sort(key=lambda x: x[1])
    
    # Trả về danh sách assignments đã sắp xếp
    return [assignment for assignment, _ in value_conflict_scores]

def recursive_backtracking(csp: CSP, use_heuristics: bool = True) -> bool:
    """
    Giải bằng thuật toán quay lui đệ quy (backtracking)
    
    Args:
        csp: Đối tượng CSP
        use_heuristics: True để sử dụng MRV và LCV, False để dùng phương pháp baseline
    """
    
    # Trường hợp cơ sở: tất cả tác vụ đã được gán
    if len(csp.assignment) == len(csp.cac_tacvu):
        csp.solution_found = True
        return True
    
    # Chọn biến chưa gán
    if use_heuristics:
        # Sử dụng MRV heuristic để chọn tác vụ "khó" nhất
        tacvu = select_variable_with_mrv(csp)
    else:
        # Baseline: chọn tác vụ đầu tiên
        tacvu = select_next_unassigned_variable(csp)
    
    if tacvu is None:
        return True
    
    # Lấy các giá trị miền cho tác vụ
    domain_values = get_domain_values(tacvu, csp)
    
    # Sắp xếp các giá trị miền
    if use_heuristics:
        # Sử dụng LCV heuristic để sắp xếp giá trị "an toàn" nhất trước
        domain_values = order_domain_values_with_lcv(tacvu, domain_values, csp)
    # Nếu không dùng heuristic, giữ nguyên thứ tự
    
    # Thử từng giá trị
    for assignment in domain_values:
        csp.assignment[tacvu.id] = assignment
        
        if recursive_backtracking(csp, use_heuristics):
            return True
        
        # Quay lui
        del csp.assignment[tacvu.id]
    
    return False

def solve_csp(dataset_folder: str, project_start_date: datetime, project_end_date: datetime, 
              use_heuristics: bool = True) -> CSP:
    """
    Hàm tổng hợp để giải bài toán CSP
    
    Args:
        dataset_folder: Đường dẫn tới thư mục dữ liệu
        project_start_date: Ngày bắt đầu dự án
        project_end_date: Ngày kết thúc dự án
        use_heuristics: True để sử dụng MRV + LCV, False để dùng baseline
    """
    
    # Nạp dữ liệu
    cac_tacvu, cac_nhansu = load_data(dataset_folder)
    
    # Tạo đối tượng CSP
    csp = CSP(cac_tacvu, cac_nhansu, project_start_date, project_end_date)
    
    # Giải bằng quay lui
    recursive_backtracking(csp, use_heuristics)
    
    return csp

def display_solution(csp: CSP):
    """Hiển thị kết quả phân công"""
    if not csp.solution_found:
        print("Không tìm thấy giải pháp!")
        return
    
    sorted_assignments = sorted(csp.assignment.items(), 
                              key=lambda x: x[1].start_time)
    
    print("\n=== KẾT QUẢ PHÂN CÔNG CÔNG VIỆC ===\n")
    
    for task_id, assignment in sorted_assignments:
        tacvu = next(t for t in csp.cac_tacvu if t.id == task_id)
        start_time = assignment.start_time
        end_time = start_time + timedelta(hours=tacvu.duration)
        
        print(f"Tác vụ {tacvu.id} ({tacvu.name}): {assignment.nhansu.name} ({assignment.nhansu.id})")
        print(f"  - Ngày bắt đầu: {start_time.strftime('%H:%M %d/%m/%Y')}")
        print(f"  - Ngày kết thúc: {end_time.strftime('%H:%M %d/%m/%Y')}")
        print(f"  - Thời lượng: {tacvu.duration} giờ\n")

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
    print(f"\nKết quả đã được xuất ra file: {filename}")
    
    print("\n=== BẢNG PHÂN CÔNG CÔNG VIỆC ===")
    print(df.to_string(index=False))

def main():
    """Chương trình chính để chạy bộ giải CSP"""
    print("=== HỆ THỐNG PHÂN CÔNG CÔNG VIỆC SỬ DỤNG CSP ===\n")
    
    print("Chọn phương pháp giải:")
    print("1. Baseline (Backtracking cơ bản)")
    print("2. Heuristics (MRV + LCV)")
    
    method_choice = input("Nhập lựa chọn (1-2): ").strip()
    
    if method_choice not in ['1', '2']:
        print("Lựa chọn không hợp lệ!")
        return
    
    use_heuristics = (method_choice == '2')
    method_name = "Heuristics (MRV + LCV)" if use_heuristics else "Baseline"
    
    print("\nChọn bộ dữ liệu:")
    print("1. complex_dependency_chain")
    print("2. load_balance") 
    print("3. skill_bottleneck")
    
    choice = input("Nhập lựa chọn (1-3): ").strip()
    
    dataset_map = {
        '1': 'complex_dependency_chain',
        '2': 'load_balance',
        '3': 'skill_bottleneck'
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
    print(f"Phương pháp: {method_name}")
    print(f"Bộ dữ liệu: {dataset_folder}")
    print(f"Thời gian dự án: {project_start_date.strftime('%d/%m/%Y %H:%M')} - {project_end_date.strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*70}\n")
    
    import time
    start_time = time.time()
    
    csp = solve_csp(dataset_folder, project_start_date, project_end_date, use_heuristics)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    display_solution(csp)
    
    print(f"\n{'='*70}")
    print(f"Thời gian thực thi: {execution_time:.4f} giây")
    print(f"{'='*70}")
    
    if csp.solution_found:
        suffix = "heuristics" if use_heuristics else "baseline"
        export_to_csv(csp, f"task_assignment_{dataset_map[choice]}_{suffix}.csv")

if __name__ == "__main__":
    main()
