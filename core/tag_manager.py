"""
tag_manager.py - Phân tích và quản lý ma trận kiến thức & Tags từ resource/tags_01_v2.md.
Hỗ trợ ánh xạ tag prefix sang chapter, đếm số lượng câu hỏi phủ mỗi tag và độ bao phủ.
"""

import re
from typing import Dict, Any, List, Set, Optional
from pathlib import Path
from .. import config

_TAGS_REF_CACHE: Optional[Dict[str, List[Dict[str, Any]]]] = None


def parse_tags_reference() -> Dict[str, List[Dict[str, Any]]]:
    """Parse file tags_01_v2.md để lấy cây cấu trúc chương và tags chuẩn."""
    if not config.TAGS_FILE.exists():
        return {}

    try:
        content = config.TAGS_FILE.read_text(encoding="utf-8")
    except Exception:
        return {}

    result: Dict[str, List[Dict[str, Any]]] = {}
    current_subject = None
    current_chapter = None
    current_tags = []

    for line in content.split("\n"):
        line = line.strip()

        if line.startswith("## Part I: Calculus 1"):
            if current_subject and current_chapter:
                result[current_subject].append({
                    "chapter": current_chapter,
                    "tags": current_tags,
                })
            current_subject = "calculus_1"
            result[current_subject] = []
            current_chapter = None
            current_tags = []

        elif line.startswith("## Part II: Algebra"):
            if current_subject and current_chapter:
                result[current_subject].append({
                    "chapter": current_chapter,
                    "tags": current_tags,
                })
            current_subject = "algebra"
            result[current_subject] = []
            current_chapter = None
            current_tags = []

        elif line.startswith("### Chapter"):
            if current_subject and current_chapter:
                result[current_subject].append({
                    "chapter": current_chapter,
                    "tags": current_tags,
                })
                current_tags = []
            current_chapter = line.lstrip("#").strip()

        elif line.startswith("|") and "`c" in line:
            match = re.search(r"`(c\d+_\w+)`", line)
            if match:
                tag_code = match.group(1)
                # Lấy mô tả tiếng Việt nếu có trong bảng
                cols = [c.strip() for c in line.split("|") if c.strip()]
                desc = cols[1] if len(cols) >= 2 else tag_code
                current_tags.append({"tag": tag_code, "desc": desc})

    # Flush chapter cuối cùng
    if current_subject and current_chapter:
        result[current_subject].append({
            "chapter": current_chapter,
            "tags": current_tags,
        })

    return result


def get_tags_reference() -> Dict[str, List[Dict[str, Any]]]:
    """Lấy cấu trúc tham chiếu chapters & tags có caching."""
    global _TAGS_REF_CACHE
    if _TAGS_REF_CACHE is None:
        _TAGS_REF_CACHE = parse_tags_reference()
    return _TAGS_REF_CACHE


def count_questions_per_tag(questions: List[Dict[str, Any]]) -> Dict[str, int]:
    """Đếm số câu hỏi chứa mỗi tag."""
    counts: Dict[str, int] = {}
    for q in questions:
        for t in q.get("section_tags", []):
            counts[t] = counts.get(t, 0) + 1
    return counts


def get_tag_coverage_stats(subject_folder: str, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tính độ phủ kiến thức (Tag coverage) của môn học:
    Tổng số tags chuẩn, số tags đã có câu hỏi, số tags còn thiếu.
    """
    ref = get_tags_reference().get(subject_folder, [])
    counts = count_questions_per_tag(questions)

    all_standard_tags = []
    for ch in ref:
        for item in ch.get("tags", []):
            t = item["tag"] if isinstance(item, dict) else item
            all_standard_tags.append(t)

    covered_tags = [t for t in all_standard_tags if counts.get(t, 0) > 0]
    missing_tags = [t for t in all_standard_tags if counts.get(t, 0) == 0]

    return {
        "total_tags": len(all_standard_tags),
        "covered_tags_count": len(covered_tags),
        "missing_tags_count": len(missing_tags),
        "coverage_rate": (len(covered_tags) / len(all_standard_tags) * 100) if all_standard_tags else 0.0,
        "counts": counts,
        "missing_tags": missing_tags,
    }
