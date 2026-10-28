"""
question_selector.py - Thuật toán chọn câu hỏi thông minh cho đề thi.
Tối đa hóa độ phủ kiến thức (Tag coverage) bằng thuật toán Greedy,
kết hợp cơ chế Deduplication tránh trùng lặp câu hỏi của các đề gần nhất.
"""

import random
from typing import List, Dict, Any, Optional, Set
from . import data_loader
from . import exam_log


def _get_question_tags(question: Dict[str, Any]) -> Set[str]:
    """Lấy tập section_tags của câu hỏi."""
    return set(question.get("section_tags", []))


def _get_point(question: Dict[str, Any]) -> int:
    """Lấy số điểm chuẩn của câu hỏi."""
    return data_loader.get_question_point(question)


def select_questions_greedy(
    questions: List[Dict[str, Any]],
    count: int,
    subject_folder: str = "",
    used_codes: Optional[Dict[str, int]] = None,
) -> List[Dict[str, Any]]:
    """
    Chọn câu hỏi bằng thuật toán tham lam (Greedy) tối đa hóa độ phủ tags.

    Quy trình:
    1. Tách pool thành Fresh (chưa từng dùng) và Stale (đã dùng trong lịch sử).
    2. Sắp xếp Stale theo thứ tự từ đề cũ nhất đến mới nhất.
    3. Greedy: Mỗi bước chọn câu đóng góp nhiều tags MỚI nhất chưa được phủ.
    4. Nếu Fresh hết câu mà chưa đủ số lượng -> Fallback sang Stale (lấy từ đề cũ nhất).
    """
    if not questions:
        return []

    if count >= len(questions):
        return questions[:]

    if used_codes is None:
        used_codes = exam_log.get_used_question_codes(subject_folder) if subject_folder else {}

    fresh = []
    stale = []
    for q in questions:
        code = q.get("question_code", "")
        if code in used_codes:
            stale.append((q, used_codes[code]))
        else:
            fresh.append(q)

    # Sắp xếp Stale theo recency giảm dần (đề cũ nhất trước)
    stale.sort(key=lambda x: -x[1])

    selected = []
    covered_tags: Set[str] = set()

    def _greedy_pick(pool: List[Dict[str, Any]]) -> int:
        best_idx = -1
        best_score = -1
        for i, q in enumerate(pool):
            q_tags = _get_question_tags(q)
            new_tags = q_tags - covered_tags
            score = len(new_tags)
            if score > best_score:
                best_score = score
                best_idx = i
            elif score == best_score and score > 0:
                if random.random() < 0.5:
                    best_idx = i
        return best_idx

    # Giai đoạn 1: Lấy từ fresh pool
    rem_fresh = fresh[:]
    while len(selected) < count and rem_fresh:
        best_i = _greedy_pick(rem_fresh)
        if best_i == -1:
            # Các câu còn lại không thêm tag mới -> bốc ngẫu nhiên
            best_i = random.randrange(len(rem_fresh))
        chosen = rem_fresh.pop(best_i)
        selected.append(chosen)
        covered_tags.update(_get_question_tags(chosen))

    # Giai đoạn 2: Lấy từ stale pool nếu chưa đủ số lượng
    rem_stale = [q for q, _ in stale]
    while len(selected) < count and rem_stale:
        best_i = _greedy_pick(rem_stale)
        if best_i == -1:
            best_i = 0
        chosen = rem_stale.pop(best_i)
        selected.append(chosen)
        covered_tags.update(_get_question_tags(chosen))

    return selected


def select_questions_by_points(
    questions: List[Dict[str, Any]],
    total_points: int = 10,
    subject_folder: str = "",
    used_codes: Optional[Dict[str, int]] = None,
) -> List[Dict[str, Any]]:
    """
    Chọn câu hỏi tự luận cho đề cuối kỳ đảm bảo:
    1. Tổng số điểm CHÍNH XÁC bằng total_points (mặc định 10 điểm).
    2. Tỷ lệ câu 1 điểm chiếm không dưới 50% tổng số câu.
    3. Tối đa hóa độ phủ tags kiến thức.
    """
    if not questions:
        return []

    if used_codes is None:
        used_codes = exam_log.get_used_question_codes(subject_folder) if subject_folder else {}

    # Phân loại câu theo điểm
    q_by_point: Dict[int, List[Dict[str, Any]]] = {}
    for q in questions:
        pt = _get_point(q)
        q_by_point.setdefault(pt, []).append(q)

    # Thử các phân phối điểm hợp lệ cho tổng 10:
    # Ví dụ: (8 câu 1đ, 1 câu 2đ), (6 câu 1đ, 2 câu 2đ), (4 câu 1đ, 3 câu 2đ)...
    candidates_combos = []
    # (num_1pt, num_2pt, num_3pt)
    for c3 in range(2):
        for c2 in range(5):
            rem = total_points - (c3 * 3 + c2 * 2)
            if rem >= 0:
                c1 = rem
                total_q = c1 + c2 + c3
                # Đảm bảo câu 1đ chiếm ít nhất 50% tổng số câu
                if total_q > 0 and (c1 / total_q) >= 0.5:
                    candidates_combos.append((c1, c2, c3))

    # Ưu tiên các combo có nhiều câu 1 điểm và ít câu 3 điểm
    candidates_combos.sort(key=lambda c: (-c[0], c[2]))

    for c1, c2, c3 in candidates_combos:
        avail_1 = len(q_by_point.get(1, []))
        avail_2 = len(q_by_point.get(2, []))
        avail_3 = len(q_by_point.get(3, []))

        if avail_1 >= c1 and avail_2 >= c2 and avail_3 >= c3:
            # Chọn từng nhóm bằng greedy
            sel_1 = select_questions_greedy(q_by_point.get(1, []), c1, subject_folder, used_codes)
            sel_2 = select_questions_greedy(q_by_point.get(2, []), c2, subject_folder, used_codes)
            sel_3 = select_questions_greedy(q_by_point.get(3, []), c3, subject_folder, used_codes)

            result = sel_1 + sel_2 + sel_3
            # Xáo trộn nhẹ để đề tự nhiên
            random.shuffle(result)
            return result

    # Nếu không thể đáp ứng ràng buộc 50%, fallback về greedy theo điểm tổng
    selected = []
    current_pts = 0
    # Xếp theo điểm nhỏ trước
    sorted_q = sorted(questions, key=lambda q: _get_point(q))
    for q in sorted_q:
        pt = _get_point(q)
        if current_pts + pt <= total_points:
            selected.append(q)
            current_pts += pt
        if current_pts == total_points:
            break

    return selected
