"""
ingestion_view.py - Màn hình điều phối Pipeline thu thập dữ liệu (OCR và SORTER).
Kiểm tra file đề thi đầu vào, trạng thái Gemini API và thực thi pipeline trực quan.
"""

from typing import Optional
from .. import config
from ..ui import colors
from ..ui import terminal
from ..ui import components
from ..ui import input_handler
from ..ui import table
from ..core import pipeline_service
from ..core import latex_compiler
from . import base_view


def show_ingestion() -> None:
    """Màn hình chính của Ingestion Pipeline."""
    while True:
        base_view.render_header(breadcrumbs=["Thu Thập Dữ Liệu", "OCR & Sorter"])
        width = terminal.get_terminal_width()

        # 1. Trạng thái API
        api_info = pipeline_service.check_api_key_status()
        api_status_str = (
            f"{colors.colorize('● Đã cấu hình', 'bright_green')} ({api_info['source']}: {api_info['masked_key']})"
            if api_info["configured"]
            else colors.colorize("● Chưa có khóa API (Đặt trong Initializing/OCR/.env)", "bright_red")
        )

        print(f"  {colors.colorize('Khóa Gemini API:', 'bright_white', bold=True)} {api_status_str}")
        print()

        # 2. Danh sách file đầu vào
        files = pipeline_service.get_input_files_status()
        if not files:
            print(f"  {colors.badge_info()} Thư mục đầu vào {config.OCR_INPUT_DIR} hiện đang trống.")
            print(f"  {colors.colorize('Vui lòng bỏ ảnh (.png, .jpg) hoặc file PDF đề thi vào thư mục trên.', 'gray')}")
        else:
            headers = ["STT", "Tên File Đề Thi", "Định Dạng", "Dung Lượng", "Trạng Thái Xử Lý"]
            rows = []
            for i, f in enumerate(files, 1):
                status_tag = (
                    colors.colorize("✔ Đã OCR", "bright_green")
                    if f["is_processed"]
                    else colors.colorize("⚡ Chờ xử lý", "bright_yellow", bold=True)
                )
                rows.append([
                    str(i),
                    f["name"],
                    f["ext"].upper(),
                    f["size_kb"],
                    status_tag,
                ])

            print(table.render_table(
                headers=headers,
                rows=rows,
                alignments=["center", "left", "center", "center", "center"],
                border_color="cyan",
                max_width=width,
            ))

        print()

        # 3. Menu thao tác
        options = [
            {
                "key": "1",
                "label": "Chạy OCR cho các file mới",
                "desc": "Chỉ quét các file chưa được đánh dấu đã xử lý",
                "badge": "OCR Mới",
                "action": "ocr_new",
            },
            {
                "key": "2",
                "label": "Chạy OCR xử lý lại toàn bộ file (--reprocess)",
                "desc": "Quét lại tất cả các file ảnh/PDF trong thư mục input",
                "badge": "Toàn bộ",
                "action": "ocr_all",
            },
            {
                "key": "3",
                "label": "Chỉ chạy SORTER (Phân loại vào chapters)",
                "desc": "Đọc JSON từ OCR output và phân loại vào các chapter môn học",
                "badge": "Sorter",
                "action": "sorter_only",
            },
            {
                "key": "4",
                "label": "Chạy toàn bộ Pipeline (OCR Mới → Sorter)",
                "desc": "Tự động OCR file mới rồi phân loại ngay lập tức",
                "badge": "Full Flow",
                "action": "full_pipeline",
            },
            {
                "key": "5",
                "label": "Mở thư mục Input trong Explorer",
                "desc": "Thêm nhanh file đề thi ảnh/PDF vào thư mục quét",
                "badge": "Folder",
                "action": "open_input",
            },
            {
                "key": "0",
                "label": "Quay lại Dashboard",
                "desc": "Trở về màn hình chính",
                "badge": "Quay lại",
                "action": "back",
            },
        ]

        choice_idx = input_handler.select_menu(
            options=options,
            title="THAO TÁC THU THẬP & PHÂN LOẠI",
            width=width,
        )

        if choice_idx is None or options[choice_idx]["action"] == "back":
            break

        act = options[choice_idx]["action"]
        if act == "open_input":
            latex_compiler.open_folder(config.OCR_INPUT_DIR)
            continue

        if not api_info["configured"] and act in ("ocr_new", "ocr_all", "full_pipeline"):
            print(f"\n  {colors.badge_error()} Bạn cần cấu hình GEMINI_API_KEY trước khi chạy OCR!")
            base_view.press_any_key()
            continue

        _execute_pipeline_action(act)


def _execute_pipeline_action(action: str) -> None:
    """Thực thi thao tác pipeline được chọn kèm phản hồi trực quan."""
    base_view.render_header(breadcrumbs=["Thu Thập Dữ Liệu", "Đang Xử Lý Pipeline..."])
    print()
    print(f"  {colors.colorize('⚙ ĐANG TIẾN HÀNH CHẠY PIPELINE...', 'bright_yellow', bold=True)}")
    print(f"  {colors.colorize('Quá trình này có thể mất từ vài giây đến vài phút tùy theo số lượng ảnh.', 'gray')}")
    print()

    run_ocr = action in ("ocr_new", "ocr_all", "full_pipeline")
    run_sort = action in ("sorter_only", "full_pipeline")
    reprocess = (action == "ocr_all")

    result = pipeline_service.run_pipeline(
        run_ocr=run_ocr,
        run_sort=run_sort,
        reprocess=reprocess,
    )

    base_view.render_header(breadcrumbs=["Thu Thập Dữ Liệu", "Kết Quả Pipeline"])
    print()

    if run_ocr:
        if result["ocr_success"]:
            print(f"  {colors.badge_success(' OCR THÀNH CÔNG ')}")
        elif result["ocr_success"] is False:
            print(f"  {colors.badge_error(' OCR THẤT BẠI ')}")
            print(colors.colorize(result["ocr_output"][-400:], "bright_red"))
        print()

    if run_sort:
        if result["sorter_success"]:
            print(f"  {colors.badge_success(' PHÂN LOẠI SORTER THÀNH CÔNG ')}")
        elif result["sorter_success"] is False:
            print(f"  {colors.badge_error(' SORTER THẤT BẠI ')}")
            print(colors.colorize(result["sorter_output"][-400:], "bright_red"))
        print()

    # Xóa cache data_loader để cập nhật dữ liệu mới
    from ..core import data_loader
    data_loader.clear_cache()

    print(f"  {colors.colorize('✔ Dữ liệu ngân hàng câu hỏi đã được làm mới tự động.', 'bright_green')}")
    base_view.press_any_key()
