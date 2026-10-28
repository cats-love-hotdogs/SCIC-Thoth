"""
colors.py - Hệ thống màu sắc ANSI, định dạng văn bản và ký tự đồ họa Unicode.
Tương thích hoàn toàn với Windows Terminal, PowerShell, CMD và mọi terminal hiện đại.
"""

import sys

# Ký tự ESC ANSI
ESC = "\033["
RESET = f"{ESC}0m"
BOLD = f"{ESC}1m"
DIM = f"{ESC}2m"
ITALIC = f"{ESC}3m"
UNDERLINE = f"{ESC}4m"
BLINK = f"{ESC}5m"
REVERSE = f"{ESC}7m"
HIDDEN = f"{ESC}8m"

# Màu chữ cơ bản
BLACK = f"{ESC}30m"
RED = f"{ESC}31m"
GREEN = f"{ESC}32m"
YELLOW = f"{ESC}33m"
BLUE = f"{ESC}34m"
MAGENTA = f"{ESC}35m"
CYAN = f"{ESC}36m"
WHITE = f"{ESC}37m"

# Màu chữ sáng (Bright / High Intensity)
BRIGHT_BLACK = f"{ESC}90m"   # Gray
BRIGHT_RED = f"{ESC}91m"
BRIGHT_GREEN = f"{ESC}92m"
BRIGHT_YELLOW = f"{ESC}93m"
BRIGHT_BLUE = f"{ESC}94m"
BRIGHT_MAGENTA = f"{ESC}95m"
BRIGHT_CYAN = f"{ESC}96m"
BRIGHT_WHITE = f"{ESC}97m"

# Màu nền (Background)
BG_BLACK = f"{ESC}40m"
BG_RED = f"{ESC}41m"
BG_GREEN = f"{ESC}42m"
BG_YELLOW = f"{ESC}43m"
BG_BLUE = f"{ESC}44m"
BG_MAGENTA = f"{ESC}45m"
BG_CYAN = f"{ESC}46m"
BG_WHITE = f"{ESC}47m"

# Tên màu ánh xạ
COLOR_MAP = {
    "black": BLACK,
    "red": RED,
    "green": GREEN,
    "yellow": YELLOW,
    "blue": BLUE,
    "magenta": MAGENTA,
    "cyan": CYAN,
    "white": WHITE,
    "gray": BRIGHT_BLACK,
    "grey": BRIGHT_BLACK,
    "bright_red": BRIGHT_RED,
    "bright_green": BRIGHT_GREEN,
    "bright_yellow": BRIGHT_YELLOW,
    "bright_blue": BRIGHT_BLUE,
    "bright_magenta": BRIGHT_MAGENTA,
    "bright_cyan": BRIGHT_CYAN,
    "bright_white": BRIGHT_WHITE,
}

# Hộp vẽ Unicode
BOX_ROUNDED = {
    "tl": "╭", "tr": "╮", "bl": "╰", "br": "╯",
    "h": "─", "v": "│",
    "t_down": "┬", "t_up": "┴", "t_right": "├", "t_left": "┤", "cross": "┼"
}

BOX_DOUBLE = {
    "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
    "h": "═", "v": "║",
    "t_down": "╦", "t_up": "╩", "t_right": "╠", "t_left": "╣", "cross": "╬"
}

BOX_SINGLE = {
    "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
    "h": "─", "v": "│",
    "t_down": "┬", "t_up": "┴", "t_right": "├", "t_left": "┤", "cross": "┼"
}

# Icon và biểu tượng đồ họa
ICONS = {
    "check": "✔",
    "cross": "✖",
    "dot": "●",
    "empty_dot": "○",
    "arrow_right": "→",
    "arrow_bullet": "▸",
    "star": "★",
    "sparkle": "✦",
    "lightning": "⚡",
    "book": "📚",
    "grad": "🎓",
    "gear": "⚙",
    "doc": "📄",
    "clock": "🕒",
    "search": "🔍",
    "folder": "📁",
    "tag": "🏷",
    "pin": "📌",
    "rocket": "🚀",
    "stats": "📊",
    "question": "❓",
    "warn": "⚠",
    "info": "ℹ",
    "box_checked": "[✔]",
    "box_unchecked": "[ ]",
}


def colorize(text: str, color: str = "", bold: bool = False, dim: bool = False, underline: bool = False, italic: bool = False) -> str:
    """Bao bọc văn bản bằng mã màu ANSI."""
    if not text:
        return ""
    code = ""
    if bold:
        code += BOLD
    if dim:
        code += DIM
    if underline:
        code += UNDERLINE
    if italic:
        code += ITALIC
    if color:
        c_code = COLOR_MAP.get(color.lower(), "")
        if c_code:
            code += c_code
        elif color.startswith(ESC):
            code += color

    if not code:
        return text
    return f"{code}{text}{RESET}"


def rgb(r: int, g: int, b: int) -> str:
    """Trả về mã màu ANSI 24-bit RGB cho màu chữ."""
    return f"{ESC}38;2;{r};{g};{b}m"


def bg_rgb(r: int, g: int, b: int) -> str:
    """Trả về mã màu ANSI 24-bit RGB cho nền."""
    return f"{ESC}48;2;{r};{g};{b}m"


# Các nhãn badge thường dùng
def badge(text: str, bg_color: str = "cyan", fg_color: str = "black", bold: bool = True) -> str:
    """Tạo badge chữ nổi."""
    bg_code = {
        "cyan": f"{ESC}46m",
        "green": f"{ESC}42m",
        "blue": f"{ESC}44m",
        "yellow": f"{ESC}43m",
        "magenta": f"{ESC}45m",
        "red": f"{ESC}41m",
        "gray": f"{ESC}100m",
        "white": f"{ESC}47m",
    }.get(bg_color.lower(), f"{ESC}46m")

    fg_code = BLACK if fg_color == "black" else BRIGHT_WHITE
    b_code = BOLD if bold else ""
    return f"{bg_code}{fg_code}{b_code} {text} {RESET}"


def badge_success(text: str = "THÀNH CÔNG") -> str:
    return badge(text, bg_color="green", fg_color="black")


def badge_error(text: str = "LỖI") -> str:
    return badge(text, bg_color="red", fg_color="white")


def badge_warn(text: str = "CẢNH BÁO") -> str:
    return badge(text, bg_color="yellow", fg_color="black")


def badge_info(text: str = "THÔNG TIN") -> str:
    return badge(text, bg_color="blue", fg_color="white")
