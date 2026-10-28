"""
table.py - Trình vẽ bảng Unicode trực quan với căn lề tuyệt đối, bóc tách ANSI và hỗ trợ tiếng Việt.
Hỗ trợ nhiều kiểu viền (bo góc, viền đôi, viền đơn, viền hiện đại).
"""

from typing import List, Optional, Union
from . import colors
from . import terminal


def render_table(
    headers: List[str],
    rows: List[List[Union[str, int, float]]],
    alignments: Optional[List[str]] = None,
    border_style: str = "rounded",
    border_color: str = "cyan",
    header_color: str = "bright_white",
    header_bg: Optional[str] = None,
    max_width: Optional[int] = None,
    padding: int = 1,
) -> str:
    """
    Vẽ bảng dữ liệu dạng chuỗi hoàn chỉnh.

    Args:
        headers: Danh sách tiêu đề cột
        rows: Danh sách các dòng dữ liệu
        alignments: 'left', 'center', 'right' cho từng cột (mặc định 'left')
        border_style: 'rounded', 'double', 'single'
        border_color: Màu viền bảng
        header_color: Màu chữ tiêu đề
        header_bg: Màu nền tiêu đề
        max_width: Giới hạn chiều rộng tối đa (mặc định theo kích thước terminal)
        padding: Khoảng cách đệm hai bên mỗi ô
    """
    if not headers and not rows:
        return ""

    num_cols = max(len(headers), max((len(r) for r in rows), default=0))
    if num_cols == 0:
        return ""

    # Chuẩn hoá headers
    norm_headers = list(headers)
    while len(norm_headers) < num_cols:
        norm_headers.append("")

    # Chuẩn hoá rows
    norm_rows = []
    for r in rows:
        row_copy = [str(cell) for cell in r]
        while len(row_copy) < num_cols:
            row_copy.append("")
        norm_rows.append(row_copy)

    # Chuẩn hoá alignments
    if alignments is None:
        alignments = ["left"] * num_cols
    else:
        alignments = list(alignments)
        while len(alignments) < num_cols:
            alignments.append("left")

    # Chọn bộ ký tự viền
    if border_style == "double":
        box = colors.BOX_DOUBLE
    elif border_style == "single":
        box = colors.BOX_SINGLE
    else:
        box = colors.BOX_ROUNDED

    # Tính chiều rộng tối thiểu cần thiết cho từng cột
    col_widths = [terminal.display_width(norm_headers[i]) for i in range(num_cols)]
    for row in norm_rows:
        for i in range(num_cols):
            w = terminal.display_width(row[i])
            if w > col_widths[i]:
                col_widths[i] = w

    # Điều chỉnh độ rộng nếu vượt quá max_width
    term_w = terminal.get_terminal_width() if max_width is None else max_width
    # Tổng viền và padding
    total_overhead = (num_cols + 1) + (num_cols * padding * 2)
    avail_w = max(20, term_w - total_overhead)

    total_content_w = sum(col_widths)
    if total_content_w > avail_w:
        # Thu nhỏ các cột dài nhất
        excess = total_content_w - avail_w
        while excess > 0:
            max_idx = max(range(num_cols), key=lambda idx: col_widths[idx])
            if col_widths[max_idx] <= 10:
                break
            reduction = min(excess, max(1, col_widths[max_idx] // 5))
            col_widths[max_idx] -= reduction
            excess -= reduction

    pad_space = " " * padding
    b_col = border_color

    def color_border(s: str) -> str:
        return colors.colorize(s, b_col)

    lines = []

    # 1. Đường viền trên cùng (Top border)
    top_parts = []
    for w in col_widths:
        top_parts.append(box["h"] * (w + padding * 2))
    lines.append(
        color_border(box["tl"])
        + color_border(box["t_down"]).join(top_parts)
        + color_border(box["tr"])
    )

    # 2. Header
    if any(norm_headers):
        header_cells = []
        for i, h in enumerate(norm_headers):
            truncated_h = terminal.truncate_string(h, col_widths[i])
            aligned_h = terminal.pad_string(truncated_h, col_widths[i], alignments[i])
            styled_h = colors.colorize(aligned_h, header_color, bold=True)
            header_cells.append(f"{pad_space}{styled_h}{pad_space}")

        lines.append(
            color_border(box["v"])
            + color_border(box["v"]).join(header_cells)
            + color_border(box["v"])
        )

        # Đường phân cách header và body
        mid_parts = []
        for w in col_widths:
            mid_parts.append(box["h"] * (w + padding * 2))
        lines.append(
            color_border(box["t_right"])
            + color_border(box["cross"]).join(mid_parts)
            + color_border(box["t_left"])
        )

    # 3. Dòng dữ liệu (Rows)
    for r_idx, row in enumerate(norm_rows):
        cells = []
        for i, cell in enumerate(row):
            truncated_c = terminal.truncate_string(cell, col_widths[i])
            aligned_c = terminal.pad_string(truncated_c, col_widths[i], alignments[i])
            cells.append(f"{pad_space}{aligned_c}{pad_space}")

        lines.append(
            color_border(box["v"])
            + color_border(box["v"]).join(cells)
            + color_border(box["v"])
        )

    # 4. Đường viền dưới cùng (Bottom border)
    bot_parts = []
    for w in col_widths:
        bot_parts.append(box["h"] * (w + padding * 2))
    lines.append(
        color_border(box["bl"])
        + color_border(box["t_up"]).join(bot_parts)
        + color_border(box["br"])
    )

    return "\n".join(lines)


def print_table(*args, **kwargs) -> None:
    """Vẽ bảng trực tiếp ra stdout."""
    output = render_table(*args, **kwargs)
    if output:
        print(output)
