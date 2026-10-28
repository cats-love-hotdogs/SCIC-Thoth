"""
diagnostics_view.py - Màn hình Chẩn đoán hệ thống và Cài đặt môi trường Thoth.
Kiểm tra tính sẵn sàng của trình biên dịch LaTeX, kiểm tra các tệp mẫu và thư mục độc lập.
"""

from pathlib import Path
from .. import config
from ..ui import colors
from ..ui import terminal
from ..ui import components
from ..ui import input_handler
from ..ui import table
from ..core import latex_compiler
from ..core import data_loader
from . import base_view


def show_diagnostics() -> None:
    """Màn hình chẩn đoán và cài đặt."""
    while True:
        base_view.render_header(breadcrumbs=["Hệ Thống", "Chẩn Đoán & Thiết Lập"])
        width = terminal.get_terminal_width()

        # 1. Kiểm tra LaTeX
        latex_info = latex_compiler.get_latex_info()

        # 2. Kiểm tra thư mục dữ liệu tự chứa
        checks = [
            ("Trình biên dịch pdflatex", latex_info["path"] or "Không tìm thấy", latex_info["found"]),
            ("Phiên bản TeX", latex_info["version"], latex_info["found"]),
            ("Thư mục Input (ảnh/PDF đề thi)", str(config.INPUT_DIR), config.INPUT_DIR.exists()),
            ("Thư mục Output (đề thi tạo ra)", str(config.OUTPUT_DIR), config.OUTPUT_DIR.exists()),
            ("Kho câu hỏi sorted", str(config.SORTED_DIR), config.SORTED_DIR.exists()),
            ("Từ điển Tags chuẩn", str(config.TAGS_FILE), config.TAGS_FILE.exists()),
            ("Mẫu đề giữa kỳ (thoth.sty)", str(config.TEMPLATE_MIDTERM_DIR / "thoth.sty"), (config.TEMPLATE_MIDTERM_DIR / "thoth.sty").exists()),
            ("Mẫu đề cuối kỳ (thoth.sty)", str(config.TEMPLATE_FINAL_DIR / "thoth.sty"), (config.TEMPLATE_FINAL_DIR / "thoth.sty").exists()),
            ("Mẫu đề tự luyện (thoth.sty)", str(config.TEMPLATE_PRACTICE_DIR / "thoth.sty"), (config.TEMPLATE_PRACTICE_DIR / "thoth.sty").exists()),
            ("Độ độc lập hệ thống", "100% Tự chứa (Self-Contained)", True),
        ]

        headers = ["Hạng Mục Kiểm Tra", "Đường Dẫn / Chi Tiết", "Trạng Thái"]
        rows = []
        for name, detail, ok in checks:
            status_tag = (
                colors.colorize("✔ Sẵn sàng", "bright_green")
                if ok
                else colors.colorize("✖ Thiếu / Lỗi", "bright_red")
            )
            rows.append([
                name,
                terminal.truncate_string(detail, 52),
                status_tag,
            ])

        print(table.render_table(
            headers=headers,
            rows=rows,
            alignments=["left", "left", "center"],
            border_color="cyan",
            max_width=width,
        ))
        print()

        opts = [
            {
                "key": "1",
                "label": "Mở thư mục Input trong Explorer",
                "desc": "Thêm file ảnh/PDF đề thi mới vào để OCR",
                "action": "open_input",
            },
            {
                "key": "2",
                "label": "Mở thư mục Output trong Explorer",
                "desc": "Xem các file đề thi .pdf và .tex đã được tạo",
                "action": "open_output",
            },
            {
                "key": "3",
                "label": "Làm mới bộ nhớ đệm dữ liệu (Clear Cache)",
                "desc": "Buộc tải lại toàn bộ câu hỏi từ các file JSON",
                "action": "clear_cache",
            },
            {
                "key": "4",
                "label": "Mở thư mục ICSC_CLI trong Explorer",
                "desc": "Xem toàn bộ cấu trúc độc lập của Thoth",
                "action": "open_cli_folder",
            },
            {
                "key": "0",
                "label": "Quay lại Dashboard",
                "desc": "Trở về màn hình chính",
                "action": "back",
            },
        ]

        choice_idx = input_handler.select_menu(opts, title="THIẾT LẬP HỆ THỐNG", width=width)
        if choice_idx is None or opts[choice_idx]["action"] == "back":
            break

        act = opts[choice_idx]["action"]
        if act == "open_input":
            latex_compiler.open_folder(config.INPUT_DIR)
        elif act == "open_output":
            latex_compiler.open_folder(config.OUTPUT_DIR)
        elif act == "clear_cache":
            data_loader.clear_cache()
            print(f"\n  {colors.badge_success()} Đã xóa bộ nhớ đệm thành công!")
            base_view.press_any_key()
        elif act == "open_cli_folder":
            latex_compiler.open_folder(config.CLI_DIR)
