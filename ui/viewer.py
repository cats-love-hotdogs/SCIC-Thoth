"""
viewer.py - Trình hiển thị và xem trước câu hỏi toán học trên terminal với định dạng LaTeX trực quan.
Hỗ trợ đầy đủ:
- Trắc nghiệm (MCQ_SA, MCQ_MA, TFQ): Đề bài + phương án [A], [B], [C], [D]
- Tự luận đơn (FRQ_SP): Đề bài hoàn chỉnh
- Tự luận nhiều ý (FRQ_MP): Main text + các ý con (a), (b), (c)... + End text
- Làm sạch và làm nổi bật công thức LaTeX trên terminal
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from . import colors
from . import terminal
from . import components
from ..core import latex_renderer
from ..core import data_loader


def clean_latex_math_for_terminal(math_str: str) -> str:
    """Chuyển đổi công thức LaTeX thành chuỗi ký tự Unicode dễ đọc trên Terminal."""
    if not math_str:
        return ""

    s = math_str.strip()
    # Loại bỏ cặp dấu $ hoặc \[ \]
    if s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("\\[") and s.endswith("\\]"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()

    # Xử lý cases environment
    if "\\begin{cases}" in s:
        s = s.replace("\\begin{cases}", "").replace("\\end{cases}", "")
        cases_lines = [l.strip() for l in s.split("\\\\") if l.strip()]
        cleaned_cases = []
        for cl in cases_lines:
            cl = cl.replace("&", "   ")
            cl = re.sub(r"\\text\{([^}]+)\}", r"\1", cl)
            cleaned_cases.append(cl)
        s = " { " + " ;  ".join(cleaned_cases) + " }"

    # Xử lý \frac{A}{B}
    s = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"(\1)/(\2)", s)
    # Xử lý \sqrt{A}
    s = re.sub(r"\\sqrt\{([^}]+)\}", r"√(\1)", s)
    s = re.sub(r"\\sqrt", r"√", s)

    # Ký tự Hy Lạp thông dụng
    greek_map = {
        "\\varphi": "φ", "\\phi": "φ", "\\alpha": "α", "\\beta": "β",
        "\\gamma": "γ", "\\delta": "δ", "\\theta": "θ", "\\lambda": "λ",
        "\\mu": "μ", "\\pi": "π", "\\sigma": "σ", "\\omega": "ω",
    }
    for k, v in greek_map.items():
        s = s.replace(k, v)

    # Toán tử & Ký hiệu
    symbols_map = {
        "\\to": "→", "\\rightarrow": "→", "\\infty": "∞",
        "\\neq": "≠", "\\ne": "≠", "\\leq": "≤", "\\le": "≤",
        "\\geq": "≥", "\\ge": "≥", "\\pm": "±", "\\times": "×",
        "\\cdot": "·", "\\in": "∈", "\\notin": "∉", "\\subset": "⊂",
        "\\cup": "∪", "\\cap": "∩", "\\int": "∫", "\\partial": "∂",
    }
    for k, v in symbols_map.items():
        s = s.replace(k, v)

    # Các hàm toán học
    s = s.replace("\\arcsin", "arcsin").replace("\\arccos", "arccos").replace("\\arctan", "arctan")
    s = s.replace("\\sin", "sin").replace("\\cos", "cos").replace("\\tan", "tan").replace("\\cot", "cot")
    s = s.replace("\\ln", "ln").replace("\\log", "log").replace("\\lim", "lim").replace("\\exp", "exp")

    # Bỏ các macro format
    s = s.replace("\\displaystyle", "").replace("\\left", "").replace("\\right", "")
    s = re.sub(r"\\text\{([^}]+)\}", r"\1", s)
    s = re.sub(r"\\mathrm\{([^}]+)\}", r"\1", s)
    s = re.sub(r"\\mathbf\{([^}]+)\}", r"\1", s)

    # Lũy thừa thông dụng
    s = s.replace("^2", "²").replace("^3", "³").replace("^{2}", "²").replace("^{3}", "³")

    # Dọn dẹp backslash thừa
    s = re.sub(r"\\[a-zA-Z]+", "", s)
    s = s.replace("\\", "")

    return " ".join(s.split())


def render_math_terminal(text: str) -> str:
    """Làm nổi bật và định dạng công thức LaTeX trong đoạn văn bản."""
    if not text:
        return ""

    def highlight_display_math(match):
        inner = match.group(1)
        pretty = clean_latex_math_for_terminal(inner)
        return "\n      " + colors.colorize(f" {pretty} ", "bright_yellow", bold=True) + "\n"

    def highlight_inline_math(match):
        inner = match.group(1)
        pretty = clean_latex_math_for_terminal(inner)
        return colors.colorize(f" {pretty} ", "bright_yellow", bold=True)

    # Thay thế display math \[ ... \] hoặc $$ ... $$
    text = re.sub(r"\\\[(.*?)\\\]", highlight_display_math, text, flags=re.DOTALL)
    text = re.sub(r"\$\$(.*?)\$\$", highlight_display_math, text, flags=re.DOTALL)
    # Thay thế inline math $ ... $
    text = re.sub(r"\$([^\$]+)\$", highlight_inline_math, text)

    return text


def _extract_question_body(question: Dict[str, Any]) -> str:
    """Trích xuất nội dung văn bản đề bài từ các định dạng dữ liệu khác nhau."""
    # 1. Trường 'question' là dictionary (chuẩn của hệ thống)
    if "question" in question and isinstance(question["question"], dict):
        tex = latex_renderer.render_content_block(question["question"], row_separator="\n")
        return tex

    # 2. Trường 'main' (với câu FRQ_MP)
    if "main" in question and isinstance(question["main"], dict):
        tex = latex_renderer.render_content_block(question["main"], row_separator="\n")
        return tex

    # 3. Fallback trường 'statement'
    if "statement" in question and isinstance(question["statement"], str):
        return question["statement"]

    return ""


def render_question_detail(question: Dict[str, Any], index: Optional[int] = None, width: Optional[int] = None) -> str:
    """
    Render toàn bộ chi tiết câu hỏi thành một khung trực quan đẹp mắt.
    """
    if width is None:
        width = terminal.get_terminal_width()

    code = question.get("question_code", "N/A")
    q_type = question.get("question_type", "UNKNOWN")
    point_val = data_loader.get_question_point(question)
    tags = question.get("section_tags", [])

    # Header & Badges
    q_title = f"CÂU HỎI #{index}" if index is not None else "CHI TIẾT CÂU HỎI"
    type_badge = colors.badge(q_type, bg_color="magenta", fg_color="white")
    point_badge = colors.badge(f"{point_val} Điểm", bg_color="blue", fg_color="white")

    lines = []
    lines.append(f"  {colors.colorize('Mã câu hỏi:', 'gray')} {colors.colorize(code, 'bright_cyan', bold=True)}   {type_badge}   {point_badge}")
    tag_str = " ".join([colors.colorize(f"#{t}", "bright_cyan") for t in tags])
    lines.append(f"  {colors.colorize('Chủ đề Tags:', 'gray')} {tag_str}")
    lines.append(colors.colorize("  " + "─" * max(10, width - 8), "gray"))

    # Đề bài
    body_tex = _extract_question_body(question)
    lines.append(f"  {colors.colorize('Đề bài:', 'bright_white', bold=True)}")
    if body_tex.strip():
        for line in body_tex.split("\n"):
            rendered_l = render_math_terminal(line.strip())
            lines.append(f"    {rendered_l}")
    else:
        lines.append(colors.colorize("    (Không có phần mở đầu)", "gray", italic=True))

    # Nếu là câu có các ý con (FRQ_MP: trường 'part')
    part_dict = question.get("part")
    if part_dict and isinstance(part_dict, dict):
        lines.append("")
        lines.append(f"  {colors.colorize('Các ý yêu cầu:', 'bright_white', bold=True)}")
        prefixes = latex_renderer.extract_choice_prefixes(part_dict)
        for p in prefixes:
            part_tex = latex_renderer.render_single_choice(part_dict, p)
            p_tag = colors.colorize(f"({p})", "bright_yellow", bold=True)
            p_rendered = render_math_terminal(part_tex.strip())
            lines.append(f"    {p_tag} {p_rendered}")

    # Nếu có phần kết (FRQ_MP: trường 'end')
    end_dict = question.get("end")
    if end_dict and isinstance(end_dict, dict):
        end_tex = latex_renderer.render_content_block(end_dict, row_separator="\n")
        if end_tex.strip():
            lines.append("")
            lines.append(f"    {render_math_terminal(end_tex.strip())}")

    # Nếu có các lựa chọn trắc nghiệm (trường 'choices')
    choices_dict = question.get("choices")
    if choices_dict and isinstance(choices_dict, dict):
        lines.append("")
        lines.append(f"  {colors.colorize('Các phương án lựa chọn:', 'bright_white', bold=True)}")
        prefixes = latex_renderer.extract_choice_prefixes(choices_dict)
        for p in prefixes:
            choice_tex = latex_renderer.render_single_choice(choices_dict, p)
            letter = p.upper()
            c_tag = colors.colorize(f"[{letter}]", "bright_green", bold=True)
            c_rendered = render_math_terminal(choice_tex.strip())
            lines.append(f"    {c_tag} {c_rendered}")

    # Lời giải nếu có
    sol = question.get("solution")
    if sol:
        lines.append("")
        lines.append(f"  {colors.colorize('Đáp án / Hướng dẫn giải:', 'bright_yellow', bold=True)}")
        lines.append(f"    {colors.colorize(str(sol), 'bright_white')}")

    # Đóng khung panel
    content = "\n".join(lines)
    return components.panel(content, title=f" {q_title} ", border_color="bright_cyan", width=width)
