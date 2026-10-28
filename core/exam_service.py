"""
exam_service.py - Dịch vụ điều phối tạo đề thi (Giữa kỳ, Cuối kỳ, Tự luyện).
Tự động sao chép template styles (thoth.sty), biên dịch PDF, ghi log và trả về kết quả chi tiết.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from .. import config
from . import data_loader
from . import question_selector
from . import latex_renderer
from . import latex_compiler
from . import exam_log


def _ensure_output_dir(subject_folder: str, exam_type: str, exam_code: str) -> Path:
    """Tạo thư mục con cho đề thi và trả về đường dẫn."""
    out_root = config.get_output_dir()
    clean_code = str(exam_code).replace(" ", "_")
    sub_folder = f"{subject_folder}_{exam_type}_{clean_code}"
    target_dir = out_root / sub_folder
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def _copy_template_style(dest_dir: Path, exam_type: str) -> None:
    """Sao chép file thoth.sty tương ứng vào thư mục đề thi (hỗ trợ nhiều cấp fallback)."""
    target_sty = dest_dir / "thoth.sty"
    candidates = []
    if exam_type == "midterm":
        candidates.append(config.TEMPLATE_MIDTERM_DIR / "thoth.sty")
    elif exam_type == "final":
        candidates.append(config.TEMPLATE_FINAL_DIR / "thoth.sty")
    elif exam_type == "practice":
        candidates.append(config.TEMPLATE_PRACTICE_DIR / "thoth.sty")

    candidates.append(config.TEMPLATES_DIR / exam_type / "thoth.sty")
    candidates.append(config.TEMPLATES_DIR / "thoth.sty")
    folder_term = exam_type if exam_type != "final" else "final_term"
    candidates.append(config.PROJECT_ROOT / f"template_{folder_term}" / "thoth.sty")

    for c in candidates:
        if c.exists():
            shutil.copy2(c, target_sty)
            return


def generate_midterm(
    subject_folder: str,
    exam_code: str = "102",
    auto_compile: bool = True,
    progress_callback: Optional[Callable[[str, float], None]] = None,
) -> Dict[str, Any]:
    """
    Tạo đề thi giữa kỳ (Midterm).
    15 câu trắc nghiệm: 10 MCQ_SA + 5 TFQ/MCQ_MA.
    """
    if progress_callback:
        progress_callback("Kiểm tra cấu hình môn học...", 0.1)

    subj_info = config.SUBJECT_BY_FOLDER.get(subject_folder)
    if not subj_info:
        return {"success": False, "error": f"Không tìm thấy môn học: {subject_folder}"}

    chapters = subj_info.get("default_midterm_chapters", [1])
    if progress_callback:
        progress_callback(f"Tải câu hỏi các chương giữa kỳ: {chapters}...", 0.2)

    all_questions = data_loader.load_chapters(subject_folder, chapters)
    if not all_questions:
        return {"success": False, "error": f"Không tìm thấy câu hỏi nào cho môn {subject_folder}!"}

    mcq_sa_pool = data_loader.filter_by_types(all_questions, {"MCQ_SA"})
    part2_pool = data_loader.filter_by_types(all_questions, {"TFQ", "MCQ_MA"})

    if len(mcq_sa_pool) < config.MIDTERM_PART1_COUNT or len(part2_pool) < config.MIDTERM_PART2_COUNT:
        # Cảnh báo thiếu câu hỏi nhưng vẫn cố gắng chọn tối đa
        pass

    if progress_callback:
        progress_callback("Lựa chọn câu hỏi tối ưu độ phủ kiến thức...", 0.4)

    used_codes = exam_log.get_used_question_codes(subject_folder)
    part1_selected = question_selector.select_questions_greedy(
        mcq_sa_pool, config.MIDTERM_PART1_COUNT, subject_folder, used_codes
    )
    part2_selected = question_selector.select_questions_greedy(
        part2_pool, config.MIDTERM_PART2_COUNT, subject_folder, used_codes
    )

    all_selected = part1_selected + part2_selected
    if not all_selected:
        return {"success": False, "error": "Không thể chọn được câu hỏi nào!"}

    if progress_callback:
        progress_callback("Render nội dung sang LaTeX...", 0.6)

    # Render Part I
    content_blocks = []
    if part1_selected:
        part1_items = [latex_renderer.render_mcq_item(q) for q in part1_selected]
        part1_content = "\n\n".join(part1_items)
        content_blocks.append(f"\\PartOne\n\n\\begin{{danhsachcau}}\n{part1_content}\n\\end{{danhsachcau}}")

    # Render Part II
    if part2_selected:
        part2_items = [latex_renderer.render_mcq_item(q) for q in part2_selected]
        part2_content = "\n\n".join(part2_items)
        part2_start = len(part1_selected) + 1
        start_opt = f"[start={part2_start}]" if part1_selected else ""
        content_blocks.append(f"\\PartTwo\n\n\\begin{{danhsachcau}}{start_opt}\n{part2_content}\n\\end{{danhsachcau}}")

    body_content = "\n\n".join(content_blocks)
    latex_cmd = subj_info["latex_cmd"]
    latex_code = subj_info["latex_code"]
    total_count = len(all_selected)

    latex_code_content = rf"""\documentclass[11pt,a4paper]{{extarticle}}
\usepackage[utf8]{{vietnam}}
\usepackage{{graphicx}}
\usepackage{{xcolor}}
\usepackage{{amsmath, amssymb, amsfonts}}
\usepackage{{geometry}}
\usepackage{{enumitem}}
\usepackage{{fancyhdr}}
\usepackage{{array}}
\usepackage{{tabularx}}
\usepackage{{lastpage}}
\usepackage{{thoth}}

\geometry{{
    a4paper,
    left=1.45cm,
    right=1.45cm,
    top=1.4cm,
    bottom=1.6cm,
    headheight=15pt,
    headsep=10pt,
    footskip=20pt
}}

\pagestyle{{fancy}}
\fancyhf{{}}
\renewcommand{{\headrulewidth}}{{0pt}}
\fancyfoot[R]{{\small Trang \thepage/\pageref{{LastPage}}}}

\begin{{document}}

\Heading{{{latex_cmd}}}{{{latex_code}}}

\Header{{{exam_code}}}{{{total_count}}}

{body_content}

\end{{document}}
"""

    target_dir = _ensure_output_dir(subject_folder, "midterm", exam_code)
    tex_path = target_dir / f"midterm_{subject_folder}_{exam_code}.tex"
    tex_path.write_text(latex_code_content, encoding="utf-8")

    # Copy thoth.sty
    _copy_template_style(target_dir, "midterm")

    # Ghi log
    all_codes = [q.get("question_code", "") for q in all_selected]
    log_entry = exam_log.create_log_entry(
        subject=subject_folder,
        exam_type="midterm",
        question_codes=all_codes,
        exam_code=exam_code,
        tex_path=str(tex_path),
    )

    pdf_path = None
    if auto_compile:
        if progress_callback:
            progress_callback("Biên dịch mã LaTeX thành file PDF...", 0.8)
        pdf_path = latex_compiler.compile_latex(tex_path)
        if pdf_path:
            log_entry["pdf_path"] = str(pdf_path)

    exam_log.write_log(log_entry)

    if progress_callback:
        progress_callback("Hoàn tất tạo đề!", 1.0)

    covered_tags = set()
    for q in all_selected:
        covered_tags.update(q.get("section_tags", []))

    return {
        "success": True,
        "subject": subject_folder,
        "exam_type": "midterm",
        "exam_code": exam_code,
        "tex_path": tex_path,
        "pdf_path": pdf_path,
        "questions": all_selected,
        "part1_count": len(part1_selected),
        "part2_count": len(part2_selected),
        "total_count": total_count,
        "covered_tags": sorted(list(covered_tags)),
    }


def generate_final(
    subject_folder: str,
    exam_code: str = "1",
    auto_compile: bool = True,
    progress_callback: Optional[Callable[[str, float], None]] = None,
) -> Dict[str, Any]:
    """
    Tạo đề thi cuối kỳ (Final).
    Tự luận chuẩn 10 điểm, tỷ lệ câu 1 điểm >= 50%, FRQ_MP tối đa 2 ý.
    """
    if progress_callback:
        progress_callback("Tải câu hỏi môn học...", 0.1)

    subj_info = config.SUBJECT_BY_FOLDER.get(subject_folder)
    if not subj_info:
        return {"success": False, "error": f"Không tìm thấy môn học: {subject_folder}"}

    all_questions = data_loader.load_all_chapters(subject_folder)
    if not all_questions:
        return {"success": False, "error": f"Không có câu hỏi nào cho môn {subject_folder}!"}

    if progress_callback:
        progress_callback("Lọc câu tự luận chuẩn (FRQ_SP, FRQ_MP ≤ 2 ý)...", 0.3)

    frq_pool = data_loader.filter_exclude_types(all_questions, config.MCQ_TYPES)
    frq_pool = data_loader.filter_frq_mp_max_parts(frq_pool, max_parts=config.FINAL_MAX_FRQ_MP_PARTS)

    if not frq_pool:
        return {"success": False, "error": "Không có câu hỏi tự luận nào phù hợp quy cách!"}

    if progress_callback:
        progress_callback("Thuật toán chọn tổ hợp câu hỏi chuẩn 10 điểm...", 0.5)

    used_codes = exam_log.get_used_question_codes(subject_folder)
    selected = question_selector.select_questions_by_points(
        frq_pool, total_points=config.FINAL_TOTAL_POINTS, subject_folder=subject_folder, used_codes=used_codes
    )

    if not selected:
        return {"success": False, "error": "Không chọn được tổ hợp câu hỏi thỏa mãn 10 điểm!"}

    if progress_callback:
        progress_callback("Render LaTeX cho đề tự luận...", 0.7)

    question_blocks = []
    for i, q in enumerate(selected, 1):
        block = latex_renderer.render_frq_question(q, i)
        question_blocks.append(block)
    questions_content = "\n".join(question_blocks)

    latex_cmd = subj_info["latex_cmd"]
    latex_code = subj_info["latex_code"]

    latex_code_content = rf"""\documentclass[14pt, a4paper]{{extarticle}}
\usepackage[utf8]{{vietnam}}
\usepackage{{graphicx}}
\usepackage{{xcolor}}
\usepackage{{color}}
\usepackage{{mathptmx}}
\usepackage{{amsmath, amssymb, amsfonts}}
\usepackage{{geometry}}
\usepackage{{float}}
\usepackage{{enumitem}}
\usepackage{{indentfirst}}
\usepackage{{fancyhdr}}
\usepackage{{thoth}}

\geometry{{
    left=2cm,
    right=2cm,
    top=1.5cm,
    bottom=2cm
}}

\pagestyle{{empty}}

\begin{{document}}

\Header{{{exam_code}}}

\vspace{{2pt}}
\noindent\rule{{\textwidth}}{{0.5pt}}

\Heading{{{latex_cmd}}}{{{latex_code}}}

{questions_content}

\end{{document}}
"""

    target_dir = _ensure_output_dir(subject_folder, "final", exam_code)
    tex_path = target_dir / f"final_{subject_folder}_{exam_code}.tex"
    tex_path.write_text(latex_code_content, encoding="utf-8")

    # Copy thoth.sty
    _copy_template_style(target_dir, "final")

    all_codes = [q.get("question_code", "") for q in selected]
    log_entry = exam_log.create_log_entry(
        subject=subject_folder,
        exam_type="final",
        question_codes=all_codes,
        exam_code=exam_code,
        tex_path=str(tex_path),
    )

    pdf_path = None
    if auto_compile:
        if progress_callback:
            progress_callback("Biên dịch LaTeX sang PDF...", 0.85)
        pdf_path = latex_compiler.compile_latex(tex_path)
        if pdf_path:
            log_entry["pdf_path"] = str(pdf_path)

    exam_log.write_log(log_entry)

    if progress_callback:
        progress_callback("Hoàn tất tạo đề!", 1.0)

    total_points = sum(data_loader.get_question_point(q) for q in selected)
    covered_tags = set()
    for q in selected:
        covered_tags.update(q.get("section_tags", []))

    return {
        "success": True,
        "subject": subject_folder,
        "exam_type": "final",
        "exam_code": exam_code,
        "tex_path": tex_path,
        "pdf_path": pdf_path,
        "questions": selected,
        "total_count": len(selected),
        "total_points": total_points,
        "covered_tags": sorted(list(covered_tags)),
    }


def generate_practice(
    subject_folder: str,
    selected_tags: Optional[List[str]] = None,
    count: Optional[int] = None,
    exam_code: str = "PRACTICE",
    auto_compile: bool = True,
    progress_callback: Optional[Callable[[str, float], None]] = None,
) -> Dict[str, Any]:
    """
    Tạo đề thi tự luyện (Practice).
    Lọc theo tags hoặc chương, tự do tùy chọn số lượng câu.
    """
    if progress_callback:
        progress_callback("Tải câu hỏi môn học...", 0.1)

    subj_info = config.SUBJECT_BY_FOLDER.get(subject_folder)
    if not subj_info:
        return {"success": False, "error": f"Không tìm thấy môn học: {subject_folder}"}

    all_questions = data_loader.load_all_chapters(subject_folder)
    if not all_questions:
        return {"success": False, "error": f"Không có câu hỏi nào cho môn {subject_folder}!"}

    filtered = all_questions
    if selected_tags:
        filtered = data_loader.filter_by_tags(all_questions, set(selected_tags))
        if not filtered:
            return {"success": False, "error": "Không tìm thấy câu hỏi nào chứa các tags đã chọn!"}

    if count and count < len(filtered):
        if progress_callback:
            progress_callback(f"Chọn {count} câu hỏi tối ưu...", 0.3)
        selected = question_selector.select_questions_greedy(filtered, count, subject_folder)
    else:
        selected = filtered[:]

    # Phân chia Phần 1 (MCQ) và Phần 2 (FRQ)
    part1 = []
    part2 = []
    _PART1_ORDER = {"MCQ_SA": 0, "MCQ_MA": 1, "TFQ": 2}

    for q in selected:
        t = q.get("question_type", "")
        if t in _PART1_ORDER:
            part1.append(q)
        else:
            part2.append(q)

    part1.sort(key=lambda q: _PART1_ORDER.get(q.get("question_type", ""), 99))
    part2.sort(key=lambda q: data_loader.get_question_point(q))

    if progress_callback:
        progress_callback("Render nội dung đề tự luyện...", 0.6)

    content_blocks = []
    if part1:
        content_blocks.append("\\noindent\\textbf{PHẦN I. TRẮC NGHIỆM}\\par\\vspace{6pt}")
        mcq_items = [latex_renderer.render_mcq_item(q) for q in part1]
        mcq_content = "\n\n".join(mcq_items)
        content_blocks.append(f"\\begin{{danhsachcau}}\n{mcq_content}\n\\end{{danhsachcau}}")

    if part2:
        content_blocks.append("\\noindent\\textbf{PHẦN II. TỰ LUẬN}\\par\\vspace{6pt}")
        start_idx = len(part1) + 1
        for i, q in enumerate(part2, start_idx):
            content_blocks.append(latex_renderer.render_frq_question(q, i))

    body_content = "\n\n\\vspace{0.5cm}\n\n".join(content_blocks)
    latex_cmd = subj_info["latex_cmd"]
    latex_code = subj_info["latex_code"]
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    latex_code_content = rf"""\documentclass[11pt,a4paper]{{extarticle}}
\usepackage[utf8]{{vietnam}}
\usepackage{{graphicx}}
\usepackage{{xcolor}}
\usepackage{{amsmath, amssymb, amsfonts}}
\usepackage{{geometry}}
\usepackage{{enumitem}}
\usepackage{{fancyhdr}}
\usepackage{{array}}
\usepackage{{tabularx}}
\usepackage{{lastpage}}
\usepackage{{thoth}}

\geometry{{
    a4paper,
    left=1.45cm,
    right=1.45cm,
    top=1.4cm,
    bottom=1.6cm,
    headheight=15pt,
    headsep=10pt,
    footskip=20pt
}}

\pagestyle{{fancy}}
\fancyhf{{}}
\renewcommand{{\headrulewidth}}{{0pt}}
\fancyfoot[R]{{\small Trang \thepage/\pageref{{LastPage}}}}

\begin{{document}}

\Heading{{{latex_cmd}}}{{{latex_code}}}

\begin{{center}}
\Large\textbf{{BỘ CÂU HỎI ÔN TẬP TỰ LUYỆN}}
\end{{center}}

\vspace{{6pt}}

{body_content}

\end{{document}}
"""

    target_dir = _ensure_output_dir(subject_folder, "practice", timestamp_str)
    tex_path = target_dir / f"practice_{subject_folder}_{timestamp_str}.tex"
    tex_path.write_text(latex_code_content, encoding="utf-8")

    # Copy thoth.sty
    _copy_template_style(target_dir, "practice")

    all_codes = [q.get("question_code", "") for q in selected]
    log_entry = exam_log.create_log_entry(
        subject=subject_folder,
        exam_type="practice",
        question_codes=all_codes,
        exam_code="PRACTICE",
        tex_path=str(tex_path),
    )

    pdf_path = None
    if auto_compile:
        if progress_callback:
            progress_callback("Biên dịch LaTeX sang PDF...", 0.85)
        pdf_path = latex_compiler.compile_latex(tex_path)
        if pdf_path:
            log_entry["pdf_path"] = str(pdf_path)

    exam_log.write_log(log_entry)

    if progress_callback:
        progress_callback("Hoàn tất tạo đề tự luyện!", 1.0)

    covered_tags = set()
    for q in selected:
        covered_tags.update(q.get("section_tags", []))

    return {
        "success": True,
        "subject": subject_folder,
        "exam_type": "practice",
        "exam_code": "PRACTICE",
        "tex_path": tex_path,
        "pdf_path": pdf_path,
        "questions": selected,
        "part1_count": len(part1),
        "part2_count": len(part2),
        "total_count": len(selected),
        "covered_tags": sorted(list(covered_tags)),
    }
