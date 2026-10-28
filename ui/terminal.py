"""
terminal.py - Quản lý terminal, kích thước màn hình, tính toán chiều rộng Unicode và ANSI.
Hỗ trợ kích hoạt Virtual Terminal Processing trên Windows 10/11.
"""

import os
import re
import sys
import unicodedata
from typing import Optional

# Regex nhận diện và bóc tách mã màu ANSI
ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def init_terminal() -> None:
    """
    Kích hoạt hỗ trợ ANSI Escape Sequences trên Windows Console.
    Đồng thời thiết lập encoding UTF-8 cho stdout nếu cần.
    """
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32
        h_stdout = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        if h_stdout != -1 and h_stdout != 0:
            mode = wintypes.DWORD()
            if kernel32.GetConsoleMode(h_stdout, ctypes.byref(mode)):
                # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                # ENABLE_PROCESSED_OUTPUT = 0x0001
                kernel32.SetConsoleMode(h_stdout, mode.value | 0x0004 | 0x0001)

        # Đảm bảo UTF-8 cho Windows console
        try:
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)
        except Exception:
            pass

    # Kích hoạt os.system('') như một fallback
    try:
        os.system("")
    except Exception:
        pass


def get_terminal_width(default: int = 95) -> int:
    """Lấy chiều rộng hiện tại của cửa sổ terminal."""
    try:
        cols = os.get_terminal_size().columns
        return max(70, min(cols, 140))  # Giới hạn khung hình chuẩn
    except Exception:
        return default


def get_terminal_height(default: int = 30) -> int:
    """Lấy chiều cao hiện tại của cửa sổ terminal."""
    try:
        return max(20, os.get_terminal_size().lines)
    except Exception:
        return default


def clear_screen() -> None:
    """Xóa màn hình và đưa con trỏ về góc trái trên."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def hide_cursor() -> None:
    """Ẩn con trỏ terminal."""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    """Hiện lại con trỏ terminal."""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def strip_ansi(text: str) -> str:
    """Loại bỏ toàn bộ mã ANSI Escape sequences để tính độ dài thực tế."""
    if not text:
        return ""
    return ANSI_ESCAPE_PATTERN.sub("", text)


def display_width(text: str) -> int:
    """
    Tính chiều rộng hiển thị thực tế trên terminal của chuỗi.
    Bỏ qua mã ANSI và tính đúng ký tự toàn giác (Fullwidth / Wide Unicode).
    """
    plain = strip_ansi(text)
    w = 0
    for ch in plain:
        # Ký tự zero-width hoặc dấu thanh ghép
        if unicodedata.combining(ch):
            continue
        # East Asian Width: Fullwidth ('F') và Wide ('W') chiếm 2 cột
        if unicodedata.east_asian_width(ch) in ("F", "W"):
            w += 2
        else:
            w += 1
    return w


def pad_string(text: str, target_width: int, align: str = "left") -> str:
    """
    Căn lề chuỗi văn bản (kể cả có chứa mã màu ANSI) đạt đúng target_width hiển thị.
    """
    cur_w = display_width(text)
    diff = max(0, target_width - cur_w)

    if align == "right":
        return (" " * diff) + text
    elif align == "center":
        left = diff // 2
        right = diff - left
        return (" " * left) + text + (" " * right)
    else:  # left
        return text + (" " * diff)


def truncate_string(text: str, max_width: int, suffix: str = "...") -> str:
    """
    Cắt ngắn chuỗi văn bản nếu vượt quá max_width hiển thị.
    """
    if display_width(text) <= max_width:
        return text

    suffix_w = display_width(suffix)
    target = max(0, max_width - suffix_w)

    result = []
    cur_w = 0
    # Cắt trên văn bản gốc plain
    plain = strip_ansi(text)
    for ch in plain:
        ch_w = 2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1
        if cur_w + ch_w > target:
            break
        result.append(ch)
        cur_w += ch_w

    return "".join(result) + suffix
