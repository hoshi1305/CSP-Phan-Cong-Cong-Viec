"""
Script thực nghiệm để chạy Baseline và Advanced model nhiều lần
và thu thập thống kê cho báo cáo
"""
import sys
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'  # Hỗ trợ Unicode

# Import các module
import baseline
import advanced

# Python 3 đã hỗ trợ UTF-8 mặc định, không cần thiết lập lại


def calculate_makespan(csp_result) -> float:
    """Tính thời gian hoàn thành dự án (ngày)"""
    if not csp_result.assignment:
        return 0.0
    
    max_end_time = None
    for task_id, assignment in csp_result.assignment.items():
        task = next(t for t in csp_result.cac_tacvu if t.id == task_id)
        end_time = assignment.start_time + timedelta(hours=task.duration)
        if max_end_time is None or end_time > max_end_time:
            max_end_time = end_time
    
    makespan = max_end_time - csp_result.project_start_date
    return makespan.total_seconds() / 86400  # Trả về số ngày


def calculate_constraint_satisfaction(csp_result) -> float:
    """
    Tính % ràng buộc thỏa mãn
    Kiểm tra tất cả ràng buộc cứng: kỹ năng, phụ thuộc, deadline, sức chứa, khung giờ
    """
    if not csp_result.assignment:
        return 0.0
    
    total_constraints = 0
    satisfied_constraints = 0
    
    for task_id, assignment in csp_result.assignment.items():
        task = next(t for t in csp_result.cac_tacvu if t.id == task_id)
        start_time = assignment.start_time
        end_time = start_time + timedelta(hours=task.duration)
        
        # 1. Ràng buộc kỹ năng
        total_constraints += 1
        if task.required_skill in assignment.nhansu.skills:
            satisfied_constraints += 1
        
        # 2. Ràng buộc phụ thuộc
        for dep_id in task.dependencies:
            total_constraints += 1
            if dep_id in csp_result.assignment:
                dep_assignment = csp_result.assignment[dep_id]
                dep_task = next(t for t in csp_result.cac_tacvu if t.id == dep_id)
                dep_end = dep_assignment.start_time + timedelta(hours=dep_task.duration)
                if start_time >= dep_end:
                    satisfied_constraints += 1
        
        # 3. Ràng buộc deadline
        total_constraints += 1
        deadline = csp_result.project_start_date + timedelta(days=task.deadline)
        if end_time <= deadline:
            satisfied_constraints += 1
        
        # 4. Ràng buộc khung thời gian dự án
        total_constraints += 1
        if (start_time >= csp_result.project_start_date and 
            end_time <= csp_result.project_end_date):
            satisfied_constraints += 1
        
        # 5. Ràng buộc khung giờ làm việc (8h-17h)
        total_constraints += 1
        if (start_time.hour >= 8 and start_time.hour < 17 and
            end_time.hour >= 8 and end_time.hour <= 17):
            satisfied_constraints += 1
    
    # 6. Ràng buộc sức chứa (kiểm tra mỗi nhân viên mỗi ngày)
    for nhansu in csp_result.cac_nhansu:
        # Nhóm công việc theo ngày
        daily_workload = {}
        for task_id, assignment in csp_result.assignment.items():
            if assignment.nhansu.id == nhansu.id:
                task = next(t for t in csp_result.cac_tacvu if t.id == task_id)
                work_date = assignment.start_time.date()
                if work_date not in daily_workload:
                    daily_workload[work_date] = 0
                daily_workload[work_date] += task.duration
        
        # Kiểm tra mỗi ngày
        for work_date, total_hours in daily_workload.items():
            total_constraints += 1
            if total_hours <= nhansu.daily_capacity:
                satisfied_constraints += 1
    
    return (satisfied_constraints / total_constraints * 100.0) if total_constraints > 0 else 0.0


def calculate_workload_std_dev(csp_result) -> float:
    """
    Tính độ lệch chuẩn workload (Standard Deviation)
    Đo sự phân bố công việc giữa các nhân viên
    """
    if not csp_result.assignment:
        return 0.0
    
    # Tính workload cho mỗi nhân viên
    workloads = []
    for nhansu in csp_result.cac_nhansu:
        total_hours = 0
        for task_id, assignment in csp_result.assignment.items():
            if assignment.nhansu.id == nhansu.id:
                task = next(t for t in csp_result.cac_tacvu if t.id == task_id)
                total_hours += task.duration
        workloads.append(total_hours)
    
    if not workloads:
        return 0.0
    
    # Tính độ lệch chuẩn
    if len(workloads) > 1:
        std_dev = statistics.stdev(workloads)
    else:
        std_dev = 0.0
    
    return std_dev


def calculate_load_balance_score(csp_result) -> float:
    """
    Tính điểm cân bằng tải (Load Balance Score)
    Điểm càng cao = cân bằng càng tốt
    """
    if not csp_result.assignment:
        return 0.0
    
    # Tính workload cho mỗi nhân viên
    workloads = []
    for nhansu in csp_result.cac_nhansu:
        total_hours = 0
        for task_id, assignment in csp_result.assignment.items():
            if assignment.nhansu.id == nhansu.id:
                task = next(t for t in csp_result.cac_tacvu if t.id == task_id)
                total_hours += task.duration
        workloads.append(total_hours)
    
    if not workloads:
        return 0.0
    
    # Tính độ lệch chuẩn
    if len(workloads) > 1:
        std_dev = statistics.stdev(workloads)
    else:
        std_dev = 0.0
    
    # Chuyển đổi thành điểm: độ lệch càng nhỏ = điểm càng cao
    # Công thức: score = 1 / (1 + std_dev)
    score = 1.0 / (1.0 + std_dev)
    return score


def calculate_priority_score(csp_result) -> float:
    """
    Tính điểm ưu tiên (Priority Score)
    Ưu tiên các tác vụ có độ ưu tiên cao được thực hiện sớm
    """
    if not csp_result.assignment:
        return 0.0
    
    total_score = 0.0
    project_duration = (csp_result.project_end_date - csp_result.project_start_date).total_seconds()
    
    for task_id, assignment in csp_result.assignment.items():
        task = next(t for t in csp_result.cac_tacvu if t.id == task_id)
        
        # Tính thời điểm bắt đầu chuẩn hóa (0 = bắt đầu dự án, 1 = kết thúc dự án)
        time_elapsed = (assignment.start_time - csp_result.project_start_date).total_seconds()
        normalized_time = time_elapsed / project_duration if project_duration > 0 else 0
        
        # Tác vụ ưu tiên cao thực hiện sớm → điểm cao
        task_score = task.priority * (1.0 - normalized_time)
        total_score += task_score
    
    # Chuẩn hóa điểm (chia cho tổng priority của tất cả tác vụ)
    total_priority = sum(t.priority for t in csp_result.cac_tacvu)
    normalized_score = total_score / total_priority if total_priority > 0 else 0
    
    return normalized_score


def run_single_experiment(dataset_folder: str, project_start_date: datetime, 
                         project_end_date: datetime, model_name: str) -> Dict:
    """
    Chạy một lần thực nghiệm với một mô hình
    
    Returns:
        Dictionary chứa các metrics
    """
    start_time = time.time()
    
    if model_name == "Baseline":
        result = baseline.solve_csp(dataset_folder, project_start_date, project_end_date)
        backtrack_count = 0  # Baseline không track
        ac3_pruned = 0
        fc_pruned = 0
    else:  # Advanced
        result = advanced.solve_csp(dataset_folder, project_start_date, project_end_date)
        backtrack_count = result.backtrack_count
        ac3_pruned = result.ac3_pruned_count
        fc_pruned = result.fc_pruned_count
    
    runtime = time.time() - start_time
    
    # Tính các metrics
    makespan = calculate_makespan(result) if result.solution_found else 0.0
    constraint_satisfaction = calculate_constraint_satisfaction(result) if result.solution_found else 0.0
    workload_std = calculate_workload_std_dev(result) if result.solution_found else 0.0
    
    # Tính ràng buộc mềm (chỉ cho Advanced khi có solution)
    load_balance_score = 0.0
    priority_score = 0.0
    if result.solution_found:
        load_balance_score = calculate_load_balance_score(result)
        priority_score = calculate_priority_score(result)
    
    return {
        'runtime': runtime,
        'makespan': makespan,
        'constraint_satisfaction': constraint_satisfaction,
        'workload_std_dev': workload_std,
        'solution_found': result.solution_found,
        'backtrack_count': backtrack_count,
        'ac3_pruned': ac3_pruned,
        'fc_pruned': fc_pruned,
        'load_balance_score': load_balance_score,
        'priority_score': priority_score
    }


def run_experiments(dataset_folder: str, num_runs: int = 1) -> Tuple[List[Dict], List[Dict]]:
    """
    Chạy thực nghiệm nhiều lần cho cả Baseline và Advanced
    
    Args:
        dataset_folder: Đường dẫn đến dataset
        num_runs: Số lần chạy (mặc định 15)
    
    Returns:
        Tuple (baseline_results, advanced_results)
    """
    # Thiết lập thời gian dự án
    project_start_date = datetime(2024, 1, 1, 8, 0, 0)  # 01/01/2024 08:00
    project_end_date = datetime(2024, 1, 31, 17, 0, 0)  # 31/01/2024 17:00
    
    baseline_results = []
    advanced_results = []
    
    print("=" * 70)
    print("BẮT ĐẦU THỰC NGHIỆM")
    print("=" * 70)
    print(f"Dataset: {dataset_folder}")
    print(f"Số lần chạy: {num_runs}")
    if num_runs == 1:
        print("Lưu ý: CSP là deterministic → kết quả giống nhau mỗi lần chạy")
        print("       Chỉ cần chạy 1 lần để lấy kết quả.")
    else:
        print("Lưu ý: Chạy nhiều lần chỉ để tính trung bình runtime (có thể dao động).")
    print(f"Thời gian dự án: {project_start_date.strftime('%d/%m/%Y')} - {project_end_date.strftime('%d/%m/%Y')}")
    print("=" * 70)
    print()
    
    # Chạy Baseline
    print("Đang chạy Baseline model...")
    for i in range(num_runs):
        print(f"  Lần {i+1}/{num_runs}...", end=" ", flush=True)
        result = run_single_experiment(dataset_folder, project_start_date, project_end_date, "Baseline")
        baseline_results.append(result)
        status = "✓" if result['solution_found'] else "✗"
        print(f"{status} ({result['runtime']:.4f}s)")
    
    print()
    
    # Chạy Advanced
    print("Đang chạy Advanced model...")
    for i in range(num_runs):
        print(f"  Lần {i+1}/{num_runs}...", end=" ", flush=True)
        result = run_single_experiment(dataset_folder, project_start_date, project_end_date, "Advanced")
        advanced_results.append(result)
        status = "✓" if result['solution_found'] else "✗"
        print(f"{status} ({result['runtime']:.4f}s)")
    
    print()
    return baseline_results, advanced_results


def calculate_statistics(results: List[Dict]) -> Dict:
    """
    Tính toán thống kê từ danh sách kết quả
    
    Returns:
        Dictionary chứa mean, std_dev, min, max cho mỗi metric
    """
    if not results:
        return {}
    
    stats = {}
    
    # Lọc các metrics số
    metrics = ['runtime', 'makespan', 'constraint_satisfaction', 'workload_std_dev', 
               'backtrack_count', 'ac3_pruned', 'fc_pruned', 'load_balance_score', 'priority_score']
    
    for metric in metrics:
        values = [r[metric] for r in results if metric in r]
        if values:
            stats[f'{metric}_mean'] = statistics.mean(values)
            stats[f'{metric}_std'] = statistics.stdev(values) if len(values) > 1 else 0.0
            stats[f'{metric}_min'] = min(values)
            stats[f'{metric}_max'] = max(values)
    
    # Success rate
    success_count = sum(1 for r in results if r.get('solution_found', False))
    stats['success_rate'] = (success_count / len(results)) * 100.0
    stats['success_count'] = success_count
    stats['total_runs'] = len(results)
    
    return stats


def export_to_excel(baseline_stats: Dict, advanced_stats: Dict, 
                    baseline_results: List[Dict], advanced_results: List[Dict],
                    output_file: str = "experiment_results.xlsx"):
    """
    Xuất kết quả ra file Excel với nhiều sheet
    """
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Tổng quan thống kê
        summary_data = {
            'Metric': [
                'Thời gian chạy (s)',
                'Makespan (ngày)',
                '% Ràng buộc thỏa mãn',
                'Độ lệch chuẩn Workload',
                'Load Balance Score',
                'Priority Score',
                'Số lần Backtrack',
                'AC-3 Pruned',
                'Forward Checking Pruned',
                'Success Rate (%)'
            ],
            'Baseline (Mean ± Std)': [
                f"{baseline_stats.get('runtime_mean', 0):.4f} ± {baseline_stats.get('runtime_std', 0):.4f}",
                f"{baseline_stats.get('makespan_mean', 0):.2f} ± {baseline_stats.get('makespan_std', 0):.2f}",
                f"{baseline_stats.get('constraint_satisfaction_mean', 0):.2f} ± {baseline_stats.get('constraint_satisfaction_std', 0):.2f}",
                f"{baseline_stats.get('workload_std_dev_mean', 0):.2f} ± {baseline_stats.get('workload_std_dev_std', 0):.2f}",
                f"{baseline_stats.get('load_balance_score_mean', 0):.4f} ± {baseline_stats.get('load_balance_score_std', 0):.4f}",
                f"{baseline_stats.get('priority_score_mean', 0):.4f} ± {baseline_stats.get('priority_score_std', 0):.4f}",
                f"{baseline_stats.get('backtrack_count_mean', 0):.0f} ± {baseline_stats.get('backtrack_count_std', 0):.0f}",
                f"{baseline_stats.get('ac3_pruned_mean', 0):.0f} ± {baseline_stats.get('ac3_pruned_std', 0):.0f}",
                f"{baseline_stats.get('fc_pruned_mean', 0):.0f} ± {baseline_stats.get('fc_pruned_std', 0):.0f}",
                f"{baseline_stats.get('success_rate', 0):.1f}%"
            ],
            'Advanced (Mean ± Std)': [
                f"{advanced_stats.get('runtime_mean', 0):.4f} ± {advanced_stats.get('runtime_std', 0):.4f}",
                f"{advanced_stats.get('makespan_mean', 0):.2f} ± {advanced_stats.get('makespan_std', 0):.2f}",
                f"{advanced_stats.get('constraint_satisfaction_mean', 0):.2f} ± {advanced_stats.get('constraint_satisfaction_std', 0):.2f}",
                f"{advanced_stats.get('workload_std_dev_mean', 0):.2f} ± {advanced_stats.get('workload_std_dev_std', 0):.2f}",
                f"{advanced_stats.get('load_balance_score_mean', 0):.4f} ± {advanced_stats.get('load_balance_score_std', 0):.4f}",
                f"{advanced_stats.get('priority_score_mean', 0):.4f} ± {advanced_stats.get('priority_score_std', 0):.4f}",
                f"{advanced_stats.get('backtrack_count_mean', 0):.0f} ± {advanced_stats.get('backtrack_count_std', 0):.0f}",
                f"{advanced_stats.get('ac3_pruned_mean', 0):.0f} ± {advanced_stats.get('ac3_pruned_std', 0):.0f}",
                f"{advanced_stats.get('fc_pruned_mean', 0):.0f} ± {advanced_stats.get('fc_pruned_std', 0):.0f}",
                f"{advanced_stats.get('success_rate', 0):.1f}%"
            ],
            'Cải thiện': [
                f"{(1 - advanced_stats.get('runtime_mean', 1) / max(baseline_stats.get('runtime_mean', 1), 0.0001)) * 100:.1f}%" if baseline_stats.get('runtime_mean', 0) > 0 else "N/A",
                f"{(1 - advanced_stats.get('makespan_mean', 1) / max(baseline_stats.get('makespan_mean', 1), 0.0001)) * 100:.1f}%" if baseline_stats.get('makespan_mean', 0) > 0 else "N/A",
                f"{(advanced_stats.get('constraint_satisfaction_mean', 0) - baseline_stats.get('constraint_satisfaction_mean', 0)):.1f}%" if baseline_stats.get('constraint_satisfaction_mean', 0) > 0 else "N/A",
                f"{(1 - advanced_stats.get('workload_std_dev_mean', 1) / max(baseline_stats.get('workload_std_dev_mean', 1), 0.0001)) * 100:.1f}%" if baseline_stats.get('workload_std_dev_mean', 0) > 0 else "N/A",
                f"{(advanced_stats.get('load_balance_score_mean', 0) - baseline_stats.get('load_balance_score_mean', 0)):.4f}" if baseline_stats.get('load_balance_score_mean', 0) > 0 else "N/A",
                f"{(advanced_stats.get('priority_score_mean', 0) - baseline_stats.get('priority_score_mean', 0)):.4f}" if baseline_stats.get('priority_score_mean', 0) > 0 else "N/A",
                "N/A",
                "N/A",
                "N/A",
                f"{(advanced_stats.get('success_rate', 0) - baseline_stats.get('success_rate', 0)):.1f}%" if baseline_stats.get('success_rate', 0) > 0 else "N/A"
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Tổng quan', index=False)
        
        # Sheet 2: Chi tiết Baseline
        df_baseline = pd.DataFrame(baseline_results)
        df_baseline.to_excel(writer, sheet_name='Baseline Chi tiết', index=False)
        
        # Sheet 3: Chi tiết Advanced
        df_advanced = pd.DataFrame(advanced_results)
        df_advanced.to_excel(writer, sheet_name='Advanced Chi tiết', index=False)
        
        # Sheet 4: Thống kê Baseline
        baseline_stats_df = pd.DataFrame([baseline_stats]).T
        baseline_stats_df.columns = ['Giá trị']
        baseline_stats_df.to_excel(writer, sheet_name='Baseline Thống kê')
        
        # Sheet 5: Thống kê Advanced
        advanced_stats_df = pd.DataFrame([advanced_stats]).T
        advanced_stats_df.columns = ['Giá trị']
        advanced_stats_df.to_excel(writer, sheet_name='Advanced Thống kê')
    
    print(f"\n✓ Kết quả đã được xuất ra file: {output_file}")


def print_summary(baseline_stats: Dict, advanced_stats: Dict):
    """In tóm tắt kết quả ra console"""
    print("\n" + "=" * 70)
    print("TÓM TẮT KẾT QUẢ THỰC NGHIỆM")
    print("=" * 70)
    
    print("\n📊 BASELINE MODEL:")
    print(f"  Thời gian chạy:     {baseline_stats.get('runtime_mean', 0):.4f} ± {baseline_stats.get('runtime_std', 0):.4f} giây")
    print(f"  Makespan:           {baseline_stats.get('makespan_mean', 0):.2f} ± {baseline_stats.get('makespan_std', 0):.2f} ngày")
    print(f"  % Ràng buộc:        {baseline_stats.get('constraint_satisfaction_mean', 0):.2f} ± {baseline_stats.get('constraint_satisfaction_std', 0):.2f}%")
    print(f"  Workload Std Dev:   {baseline_stats.get('workload_std_dev_mean', 0):.2f} ± {baseline_stats.get('workload_std_dev_std', 0):.2f}")
    print(f"  Success Rate:       {baseline_stats.get('success_rate', 0):.1f}% ({baseline_stats.get('success_count', 0)}/{baseline_stats.get('total_runs', 0)})")
    
    print("\n🚀 ADVANCED MODEL:")
    print(f"  Thời gian chạy:     {advanced_stats.get('runtime_mean', 0):.4f} ± {advanced_stats.get('runtime_std', 0):.4f} giây")
    print(f"  Makespan:           {advanced_stats.get('makespan_mean', 0):.2f} ± {advanced_stats.get('makespan_std', 0):.2f} ngày")
    print(f"  % Ràng buộc:        {advanced_stats.get('constraint_satisfaction_mean', 0):.2f} ± {advanced_stats.get('constraint_satisfaction_std', 0):.2f}%")
    print(f"  Workload Std Dev:   {advanced_stats.get('workload_std_dev_mean', 0):.2f} ± {advanced_stats.get('workload_std_dev_std', 0):.2f}")
    print(f"  Load Balance Score: {advanced_stats.get('load_balance_score_mean', 0):.4f} ± {advanced_stats.get('load_balance_score_std', 0):.4f}")
    print(f"  Priority Score:     {advanced_stats.get('priority_score_mean', 0):.4f} ± {advanced_stats.get('priority_score_std', 0):.4f}")
    print(f"  Số lần Backtrack:   {advanced_stats.get('backtrack_count_mean', 0):.0f} ± {advanced_stats.get('backtrack_count_std', 0):.0f}")
    print(f"  AC-3 Pruned:         {advanced_stats.get('ac3_pruned_mean', 0):.0f} ± {advanced_stats.get('ac3_pruned_std', 0):.0f}")
    print(f"  FC Pruned:           {advanced_stats.get('fc_pruned_mean', 0):.0f} ± {advanced_stats.get('fc_pruned_std', 0):.0f}")
    print(f"  Success Rate:       {advanced_stats.get('success_rate', 0):.1f}% ({advanced_stats.get('success_count', 0)}/{advanced_stats.get('total_runs', 0)})")
    
    # Tính cải thiện
    if baseline_stats.get('runtime_mean', 0) > 0:
        speedup = baseline_stats.get('runtime_mean', 1) / max(advanced_stats.get('runtime_mean', 0.0001), 0.0001)
        print(f"\n⚡ CẢI THIỆN:")
        print(f"  Tốc độ:             {speedup:.2f}x nhanh hơn")
        if baseline_stats.get('makespan_mean', 0) > 0:
            makespan_improvement = (1 - advanced_stats.get('makespan_mean', 1) / baseline_stats.get('makespan_mean', 1)) * 100
            print(f"  Makespan:           {makespan_improvement:.1f}% tốt hơn")
        constraint_improvement = advanced_stats.get('constraint_satisfaction_mean', 0) - baseline_stats.get('constraint_satisfaction_mean', 0)
        print(f"  % Ràng buộc:        +{constraint_improvement:.1f}%")
        
        workload_improvement = (1 - advanced_stats.get('workload_std_dev_mean', 1) / max(baseline_stats.get('workload_std_dev_mean', 1), 0.0001)) * 100
        print(f"  Workload cân bằng:  {workload_improvement:.1f}% tốt hơn")
    
    # Phân tích hiệu quả kỹ thuật (chỉ khi chạy 1 lần hoặc có dữ liệu)
    print(f"\n📈 PHÂN TÍCH HIỆU QUẢ KỸ THUẬT (Advanced Model):")
    ac3_pruned = advanced_stats.get('ac3_pruned_mean', 0)
    fc_pruned = advanced_stats.get('fc_pruned_mean', 0)
    backtrack = advanced_stats.get('backtrack_count_mean', 0)
    load_balance_score = advanced_stats.get('load_balance_score_mean', 0)
    priority_score = advanced_stats.get('priority_score_mean', 0)
    
    print(f"  AC-3 đã cắt tỉa:     {ac3_pruned:.0f} giá trị không khả thi")
    print(f"  Forward Checking:    {fc_pruned:.0f} giá trị bị loại bỏ")
    print(f"  Số lần Backtrack:    {backtrack:.0f} lần")
    print(f"  Load Balance Score:  {load_balance_score:.4f}")
    print(f"  Priority Score:      {priority_score:.4f}")
    
    if backtrack == 0:
        print(f"  → Tìm được lời giải ngay từ đầu, không cần backtrack!")
    elif backtrack < 5:
        print(f"  → Rất ít backtrack, thuật toán hiệu quả cao")
    else:
        print(f"  → Cần {backtrack:.0f} lần backtrack để tìm lời giải")
    
    print("=" * 70)


def plot_runtime_per_trial(baseline_results: List[Dict], advanced_results: List[Dict], 
                           output_file: str = "runtime_per_trial.png"):
    """
    Vẽ biểu đồ line graph cho runtime theo từng trial
    """
    trials = list(range(1, len(baseline_results) + 1))
    baseline_runtimes = [r['runtime'] for r in baseline_results]
    advanced_runtimes = [r['runtime'] for r in advanced_results]
    
    plt.figure(figsize=(12, 6))
    plt.plot(trials, baseline_runtimes, 'o-', label='Baseline', color='#1f77b4', linewidth=2, markersize=6)
    plt.plot(trials, advanced_runtimes, 'o-', label='Advanced', color='#ff7f0e', linewidth=2, markersize=6)
    
    plt.xlabel('Trial', fontsize=12, fontweight='bold')
    plt.ylabel('Runtime (seconds)', fontsize=12, fontweight='bold')
    plt.title('Runtime per Trial', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Đã lưu biểu đồ: {output_file}")
    plt.close()


def plot_average_comparison(baseline_stats: Dict, advanced_stats: Dict,
                           output_file: str = "average_comparison.png"):
    """
    Vẽ biểu đồ bar chart so sánh trung bình các metrics
    Style giống gui_app.py
    """
    fig = plt.figure(figsize=(12, 8))
    
    categories = ['Baseline', 'Advanced']
    colors = ['#e74c3c', '#27ae60']  # Đỏ cho Baseline, Xanh lá cho Advanced (giống gui_app.py)
    
    # 1. Makespan
    ax1 = fig.add_subplot(2, 2, 1)
    makespan_values = [
        baseline_stats.get('makespan_mean', 0),
        advanced_stats.get('makespan_mean', 0)
    ]
    bars1 = ax1.bar(categories, makespan_values, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Ngày', fontsize=10)
    ax1.set_title('Thời Gian Hoàn Thành Dự Án\n(Makespan - Càng thấp càng tốt)', 
                 fontsize=11, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Thêm giá trị lên cột
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f} ngày', ha='center', va='bottom', fontsize=9)
    
    # 2. % Ràng Buộc Thỏa
    ax2 = fig.add_subplot(2, 2, 2)
    constraint_values = [
        baseline_stats.get('constraint_satisfaction_mean', 0),
        advanced_stats.get('constraint_satisfaction_mean', 0)
    ]
    bars2 = ax2.bar(categories, constraint_values, color=colors, alpha=0.7, edgecolor='black')
    ax2.set_ylabel('%', fontsize=10)
    ax2.set_title('% Ràng Buộc Thỏa\n(Càng cao càng tốt)', 
                 fontsize=11, fontweight='bold')
    ax2.set_ylim([0, 105])
    ax2.grid(axis='y', alpha=0.3)
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # 3. Độ Lệch Chuẩn Workload
    ax3 = fig.add_subplot(2, 2, 3)
    workload_std_values = [
        baseline_stats.get('workload_std_dev_mean', 0),
        advanced_stats.get('workload_std_dev_mean', 0)
    ]
    bars3 = ax3.bar(categories, workload_std_values, color=colors, alpha=0.7, edgecolor='black')
    ax3.set_ylabel('Giờ', fontsize=10)
    ax3.set_title('Độ Lệch Chuẩn Workload\n(Càng thấp càng tốt)', 
                 fontsize=11, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    # 4. Thời Gian Chạy
    ax4 = fig.add_subplot(2, 2, 4)
    time_values = [
        baseline_stats.get('runtime_mean', 0),
        advanced_stats.get('runtime_mean', 0)
    ]
    bars4 = ax4.bar(categories, time_values, color=colors, alpha=0.7, edgecolor='black')
    ax4.set_ylabel('Giây', fontsize=10)
    ax4.set_title('Thời Gian Chạy\n(Càng thấp càng tốt)', 
                 fontsize=11, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    
    for bar in bars4:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}s', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Đã lưu biểu đồ: {output_file}")
    plt.close()


def plot_all_charts(baseline_results: List[Dict], advanced_results: List[Dict],
                   baseline_stats: Dict, advanced_stats: Dict):
    """
    Vẽ tất cả các biểu đồ
    """
    print("\nĐang vẽ biểu đồ...")
    
    # 1. Runtime per trial (line graph) - chỉ vẽ nếu có nhiều hơn 1 lần chạy
    if len(baseline_results) > 1:
        plot_runtime_per_trial(baseline_results, advanced_results, "runtime_per_trial.png")
    else:
        print("  (Bỏ qua runtime_per_trial vì chỉ chạy 1 lần)")
    
    # 2. Average comparison (bar chart)
    plot_average_comparison(baseline_stats, advanced_stats, "average_comparison.png")
    
    print("✓ Hoàn thành vẽ biểu đồ!")


def main():
    """Hàm chính"""
    print("=" * 70)
    print("HỆ THỐNG THỰC NGHIỆM - SO SÁNH BASELINE VÀ ADVANCED MODEL")
    print("=" * 70)
    print()
    
    # Chọn dataset
    dataset_folder = "datasets/medium_project"
    
    # Số lần chạy - CSP là deterministic nên kết quả giống nhau
    # Chỉ cần chạy nhiều lần nếu muốn tính trung bình runtime (có thể dao động do hệ thống)
    # Mặc định chạy 1 lần vì kết quả giống nhau
    num_runs = 1
    
    print(f"Dataset: {dataset_folder}")
    print(f"Số lần chạy mỗi mô hình: {num_runs}")
    print("Lưu ý: CSP là deterministic, kết quả sẽ giống nhau mỗi lần chạy.")
    print("       Chỉ cần chạy nhiều lần nếu muốn tính trung bình runtime.")
    print()
    
    # Chạy thực nghiệm
    baseline_results, advanced_results = run_experiments(dataset_folder, num_runs)
    
    # Tính toán thống kê
    print("Đang tính toán thống kê...")
    baseline_stats = calculate_statistics(baseline_results)
    advanced_stats = calculate_statistics(advanced_results)
    
    # In tóm tắt
    print_summary(baseline_stats, advanced_stats)
    
    # Xuất ra Excel
    output_file = "experiment_results_medium_project.xlsx"
    export_to_excel(baseline_stats, advanced_stats, baseline_results, advanced_results, output_file)
    
    # Vẽ biểu đồ
    plot_all_charts(baseline_results, advanced_results, baseline_stats, advanced_stats)
    
    print("\n✓ Hoàn thành thực nghiệm!")


if __name__ == "__main__":
    main()

