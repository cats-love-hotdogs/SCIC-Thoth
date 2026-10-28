"""
exam_log.py - Quản lý nhật ký và lịch sử các đề thi đã tạo.
Lưu giữ mã câu hỏi đã sử dụng để thuật toán tự động tránh trùng lặp.
Toàn bộ việc ghi log mặc định thực hiện trong ICSC_CLI/logs để không can thiệp bên ngoài.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from .. import config


def read_all_logs() -> List[Dict[str, Any]]:
    """
    Đọc toàn bộ lịch sử tạo đề.
    Kết hợp cả log gốc của dự án (chỉ đọc) và log mới trong ICSC_CLI.
    """
    entries = []

    # 1. Đọc từ root log nếu có (read-only)
    if config.ROOT_LOG_FILE.exists():
        try:
            with open(config.ROOT_LOG_FILE, "r", encoding="utf-8") as f:
                root_data = json.load(f)
                if isinstance(root_data, list):
                    entries.extend(root_data)
        except Exception:
            pass

    # 2. Đọc từ CLI log (ưu tiên ghi mới vào đây)
    if config.CLI_LOG_FILE.exists():
        try:
            with open(config.CLI_LOG_FILE, "r", encoding="utf-8") as f:
                cli_data = json.load(f)
                if isinstance(cli_data, list):
                    # Tránh trùng lặp entry dựa trên timestamp và subject
                    existing_keys = {
                        (e.get("timestamp"), e.get("subject")) for e in entries
                    }
                    for e in cli_data:
                        k = (e.get("timestamp"), e.get("subject"))
                        if k not in existing_keys:
                            entries.append(e)
        except Exception:
            pass

    # Sắp xếp theo thời gian mới nhất trước
    entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return entries


def write_log(exam_entry: Dict[str, Any]) -> None:
    """
    Ghi một mục đề thi mới vào log của ICSC_CLI.
    """
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    current_logs = []
    if config.CLI_LOG_FILE.exists():
        try:
            with open(config.CLI_LOG_FILE, "r", encoding="utf-8") as f:
                current_logs = json.load(f)
        except Exception:
            current_logs = []

    current_logs.append(exam_entry)
    # Giới hạn số lượng
    current_logs = current_logs[-config.LOG_HISTORY_SIZE :]

    try:
        with open(config.CLI_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(current_logs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  [Lỗi ghi log] {e}")


def create_log_entry(
    subject: str,
    exam_type: str,
    question_codes: List[str],
    exam_code: str = "",
    pdf_path: str = "",
    tex_path: str = "",
) -> Dict[str, Any]:
    """Tạo dict biểu diễn một đề thi trong lịch sử."""
    return {
        "subject": subject,
        "exam_type": exam_type,
        "exam_code": exam_code,
        "question_codes": question_codes,
        "question_count": len(question_codes),
        "pdf_path": str(pdf_path) if pdf_path else "",
        "tex_path": str(tex_path) if tex_path else "",
        "timestamp": datetime.now().isoformat(),
    }


def get_used_question_codes(subject_folder: str) -> Dict[str, int]:
    """
    Lấy dict các mã câu hỏi đã sử dụng cho môn học kèm mức độ ưu tiên tránh trùng lặp.
    Trả về dict: question_code -> recency (recency = 0: đề mới nhất).
    """
    all_logs = read_all_logs()
    # Lọc theo môn học
    subject_logs = [e for e in all_logs if e.get("subject") == subject_folder]
    # Lấy tối đa LOG_HISTORY_SIZE đề gần nhất
    recent_logs = subject_logs[: config.LOG_HISTORY_SIZE]

    used_codes: Dict[str, int] = {}
    for recency, entry in enumerate(recent_logs):
        for code in entry.get("question_codes", []):
            if code and code not in used_codes:
                used_codes[code] = recency

    return used_codes
