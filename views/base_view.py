"""
base_view.py - Các hàm tiện ích dùng chung cho các màn hình (Views) trong ICSC CLI.
"""

from typing import List, Optional
from .. import config
from ..ui import colors
from ..ui import terminal
from ..ui import components


def render_header(breadcrumbs: Optional[List[str]] = None, show_banner: bool = False) -> None:
    """Xóa màn hình và vẽ thanh tiêu đề đồng nhất cho tất cả các View."""
    terminal.clear_screen()
    width = terminal.get_terminal_width()

    if show_banner:
        components.print_banner(width)
    else:
        # Header thu nhỏ hiện đại
        app_tag = colors.colorize(f" {config.APP_NAME} v{config.APP_VERSION} ", "black")
        bg_header = f"\033[46m{app_tag}\033[0m"
        sub_title = colors.colorize("HỆ THỐNG TẠO ĐỀ & QUẢN LÝ NGÂN HÀNG CÂU HỎI", "gray")

        print()
        print(f"  {bg_header}  {sub_title}")
        print()

    if breadcrumbs:
        full_crumbs = ["Thoth"] + breadcrumbs
        print(components.breadcrumb(full_crumbs, width))
        print()


def press_any_key(prompt: str = "Nhấn phím bất kỳ để tiếp tục...") -> None:
    """Đợi người dùng bấm phím để quay lại."""
    from ..ui import input_handler
    print()
    print(f"  {colors.colorize('▸', 'bright_cyan')} {colors.colorize(prompt, 'gray', italic=True)}")
    input_handler.read_key()
