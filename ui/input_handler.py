"""
input_handler.py - Bắt phím bàn phím tương tác và điều hướng menu (mũi tên lên/xuống, Enter, Space).
Đảm bảo viền khung hộp luôn liền mạch tuyệt đối 100%, không bị xô lệch kể cả khi dòng dài bất thường.
"""

import sys
from typing import List, Dict, Any, Optional, Tuple, Callable
from . import colors
from . import terminal

# Hằng số mã phím điều hướng
KEY_UP = "UP"
KEY_DOWN = "DOWN"
KEY_LEFT = "LEFT"
KEY_RIGHT = "RIGHT"
KEY_ENTER = "ENTER"
KEY_ESCAPE = "ESCAPE"
KEY_SPACE = "SPACE"
KEY_BACKSPACE = "BACKSPACE"
KEY_TAB = "TAB"
KEY_PAGE_UP = "PAGE_UP"
KEY_PAGE_DOWN = "PAGE_DOWN"
KEY_CHAR = "CHAR"
KEY_OTHER = "OTHER"


def read_key() -> Tuple[str, str]:
    """
    Đọc một phím nhấn từ bàn phím mà không cần nhấn Enter.
    Trả về tuple: (key_type, char_value).
    """
    if sys.platform == "win32":
        try:
            import msvcrt

            ch = msvcrt.getch()
            # Phím mở rộng (Extended key)
            if ch in (b"\x00", b"\xe0"):
                ch2 = msvcrt.getch()
                if ch2 == b"H":
                    return (KEY_UP, "")
                elif ch2 == b"P":
                    return (KEY_DOWN, "")
                elif ch2 == b"K":
                    return (KEY_LEFT, "")
                elif ch2 == b"M":
                    return (KEY_RIGHT, "")
                elif ch2 == b"I":
                    return (KEY_PAGE_UP, "")
                elif ch2 == b"Q":
                    return (KEY_PAGE_DOWN, "")
                return (KEY_OTHER, "")

            if ch in (b"\r", b"\n"):
                return (KEY_ENTER, "")
            elif ch == b"\x1b":
                return (KEY_ESCAPE, "")
            elif ch == b" ":
                return (KEY_SPACE, " ")
            elif ch == b"\x08":
                return (KEY_BACKSPACE, "")
            elif ch == b"\t":
                return (KEY_TAB, "")
            else:
                try:
                    return (KEY_CHAR, ch.decode("utf-8", errors="ignore"))
                except Exception:
                    return (KEY_CHAR, str(ch))
        except Exception:
            pass

    # Fallback cho Unix hoặc môi trường đặc thù
    try:
        line = sys.stdin.readline().strip()
        if not line:
            return (KEY_ENTER, "")
        return (KEY_CHAR, line)
    except Exception:
        return (KEY_ESCAPE, "")


def select_menu(
    options: List[Dict[str, Any]],
    title: str = "LỰA CHỌN THAO TÁC",
    prompt_help: str = "Dùng phím [↑/↓] hoặc bấm số, nhấn [Enter] để chọn, [Esc/b] để quay lại",
    initial_index: int = 0,
    allow_cancel: bool = True,
    width: Optional[int] = None,
) -> Optional[int]:
    """
    Hiển thị menu tương tác di chuyển con trỏ bằng phím mũi tên.
    Căn chuẩn 100% độ rộng khung viền, không bao giờ bị lệch viền do dòng quá dài.
    """
    if not options:
        return None

    if width is None:
        width = terminal.get_terminal_width()

    # Đảm bảo chiều rộng tối thiểu và chuẩn
    width = max(60, min(width, 120))
    inner_w = width - 4  # Độ rộng bên trong viền sau khi trừ 2 ký tự viền và 2 khoảng cách

    # Kiểm tra xem có thể tương tác tty không
    is_interactive = sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else True

    if not is_interactive:
        # Fallback chế độ dòng lệnh tĩnh
        print(f"\n{colors.colorize(title, 'bright_cyan', bold=True)}")
        for i, opt in enumerate(options):
            key_tag = opt.get("key", str(i + 1))
            label = opt.get("label", "")
            desc = f" ({opt['desc']})" if "desc" in opt else ""
            print(f"  [{key_tag}] {label}{desc}")
        try:
            choice = input("\nLựa chọn của bạn: ").strip()
            for i, opt in enumerate(options):
                if choice == str(opt.get("key", str(i + 1))) or choice == str(i + 1):
                    return i
            return None
        except Exception:
            return None

    current_idx = max(0, min(initial_index, len(options) - 1))
    terminal.hide_cursor()

    try:
        while True:
            lines_to_render = []
            box = colors.BOX_ROUNDED
            v_border = colors.colorize(box["v"], "bright_cyan")

            # 1. Header (Khung trên cùng)
            title_clean = f" {title.strip()} "
            max_title_w = width - 6
            if terminal.display_width(title_clean) > max_title_w:
                title_clean = terminal.truncate_string(title_clean, max_title_w)
            title_w = terminal.display_width(title_clean)
            right_h_count = max(0, width - 4 - title_w)

            top_line = (
                colors.colorize(f"{box['tl']}{box['h'] * 2}", "bright_cyan")
                + colors.colorize(title_clean, "bright_white", bold=True)
                + colors.colorize(f"{box['h'] * right_h_count}{box['tr']}", "bright_cyan")
            )
            lines_to_render.append(top_line)

            # 2. Render từng dòng options
            for i, opt in enumerate(options):
                is_selected = (i == current_idx)
                key_tag = str(opt.get("key", str(i + 1)))
                icon = opt.get("icon", "▸" if is_selected else " ")
                label = opt.get("label", "")
                desc = opt.get("desc", "")
                badge_text = opt.get("badge", "")

                # Badge phía bên phải
                badge_str = ""
                badge_w = 0
                if badge_text:
                    badge_str = colors.badge(badge_text, bg_color="blue", fg_color="white")
                    badge_w = terminal.display_width(badge_str)

                # Prefix bên trái: con trỏ + phím số + icon
                if is_selected:
                    pointer_styled = colors.colorize(" ➔ ", "bright_yellow", bold=True)
                    key_styled = colors.colorize(f"[{key_tag}]", "bright_white", bold=True)
                    icon_styled = colors.colorize(icon, "bright_yellow")
                    label_styled_base = "bright_yellow"
                else:
                    pointer_styled = "   "
                    key_styled = colors.colorize(f"[{key_tag}]", "gray")
                    icon_styled = colors.colorize(icon, "gray")
                    label_styled_base = "white"

                prefix_plain = f"   [{key_tag}] {icon} "
                prefix_styled = f"{pointer_styled}{key_styled} {icon_styled} "
                prefix_w = terminal.display_width(prefix_plain)

                # Chiều rộng còn lại cho Label và Desc
                avail_content_w = inner_w - prefix_w - (badge_w + 1 if badge_w > 0 else 0)
                avail_content_w = max(5, avail_content_w)

                if desc:
                    # Chia không gian giữa label và desc
                    label_max = min(terminal.display_width(label), max(18, avail_content_w // 2))
                    label_trunc = terminal.truncate_string(label, label_max)
                    rem_for_desc = max(0, avail_content_w - terminal.display_width(label_trunc) - 2)
                    desc_trunc = terminal.truncate_string(desc, rem_for_desc) if rem_for_desc > 3 else ""

                    label_styled = colors.colorize(label_trunc, label_styled_base, bold=is_selected)
                    desc_styled = colors.colorize(f" ({desc_trunc})", "gray", italic=True) if desc_trunc else ""
                    left_text_plain = f"{prefix_plain}{label_trunc}{f' ({desc_trunc})' if desc_trunc else ''}"
                    left_text_styled = f"{prefix_styled}{label_styled}{desc_styled}"
                else:
                    label_trunc = terminal.truncate_string(label, avail_content_w)
                    label_styled = colors.colorize(label_trunc, label_styled_base, bold=is_selected)
                    left_text_plain = f"{prefix_plain}{label_trunc}"
                    left_text_styled = f"{prefix_styled}{label_styled}"

                # Căn lề padding chuẩn xác đến từng ký tự
                left_actual_w = terminal.display_width(left_text_plain)
                pad_count = max(0, inner_w - left_actual_w - badge_w)
                content_row = f"{left_text_styled}{' ' * pad_count}{badge_str}"

                # Kiểm tra bù trừ độ rộng tuyệt đối
                cur_cw = terminal.display_width(content_row)
                if cur_cw < inner_w:
                    content_row += " " * (inner_w - cur_cw)

                lines_to_render.append(f"{v_border} {content_row} {v_border}")

            # 3. Đường phân cách và Footer hướng dẫn
            mid_border = colors.colorize(f"{box['t_right']}{box['h'] * (width - 2)}{box['t_left']}", "bright_cyan")
            lines_to_render.append(mid_border)

            help_trunc = terminal.truncate_string(prompt_help, inner_w)
            help_styled = colors.colorize(help_trunc, "gray", dim=True)
            help_w = terminal.display_width(help_trunc)
            help_pad = " " * max(0, inner_w - help_w)
            lines_to_render.append(f"{v_border} {help_styled}{help_pad} {v_border}")

            bot_border = colors.colorize(f"{box['bl']}{box['h'] * (width - 2)}{box['br']}", "bright_cyan")
            lines_to_render.append(bot_border)

            # In menu ra màn hình
            menu_output = "\n".join(lines_to_render)
            print(menu_output)

            # Đợi phím bấm
            k_type, k_val = read_key()

            # Xoá các dòng đã vẽ để vẽ lại frame mới
            total_lines = len(lines_to_render)
            sys.stdout.write(f"\033[{total_lines}A\r")
            sys.stdout.flush()

            if k_type == KEY_UP:
                current_idx = (current_idx - 1) % len(options)
            elif k_type == KEY_DOWN:
                current_idx = (current_idx + 1) % len(options)
            elif k_type == KEY_ENTER:
                terminal.show_cursor()
                sys.stdout.write(f"\033[{total_lines}B\n")
                sys.stdout.flush()
                return current_idx
            elif k_type == KEY_ESCAPE:
                if allow_cancel:
                    terminal.show_cursor()
                    sys.stdout.write(f"\033[{total_lines}B\n")
                    sys.stdout.flush()
                    return None
            elif k_type == KEY_CHAR:
                k_char = k_val.lower()
                if allow_cancel and k_char in ("b", "q"):
                    terminal.show_cursor()
                    sys.stdout.write(f"\033[{total_lines}B\n")
                    sys.stdout.flush()
                    return None
                for idx, opt in enumerate(options):
                    if str(opt.get("key", "")).lower() == k_char:
                        terminal.show_cursor()
                        sys.stdout.write(f"\033[{total_lines}B\n")
                        sys.stdout.flush()
                        return idx
    finally:
        terminal.show_cursor()


def multi_select_menu(
    items: List[Dict[str, Any]],
    title: str = "CHỌN DANH SÁCH (CÓ THỂ CHỌN NHIỀU)",
    prompt_help: str = "[↑/↓] Di chuyển | [Space] Chọn/Bỏ | [a] Chọn tất cả | [Enter] Xác nhận | [Esc] Hủy",
    initial_selected: Optional[List[int]] = None,
    width: Optional[int] = None,
) -> Optional[List[int]]:
    """
    Menu chọn nhiều mục với checkbox [✔] / [ ].
    Căn chuẩn 100% độ rộng khung viền, viền liền mạch không xô lệch.
    """
    if not items:
        return []

    if width is None:
        width = terminal.get_terminal_width()

    width = max(60, min(width, 120))
    inner_w = width - 4

    selected_set = set(initial_selected or [])
    current_idx = 0
    terminal.hide_cursor()

    try:
        while True:
            lines = []
            box = colors.BOX_ROUNDED
            v_border = colors.colorize(box["v"], "bright_cyan")

            # 1. Header
            title_clean = f" {title.strip()} "
            max_title_w = width - 6
            if terminal.display_width(title_clean) > max_title_w:
                title_clean = terminal.truncate_string(title_clean, max_title_w)
            title_w = terminal.display_width(title_clean)
            right_h_count = max(0, width - 4 - title_w)

            top_line = (
                colors.colorize(f"{box['tl']}{box['h'] * 2}", "bright_cyan")
                + colors.colorize(title_clean, "bright_white", bold=True)
                + colors.colorize(f"{box['h'] * right_h_count}{box['tr']}", "bright_cyan")
            )
            lines.append(top_line)

            # 2. Danh sách
            for i, item in enumerate(items):
                is_cursor = (i == current_idx)
                is_checked = (i in selected_set)

                cb_icon = (
                    colors.colorize("[✔]", "bright_green", bold=True)
                    if is_checked
                    else colors.colorize("[ ]", "gray")
                )
                pointer = colors.colorize(" ➔ ", "bright_yellow", bold=True) if is_cursor else "   "

                label = item.get("label", "")
                desc = item.get("desc", "")

                label_styled_base = "bright_yellow" if is_cursor else "bright_white"
                prefix_plain = f"   {'[✔]' if is_checked else '[ ]'} "
                prefix_styled = f"{pointer}{cb_icon} "
                prefix_w = terminal.display_width(prefix_plain)

                avail_w = max(5, inner_w - prefix_w)

                if desc:
                    label_max = min(terminal.display_width(label), max(18, avail_w // 2))
                    label_trunc = terminal.truncate_string(label, label_max)
                    rem_for_desc = max(0, avail_w - terminal.display_width(label_trunc) - 2)
                    desc_trunc = terminal.truncate_string(desc, rem_for_desc) if rem_for_desc > 3 else ""

                    label_styled = colors.colorize(label_trunc, label_styled_base, bold=is_cursor)
                    desc_styled = colors.colorize(f" ({desc_trunc})", "gray", italic=True) if desc_trunc else ""
                    full_plain = f"{prefix_plain}{label_trunc}{f' ({desc_trunc})' if desc_trunc else ''}"
                    full_styled = f"{prefix_styled}{label_styled}{desc_styled}"
                else:
                    label_trunc = terminal.truncate_string(label, avail_w)
                    label_styled = colors.colorize(label_trunc, label_styled_base, bold=is_cursor)
                    full_plain = f"{prefix_plain}{label_trunc}"
                    full_styled = f"{prefix_styled}{label_styled}"

                actual_w = terminal.display_width(full_plain)
                pad_count = max(0, inner_w - actual_w)
                content_row = f"{full_styled}{' ' * pad_count}"

                cur_cw = terminal.display_width(content_row)
                if cur_cw < inner_w:
                    content_row += " " * (inner_w - cur_cw)

                lines.append(f"{v_border} {content_row} {v_border}")

            # 3. Footer
            lines.append(colors.colorize(f"{box['t_right']}{box['h'] * (width - 2)}{box['t_left']}", "bright_cyan"))

            count_info = f"Đã chọn: {len(selected_set)}/{len(items)} | "
            full_help = count_info + prompt_help
            help_trunc = terminal.truncate_string(full_help, inner_w)
            help_w = terminal.display_width(help_trunc)
            help_pad = " " * max(0, inner_w - help_w)
            help_styled = colors.colorize(help_trunc, "gray", dim=True)
            lines.append(f"{v_border} {help_styled}{help_pad} {v_border}")

            lines.append(colors.colorize(f"{box['bl']}{box['h'] * (width - 2)}{box['br']}", "bright_cyan"))

            # In ra màn hình
            print("\n".join(lines))

            # Bắt phím
            k_type, k_val = read_key()

            # Xóa các dòng
            sys.stdout.write(f"\033[{len(lines)}A\r")
            sys.stdout.flush()

            if k_type == KEY_UP:
                current_idx = (current_idx - 1) % len(items)
            elif k_type == KEY_DOWN:
                current_idx = (current_idx + 1) % len(items)
            elif k_type == KEY_SPACE:
                if current_idx in selected_set:
                    selected_set.remove(current_idx)
                else:
                    selected_set.add(current_idx)
            elif k_type == KEY_CHAR and k_val.lower() == "a":
                if len(selected_set) == len(items):
                    selected_set.clear()
                else:
                    selected_set = set(range(len(items)))
            elif k_type == KEY_ENTER:
                terminal.show_cursor()
                sys.stdout.write(f"\033[{len(lines)}B\n")
                sys.stdout.flush()
                return sorted(list(selected_set))
            elif k_type == KEY_ESCAPE:
                terminal.show_cursor()
                sys.stdout.write(f"\033[{len(lines)}B\n")
                sys.stdout.flush()
                return None
    finally:
        terminal.show_cursor()


def prompt_text(
    message: str,
    default: str = "",
    validator: Optional[Callable[[str], bool]] = None,
    error_msg: str = "Giá trị không hợp lệ, vui lòng thử lại.",
) -> str:
    """Nhập chuỗi văn bản với giá trị mặc định và kiểm tra tính hợp lệ."""
    terminal.show_cursor()
    prompt_str = f"  {colors.colorize('?', 'bright_cyan', bold=True)} {colors.colorize(message, 'bright_white')}"
    if default:
        prompt_str += f" {colors.colorize(f'({default})', 'gray')}"
    prompt_str += ": "

    while True:
        try:
            val = input(prompt_str).strip()
            if not val and default:
                return default
            if validator and not validator(val):
                print(f"  {colors.colorize('✖', 'bright_red')} {colors.colorize(error_msg, 'bright_red')}")
                continue
            return val
        except (KeyboardInterrupt, EOFError):
            return default


def confirm(message: str, default: bool = True) -> bool:
    """Hỏi xác nhận Có/Không (Y/n hoặc y/N)."""
    options = " (Y/n): " if default else " (y/N): "
    prompt_str = f"  {colors.colorize('?', 'bright_yellow', bold=True)} {colors.colorize(message, 'bright_white')}{options}"
    try:
        ans = input(prompt_str).strip().lower()
        if not ans:
            return default
        return ans in ("y", "yes", "có", "c", "1")
    except (KeyboardInterrupt, EOFError):
        return default
