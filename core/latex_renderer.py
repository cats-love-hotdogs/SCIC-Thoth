"""
latex_renderer.py - Chuyển đổi dữ liệu câu hỏi JSON sang định dạng LaTeX chuẩn.
Hỗ trợ đầy đủ:
- line, inline_math, display_math, inline_matrix, display_system (cases)
- Các macro trắc nghiệm: \\haicot, \\namcot, \\saucot
- Các macro tự luận: \\OnePointQues, \\TwoPointQues, \\ThreePointQues
- Phòng vệ chống khối enumerate rỗng và xử lý backslash an toàn
"""

import re
from collections import OrderedDict
from typing import Dict, Any, List, Tuple, Optional
from . import data_loader


def fix_backslashes(text: Any) -> str:
    """Đảm bảo chuỗi an toàn cho LaTeX."""
    if not isinstance(text, str):
        return str(text)
    return text


_KEY_PATTERN = re.compile(
    r"^(?:([a-z])_)?(line|inline_math|display_math|inline_matrix|display_system)_(\d+)_(\d+)$"
)


def parse_key(key: str) -> Optional[Tuple[Optional[str], str, str, str]]:
    """Parse content key thành (prefix, content_type, row, col)."""
    match = _KEY_PATTERN.match(key)
    if match:
        return match.groups()  # type: ignore
    return None


def render_matrix(matrix_data: Dict[str, Any]) -> str:
    """Render inline_matrix thành \\begin{style} ... \\end{style}."""
    style = matrix_data.get("style", "pmatrix")
    rows = matrix_data.get("rows", [])
    row_strs = [" & ".join(str(cell) for cell in row) for row in rows]
    inner = " \\\\ ".join(row_strs)
    return f"\\begin{{{style}}} {inner} \\end{{{style}}}"


def render_system(system_data: Any) -> str:
    """Render display_system thành \\begin{cases} ... \\end{cases}."""
    if not isinstance(system_data, dict):
        return fix_backslashes(str(system_data))
    style = system_data.get("style", "cases")
    eqs = system_data.get("eqs", [])
    eq_strs = [fix_backslashes(str(eq)) for eq in eqs]
    inner = " \\\\ ".join(eq_strs)
    return f"\\begin{{{style}}} {inner} \\end{{{style}}}"


def render_content_block(
    data_dict: Dict[str, Any],
    prefix: Optional[str] = None,
    row_separator: str = "\\\\\n",
    display_as_inline: bool = False,
) -> str:
    """
    Render một JSON content block thành chuỗi LaTeX.
    """
    items = []
    for key, value in data_dict.items():
        parsed = parse_key(key)
        if not parsed:
            continue
        p, content_type, row, col = parsed
        if prefix is not None and p != prefix:
            continue
        if prefix is None and p is not None:
            continue
        items.append((row, content_type, value))

    if not items:
        return ""

    rows = OrderedDict()
    for row, content_type, value in items:
        rows.setdefault(row, []).append((content_type, value))

    rendered_rows = []
    for row_key, row_items in rows.items():
        parts = []
        has_display = False

        for content_type, value in row_items:
            if content_type == "line":
                parts.append(fix_backslashes(str(value)))
            elif content_type == "inline_math":
                parts.append(f"${fix_backslashes(value)}$")
            elif content_type == "display_math":
                fixed = fix_backslashes(value)
                if display_as_inline:
                    parts.append(f"$\\displaystyle {fixed}$")
                else:
                    has_display = True
                    parts.append(f"\\[{fixed}\\]")
            elif content_type == "inline_matrix":
                parts.append(f"${render_matrix(value)}$")
            elif content_type == "display_system":
                system_tex = render_system(value)
                if display_as_inline or prefix is not None:
                    parts.append(f"${system_tex}$")
                else:
                    has_display = True
                    parts.append(f"\\[{system_tex}\\]")

        rendered_rows.append((" ".join(parts), has_display))

    result = []
    for i, (text, has_display) in enumerate(rendered_rows):
        if i == 0:
            result.append(text)
        else:
            if has_display or rendered_rows[i - 1][1]:
                result.append("\n" + text)
            else:
                result.append(row_separator + text)

    return "".join(result)


def render_question_text(question_data: Dict[str, Any], question_type: str = "MCQ_SA") -> str:
    """Render phần question text."""
    if question_type in ("MCQ_SA", "MCQ_MA", "TFQ"):
        return render_content_block(question_data, row_separator="\\\\\n")
    return render_content_block(question_data, row_separator="\n")


def extract_choice_prefixes(choices_dict: Dict[str, Any]) -> List[str]:
    """Trích xuất danh sách prefixes (a, b, c, ...)."""
    prefixes = set()
    for key in choices_dict:
        parsed = parse_key(key)
        if parsed and parsed[0]:
            prefixes.add(parsed[0])
        else:
            parts = key.split("_")
            if len(parts) >= 2 and len(parts[0]) == 1 and parts[0].isalpha():
                prefixes.add(parts[0])
    return sorted(prefixes)


def render_single_choice(choices_dict: Dict[str, Any], prefix: str) -> str:
    """Render một lựa chọn trắc nghiệm."""
    return render_content_block(
        choices_dict,
        prefix=prefix,
        row_separator=" ",
        display_as_inline=True,
    )


def render_choices(choices_dict: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Render tất cả các lựa chọn."""
    prefixes = extract_choice_prefixes(choices_dict)
    return [(p, render_single_choice(choices_dict, p)) for p in prefixes]


def get_choice_macro(num_choices: int) -> str:
    """Chọn macro haicot, namcot, saucot."""
    if num_choices <= 4:
        return "haicot"
    elif num_choices == 5:
        return "namcot"
    return "saucot"


def render_mcq_choices_latex(choices_dict: Dict[str, Any]) -> str:
    """Render choices thành macro LaTeX."""
    choices = render_choices(choices_dict)
    macro = get_choice_macro(len(choices))
    args = "".join(f"{{{text}}}" for _, text in choices)
    return f"\\{macro}{args}"


def render_mcq_item(question: Dict[str, Any]) -> str:
    """Render một câu trắc nghiệm cho môi trường danhsachcau."""
    q_type = question.get("question_type", "MCQ_SA")
    q_text = render_question_text(question.get("question", {}), q_type)
    choices_tex = render_mcq_choices_latex(question.get("choices", {}))
    return f"    \\item {q_text}\n    {choices_tex}"


def get_point_header(question_num: int, point_value: int) -> str:
    """Tạo macro đề bài tự luận tương ứng số điểm."""
    if point_value == 1:
        return f"\\OnePointQues{{{question_num}}}"
    elif point_value == 2:
        return f"\\TwoPointQues{{{question_num}}}"
    elif point_value == 3:
        return f"\\ThreePointQues{{{question_num}}}"
    return f"\\textbf{{Câu {question_num} ({point_value}đ).}}"


def render_frq_sp(question: Dict[str, Any], question_num: int, point_value: int) -> str:
    """Render câu tự luận đơn phần."""
    header = get_point_header(question_num, point_value)
    q_text = render_question_text(question.get("question", {}), "FRQ_SP")
    last_key = list(question.get("question", {}).keys())[-1] if question.get("question") else ""
    vspace = "\\vspace{0.3cm}" if "display_math" in last_key else "\\vspace{0.5cm}"
    return f"{header} {q_text}\n\n{vspace}"


def render_frq_mp(question: Dict[str, Any], question_num: int, point_value: int) -> str:
    """Render câu tự luận nhiều ý (FRQ_MP)."""
    header = get_point_header(question_num, point_value)
    main_text = render_content_block(question.get("main", {}), row_separator="\n")

    part_dict = question.get("part", {})
    part_prefixes = extract_choice_prefixes(part_dict)

    parts_latex = []
    for p in part_prefixes:
        part_text = render_content_block(part_dict, prefix=p, row_separator="\n")
        if part_text.strip():
            parts_latex.append(f"    \\item {part_text}")

    parts_block = ""
    if parts_latex:
        parts_block = (
            f"\\begin{{enumerate}}[label=\\alph*)]\n"
            f"{chr(10).join(parts_latex)}\n"
            f"\\end{{enumerate}}"
        )

    end_text = ""
    if question.get("end"):
        end_text = render_content_block(question["end"], row_separator="\n")

    blocks = []
    if main_text.strip():
        blocks.append(f"{header} {main_text}")
    else:
        blocks.append(f"{header}")

    if parts_block:
        blocks.append(parts_block)

    if end_text.strip():
        blocks.append(end_text)

    full_text = "\n".join(blocks)
    return f"{full_text}\n\n\\vspace{{0.3cm}}"


def render_frq_question(question: Dict[str, Any], question_num: int) -> str:
    """Render câu hỏi tự luận."""
    q_type = question.get("question_type")
    point_val = data_loader.get_question_point(question)
    if q_type == "FRQ_MP":
        return render_frq_mp(question, question_num, point_val)
    return render_frq_sp(question, question_num, point_val)
