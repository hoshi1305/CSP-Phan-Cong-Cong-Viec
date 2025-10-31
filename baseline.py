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
    """Chọn tác vụ chưa được gán tiếp theo"""
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

def recursive_backtracking(csp: CSP) -> bool:
    """Giải bằng thuật toán quay lui đệ quy (backtracking)"""
    
    # Trường hợp cơ sở: tất cả tác vụ đã được gán
    if len(csp.assignment) == len(csp.cac_tacvu):
        csp.solution_found = True
        return True
    
    # Chọn biến chưa gán
    tacvu = select_next_unassigned_variable(csp)
    if tacvu is None:
        return True
    
    # Lấy các giá trị miền cho tác vụ
    domain_values = get_domain_values(tacvu, csp)
    
    # Thử từng giá trị
    for assignment in domain_values:
        csp.assignment[tacvu.id] = assignment
        
        if recursive_backtracking(csp):
            return True
        
        # Quay lui
        del csp.assignment[tacvu.id]
    
    return False

def solve_csp(dataset_folder: str, project_start_date: datetime, project_end_date: datetime) -> CSP:
    """Hàm tổng hợp để giải bài toán CSP"""
    
    # Nạp dữ liệu
    cac_tacvu, cac_nhansu = load_data(dataset_folder)
    
    # Tạo đối tượng CSP
    csp = CSP(cac_tacvu, cac_nhansu, project_start_date, project_end_date)
    
    # Giải bằng quay lui
    recursive_backtracking(csp)
    
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
    
    print("Chọn bộ dữ liệu:")
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
    
    print(f"\nĐang giải CSP với bộ dữ liệu: {dataset_folder}")
    print(f"Thời gian dự án: {project_start_date.strftime('%d/%m/%Y %H:%M')} - {project_end_date.strftime('%d/%m/%Y %H:%M')}")
    
    csp = solve_csp(dataset_folder, project_start_date, project_end_date)
    display_solution(csp)
    
    if csp.solution_found:
        export_to_csv(csp, f"task_assignment_{dataset_map[choice]}.csv")

if __name__ == "__main__":
    main()
