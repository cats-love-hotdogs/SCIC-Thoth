"""
history_view.py - Màn hình xem lịch sử đề thi đã tạo và quản lý các file xuất bản.
Hỗ trợ mở trực tiếp file PDF, file .tex và xem danh sách mã câu hỏi trong từng đề.
"""

from pathlib import Path
from datetime import datetime
from ..ui import colors
from ..ui import terminal
from ..ui import components
from ..ui import input_handler
from ..ui import table
from ..core import exam_log
from ..core import latex_compiler
from . import base_view


def show_history() -> None:
    """Màn hình hiển thị danh sách các đề thi trong lịch sử."""
    while True:
        base_view.render_header(breadcrumbs=["Lịch Sử Đề Thi"])
        width = terminal.get_terminal_width()

        logs = exam_log.read_all_logs()
        if not logs:
            print(f"  {colors.badge_info()} Chưa có đề thi nào được tạo trong lịch sử hệ thống.")
            base_view.press_any_key()
            break

        headers = ["STT", "Thời Điểm Tạo", "Môn Học", "Loại Đề", "Mã Đề", "Số Câu", "File PDF"]
        rows = []
        for i, entry in enumerate(logs, 1):
            ts = entry.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(ts)
                time_str = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                time_str = ts[:16]

            subj = entry.get("subject", "N/A")
            t_name = entry.get("exam_type", "N/A")
            type_label = {
                "midterm": "Giữa kỳ",
                "final": "Cuối kỳ",
                "practice": "Tự luyện",
            }.get(t_name, t_name)

            q_count = entry.get("question_count", len(entry.get("question_codes", [])))
            code = entry.get("exam_code", "-")
            pdf_path = entry.get("pdf_path", "")

            pdf_badge = (
                colors.colorize("✔ Có PDF", "bright_green")
                if pdf_path and Path(pdf_path).exists()
                else colors.colorize("✖ Không có", "gray")
            )

            rows.append([
                str(i),
                time_str,
                subj,
                type_label,
                str(code),
                f"{q_count} câu",
                pdf_badge,
            ])

        print(table.render_table(
            headers=headers,
            rows=rows,
            alignments=["center", "center", "left", "center", "center", "center", "center"],
            border_color="cyan",
            max_width=width,
        ))
        print()

        menu_opts = [
            {
                "key": "1",
                "label": "Chọn một đề thi để xem chi tiết / Mở file PDF",
                "desc": "Mở file PDF, xem mã câu hỏi hoặc thư mục chứa file",
                "badge": "Chi tiết",
                "action": "detail",
            },
            {
                "key": "0",
                "label": "Quay lại Dashboard",
                "desc": "Trở về màn hình chính",
                "badge": "Quay lại",
                "action": "back",
            },
        ]

        choice_idx = input_handler.select_menu(menu_opts, title="THAO TÁC LỊCH SỬ ĐỀ THI", width=width)
        if choice_idx is None or menu_opts[choice_idx]["action"] == "back":
            break

        if menu_opts[choice_idx]["action"] == "detail":
            val = input_handler.prompt_text(f"Nhập số thứ tự đề thi (1 - {len(logs)})", default="1")
            try:
                idx = int(val) - 1
                if 0 <= idx < len(logs):
                    _show_exam_detail(logs[idx])
            except ValueError:
                pass


def _show_exam_detail(entry: dict) -> None:
    """Hiển thị chi tiết một đề thi và các tùy chọn mở file."""
    while True:
        base_view.render_header(breadcrumbs=["Lịch Sử Đề Thi", f"Chi Tiết Đề Thi ({entry.get('subject')})"])
        width = terminal.get_terminal_width()

        pdf_p = Path(entry.get("pdf_path", "")) if entry.get("pdf_path") else None
        tex_p = Path(entry.get("tex_path", "")) if entry.get("tex_path") else None

        info_list = [
            ("Môn học", entry.get("subject", "N/A")),
            ("Loại đề", entry.get("exam_type", "N/A")),
            ("Mã đề thi", entry.get("exam_code", "-")),
            ("Thời điểm tạo", entry.get("timestamp", "")),
            ("Số câu hỏi", str(entry.get("question_count", len(entry.get("question_codes", []))))),
            ("File PDF", str(pdf_p) if pdf_p and pdf_p.exists() else "Không tìm thấy"),
            ("File TeX", str(tex_p) if tex_p and tex_p.exists() else "Không tìm thấy"),
        ]

        print(components.key_value_card(info_list, title="THÔNG TIN ĐỀ THI"))
        print()

        # Hiển thị danh sách câu hỏi
        codes = entry.get("question_codes", [])
        if codes:
            print(f"  {colors.colorize('Danh sách mã câu hỏi trong đề:', 'bright_white', bold=True)}")
            codes_formatted = [f"• {c}" for c in codes]
            # In 3 cột
            for i in range(0, len(codes_formatted), 3):
                chunk = codes_formatted[i:i+3]
                print("    " + "   ".join([terminal.pad_string(c, 26) for c in chunk]))
            print()

        opts = []
        if pdf_p and pdf_p.exists():
            opts.append({"key": "1", "label": "Mở file PDF", "action": "open_pdf"})
        if tex_p and tex_p.exists():
            opts.append({"key": "2", "label": "Mở thư mục chứa file", "action": "open_folder"})
        opts.append({"key": "0", "label": "Quay lại danh sách", "action": "back"})

        c_idx = input_handler.select_menu(opts, title="THAO TÁC VỚI ĐỀ THI", width=width)
        if c_idx is None or opts[c_idx]["action"] == "back":
            break

        act = opts[c_idx]["action"]
        if act == "open_pdf" and pdf_p:
            latex_compiler.open_pdf(pdf_p)
        elif act == "open_folder" and tex_p:
            latex_compiler.open_folder(tex_p.parent)
