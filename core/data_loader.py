"""
data_loader.py - Tải và phân tích dữ liệu câu hỏi từ kho sorted JSON.
Hỗ trợ bộ nhớ đệm (caching), thống kê kho câu hỏi, tính điểm chuẩn và các bộ lọc đa dạng.
"""

import json
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from .. import config

# Bộ nhớ đệm dữ liệu môn học
_CACHE: Dict[str, Dict[int, List[Dict[str, Any]]]] = {}


def clear_cache() -> None:
    """Xóa bộ nhớ đệm."""
    _CACHE.clear()


def get_available_chapters(subject_folder: str) -> List[int]:
    """
    Lấy danh sách các chapter có sẵn cho một môn học.
    """
    folder = config.SORTED_DIR / subject_folder
    if not folder.exists():
        return []

    chapters = []
    for filepath in sorted(folder.glob("chapter_*.json")):
        basename = filepath.name
        try:
            num = int(basename.replace("chapter_", "").replace(".json", ""))
            chapters.append(num)
        except ValueError:
            continue
    return sorted(chapters)


def load_chapter(subject_folder: str, chapter_num: int) -> List[Dict[str, Any]]:
    """
    Tải câu hỏi từ một chapter cụ thể.
    """
    if subject_folder not in _CACHE:
        _CACHE[subject_folder] = {}

    if chapter_num in _CACHE[subject_folder]:
        return _CACHE[subject_folder][chapter_num]

    filepath = config.SORTED_DIR / subject_folder / f"chapter_{chapter_num}.json"
    if not filepath.exists():
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            _CACHE[subject_folder][chapter_num] = data
            return data
    except Exception as e:
        print(f"  [Lỗi đọc file] {filepath}: {e}")
        return []


def load_chapters(subject_folder: str, chapter_nums: List[int]) -> List[Dict[str, Any]]:
    """
    Tải câu hỏi từ danh sách chapters.
    """
    questions = []
    for num in chapter_nums:
        questions.extend(load_chapter(subject_folder, num))
    return questions


def load_all_chapters(subject_folder: str) -> List[Dict[str, Any]]:
    """
    Tải toàn bộ câu hỏi của môn học.
    """
    chapters = get_available_chapters(subject_folder)
    return load_chapters(subject_folder, chapters)


def get_question_point(question: Dict[str, Any]) -> int:
    """
    Tính số điểm của một câu hỏi theo quy tắc chuẩn:
    - Nếu có trường 'point' trong JSON: lấy giá trị int(point).
    - Nếu 'point' is None:
      + Với FRQ_MP (tự luận nhiều ý): số điểm = số ý (hoặc mặc định 2 điểm).
      + Với các câu khác: mặc định 1 điểm.
    """
    p = question.get("point")
    if p is not None:
        try:
            return int(p)
        except (ValueError, TypeError):
            pass

    q_type = question.get("question_type", "")
    if q_type == "FRQ_MP":
        parts = question.get("parts", [])
        if parts:
            return len(parts)
        return 2

    return 1


def filter_by_types(questions: List[Dict[str, Any]], types: Set[str]) -> List[Dict[str, Any]]:
    """Lọc câu hỏi theo loại."""
    return [q for q in questions if q.get("question_type") in types]


def filter_exclude_types(questions: List[Dict[str, Any]], types: Set[str]) -> List[Dict[str, Any]]:
    """Lọc loại trừ các loại câu hỏi."""
    return [q for q in questions if q.get("question_type") not in types]


def filter_by_tags(questions: List[Dict[str, Any]], tags: Set[str]) -> List[Dict[str, Any]]:
    """Lọc các câu hỏi chứa ít nhất một tag trong tập tags."""
    return [q for q in questions if set(q.get("section_tags", [])) & tags]


def filter_frq_mp_max_parts(questions: List[Dict[str, Any]], max_parts: int = 2) -> List[Dict[str, Any]]:
    """
    Lọc các câu FRQ_MP: chỉ giữ lại các câu có tối đa max_parts ý con.
    Các loại câu khác giữ nguyên.
    """
    result = []
    for q in questions:
        if q.get("question_type") == "FRQ_MP":
            parts = q.get("parts", [])
            if len(parts) <= max_parts:
                result.append(q)
        else:
            result.append(q)
    return result


def get_stats_summary() -> Dict[str, Any]:
    """
    Thống kê tổng quan ngân hàng câu hỏi trên toàn bộ các môn học.
    """
    summary = {
        "total_questions": 0,
        "subjects": {},
        "type_counts": {
            "MCQ_SA": 0,
            "MCQ_MA": 0,
            "TFQ": 0,
            "FRQ_SP": 0,
            "FRQ_MP": 0,
            "OTHER": 0,
        },
    }

    for s_key, s_info in config.SUBJECTS.items():
        folder = s_info["folder"]
        chapters = get_available_chapters(folder)
        all_q = load_all_chapters(folder)

        s_stats = {
            "display_name": s_info["display_name"],
            "vn_name": s_info["vn_name"],
            "folder": folder,
            "chapters": chapters,
            "total": len(all_q),
            "mcq_sa": 0,
            "mcq_ma": 0,
            "tfq": 0,
            "frq_sp": 0,
            "frq_mp": 0,
            "other": 0,
        }

        for q in all_q:
            t = q.get("question_type", "OTHER")
            if t == "MCQ_SA":
                s_stats["mcq_sa"] += 1
                summary["type_counts"]["MCQ_SA"] += 1
            elif t == "MCQ_MA":
                s_stats["mcq_ma"] += 1
                summary["type_counts"]["MCQ_MA"] += 1
            elif t == "TFQ":
                s_stats["tfq"] += 1
                summary["type_counts"]["TFQ"] += 1
            elif t == "FRQ_SP":
                s_stats["frq_sp"] += 1
                summary["type_counts"]["FRQ_SP"] += 1
            elif t == "FRQ_MP":
                s_stats["frq_mp"] += 1
                summary["type_counts"]["FRQ_MP"] += 1
            else:
                s_stats["other"] += 1
                summary["type_counts"]["OTHER"] += 1

        summary["total_questions"] += len(all_q)
        summary["subjects"][folder] = s_stats

    return summary
