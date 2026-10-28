"""
components.py - Các khối giao diện trực quan: Panel, Banner, Thẻ thống kê, Thanh tiến trình, Breadcrumb.
"""

import sys
import time
from typing import List, Dict, Any, Optional, Tuple
from . import colors
from . import terminal


def print_banner(width: Optional[int] = None) -> None:
    """In banner chính của Thoth với phong cách gradient hiện đại."""
    if width is None:
        width = terminal.get_terminal_width()

    banner_lines = [
        "   ████████╗██╗  ██╗ ██████╗ ████████╗██╗  ██╗",
        "   ╚══██╔══╝██║  ██║██╔═══██╗╚══██╔══╝██║  ██║",
        "      ██║   ███████║██║   ██║   ██║   ███████║",
        "      ██║   ██╔══██║██║   ██║   ██║   ██╔══██║",
        "      ██║   ██║  ██║╚██████╔╝   ██║   ██║  ██║",
        "      ╚═╝   ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝",
    ]

    print()
    for line in banner_lines:
        print(colors.colorize(line, "bright_cyan", bold=True))

    sub_title = "★ THOTH - HỆ THỐNG TẠO ĐỀ THI & QUẢN LÝ NGÂN HÀNG CÂU HỎI ★"
    credit = "Thoth Intelligent Exam System • Terminal Pro v2.0"

    print(terminal.pad_string(colors.colorize(sub_title, "bright_yellow", bold=True), width, "center"))
    print(terminal.pad_string(colors.colorize(credit, "gray", italic=True), width, "center"))
    print()


def breadcrumb(segments: List[str], width: Optional[int] = None) -> str:
    """Tạo thanh điều hướng breadcrumb: ICSC > 🎓 Tạo đề > Calculus 1."""
    if not segments:
        return ""
    sep = colors.colorize(" › ", "gray")
    styled_segments = []
    for i, seg in enumerate(segments):
        if i == len(segments) - 1:
            styled_segments.append(colors.colorize(seg, "bright_yellow", bold=True))
        else:
            styled_segments.append(colors.colorize(seg, "bright_white"))

    crumb_str = sep.join(styled_segments)
    return f"  {colors.colorize('●', 'bright_cyan')} {crumb_str}"


def divider(title: str = "", width: Optional[int] = None, color: str = "gray") -> None:
    """In đường phân cách ngang thanh lịch."""
    if width is None:
        width = terminal.get_terminal_width()

    if not title:
        print(colors.colorize("─" * width, color))
        return

    title_w = terminal.display_width(title)
    if title_w + 6 >= width:
        print(colors.colorize(title, color, bold=True))
        return

    left_w = 4
    right_w = max(0, width - title_w - left_w - 2)
    left_str = "─" * left_w
    right_str = "─" * right_w

    full = (
        colors.colorize(left_str, color)
        + f" {colors.colorize(title, 'bright_white', bold=True)} "
        + colors.colorize(right_str, color)
    )
    print(full)


def wrap_text_ansi(line: str, max_w: int) -> List[str]:
    """
    Tự động xuống dòng các đoạn văn bản dài mà vẫn bảo toàn mã màu ANSI,
    căn lề thụt đầu dòng (indentation) và không bao giờ cắt cụt văn bản bằng '...'.
    """
    if terminal.display_width(line) <= max_w:
        return [line]

    import re
    plain = terminal.strip_ansi(line)
    leading_count = len(plain) - len(plain.lstrip(" "))
    indent = " " * leading_count

    tokens = re.split(r"( +)", line)
    sub_lines = []
    cur_line = ""

    for tok in tokens:
        if not tok:
            continue
        test_cand = cur_line + tok
        if terminal.display_width(test_cand) <= max_w:
            cur_line = test_cand
        else:
            if cur_line.strip():
                sub_lines.append(cur_line)
                cur_line = indent + (tok if tok.strip() else "")
            else:
                for ch in tok:
                    if terminal.display_width(cur_line + ch) > max_w:
                        if cur_line:
                            sub_lines.append(cur_line)
                        cur_line = indent + ch
                    else:
                        cur_line += ch

    if cur_line.strip():
        sub_lines.append(cur_line)

    return sub_lines if sub_lines else [line]


def panel(
    content: str,
    title: str = "",
    subtitle: str = "",
    border_style: str = "rounded",
    border_color: str = "cyan",
    padding: int = 1,
    width: Optional[int] = None,
) -> str:
    """Bọc nội dung trong một Panel hộp trực quan với tự động ngắt dòng thông minh."""
    if width is None:
        width = terminal.get_terminal_width()

    box = (
        colors.BOX_DOUBLE
        if border_style == "double"
        else colors.BOX_SINGLE
        if border_style == "single"
        else colors.BOX_ROUNDED
    )

    lines = content.split("\n")
    inner_width = max(10, width - 2 - (padding * 2))

    # Tự động xuống dòng cho các dòng dài mà không bao giờ cắt bỏ bằng '...'
    expanded_lines = []
    for line in lines:
        if terminal.display_width(line) > inner_width:
            expanded_lines.extend(wrap_text_ansi(line, inner_width))
        else:
            expanded_lines.append(line)

    # Top border with title
    header_text = f" {title} " if title else ""
    header_w = terminal.display_width(header_text)
    if header_text:
        left_h = box["h"] * 2
        right_h = box["h"] * max(0, width - 2 - 2 - header_w)
        top_line = (
            colors.colorize(f"{box['tl']}{left_h}", border_color)
            + colors.colorize(header_text, "bright_white", bold=True)
            + colors.colorize(f"{right_h}{box['tr']}", border_color)
        )
    else:
        top_line = colors.colorize(f"{box['tl']}{box['h'] * (width - 2)}{box['tr']}", border_color)

    res = [top_line]

    pad_space = " " * padding
    v_border = colors.colorize(box["v"], border_color)

    for line in expanded_lines:
        line_w = terminal.display_width(line)
        pad_r = " " * max(0, inner_width - line_w)
        res.append(f"{v_border}{pad_space}{line}{pad_r}{pad_space}{v_border}")

    # Bottom border with optional subtitle
    if subtitle:
        sub_text = f" {subtitle} "
        sub_w = terminal.display_width(sub_text)
        left_h = box["h"] * max(0, width - 4 - sub_w)
        right_h = box["h"] * 2
        bot_line = (
            colors.colorize(f"{box['bl']}{left_h}", border_color)
            + colors.colorize(sub_text, "gray", italic=True)
            + colors.colorize(f"{right_h}{box['br']}", border_color)
        )
    else:
        bot_line = colors.colorize(f"{box['bl']}{box['h'] * (width - 2)}{box['br']}", border_color)

    res.append(bot_line)
    return "\n".join(res)


def key_value_card(data: List[Tuple[str, str]], title: str = "", border_color: str = "cyan") -> str:
    """Hiển thị card chứa các cặp thông số (Key-Value)."""
    if not data:
        return ""
    max_k_w = max((terminal.display_width(k) for k, _ in data), default=10)

    rows = []
    for k, v in data:
        k_padded = terminal.pad_string(k, max_k_w, "right")
        k_styled = colors.colorize(k_padded, "bright_cyan")
        v_styled = colors.colorize(str(v), "bright_white", bold=True)
        rows.append(f"  {k_styled}  :  {v_styled}")

    content = "\n".join(rows)
    return panel(content, title=title, border_color=border_color)


def stat_card(label: str, value: Any, icon: str = "📊", color: str = "bright_cyan") -> str:
    """Tạo thẻ thống kê thu nhỏ."""
    val_str = colors.colorize(str(value), color, bold=True)
    lbl_str = colors.colorize(label, "gray")
    return f"[{icon} {lbl_str}: {val_str}]"


def progress_bar(current: int, total: int, width: int = 25, label: str = "") -> str:
    """Tạo chuỗi thanh tiến trình trực quan: [████████░░░░░] 60%."""
    if total <= 0:
        total = 1
    pct = max(0.0, min(1.0, current / total))
    filled_len = int(width * pct)
    empty_len = width - filled_len

    bar = (
        colors.colorize("█" * filled_len, "bright_green")
        + colors.colorize("░" * empty_len, "gray")
    )
    pct_str = colors.colorize(f"{int(pct * 100):>3}%", "bright_yellow", bold=True)
    count_str = colors.colorize(f"({current}/{total})", "gray")

    if label:
        return f"{label} [{bar}] {pct_str} {count_str}"
    return f"[{bar}] {pct_str} {count_str}"
