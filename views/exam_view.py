"""
exam_view.py - Wizard tạo đề thi tương tác trực quan (Giữa kỳ, Cuối kỳ, Tự luyện).
Hỗ trợ xem trước thông số, tiến trình tạo sinh động và mở trực tiếp file PDF.
"""

import sys
import time
from typing import Optional, List
from pathlib import Path

from .. import config
from ..ui import colors
from ..ui import terminal
from ..ui import components
from ..ui import input_handler
from ..ui import table
from ..core import data_loader
from ..core import exam_service
from ..core import latex_compiler
from ..core import tag_manager
from . import base_view


def show_exam_generator() -> None:
    """Điều phối luồng Wizard tạo đề thi."""
    while True:
        base_view.render_header(breadcrumbs=["Tạo Đề Thi", "Bước 1: Chọn Môn Học"])
        width = terminal.get_terminal_width()

        # ----------------------------------------------------
        # Bước 1: Chọn môn học
        # ----------------------------------------------------
        subject_options = []
        for key, s_info in config.SUBJECTS.items():
            folder = s_info["folder"]
            chapters = data_loader.get_available_chapters(folder)
            all_q = data_loader.load_all_chapters(folder)
            ch_str = f"{len(chapters)} chương" if chapters else "Trống"
            q_str = f"{len(all_q)} câu hỏi" if all_q else "Chưa có dữ liệu"

            subject_options.append({
                "key": key,
                "label": f"{s_info['display_name']} ({s_info['vn_name']})",
                "desc": f"Kho dữ liệu: {ch_str} • {q_str}",
                "badge": s_info["key"].upper(),
                "folder": folder,
                "info": s_info,
                "total_q": len(all_q),
            })

        subject_options.append({
            "key": "0",
            "label": "Quay lại Dashboard",
            "desc": "Trở về màn hình chính",
            "badge": "Quay lại",
            "folder": None,
        })

        s_idx = input_handler.select_menu(
            options=subject_options,
            title="BƯỚC 1: CHỌN MÔN HỌC",
            prompt_help="Dùng [↑/↓] hoặc bấm số để chọn môn học cần tạo đề",
            width=width,
        )

        if s_idx is None or subject_options[s_idx]["folder"] is None:
            break

        selected_subject = subject_options[s_idx]
        folder_name = selected_subject["folder"]

        if selected_subject["total_q"] == 0:
            print(f"\n  {colors.colorize('✖ CẢNH BÁO:', 'bright_red', bold=True)} Môn {selected_subject['label']} chưa có câu hỏi nào trong kho dữ liệu!")
            base_view.press_any_key()
            continue

        # ----------------------------------------------------
        # Bước 2: Chọn loại đề thi
        # ----------------------------------------------------
        base_view.render_header(breadcrumbs=["Tạo Đề Thi", selected_subject["info"]["display_name"], "Bước 2: Chọn Loại Đề"])

        type_options = []
        for key, t_info in config.EXAM_TYPES.items():
            type_options.append({
                "key": key,
                "label": t_info["name"],
                "desc": f"{t_info['spec']} - {t_info['description']}",
                "badge": t_info["badge"],
                "type_key": t_info["key"],
                "info": t_info,
            })

        type_options.append({
            "key": "0",
            "label": "Quay lại chọn môn học",
            "desc": "Trở về bước trước",
            "badge": "Quay lại",
            "type_key": None,
        })

        t_idx = input_handler.select_menu(
            options=type_options,
            title=f"BƯỚC 2: CHỌN LOẠI ĐỀ THI ({selected_subject['info']['display_name']})",
            width=width,
        )

        if t_idx is None or type_options[t_idx]["type_key"] is None:
            continue

        selected_type = type_options[t_idx]
        exam_type_key = selected_type["type_key"]

        # ----------------------------------------------------
        # Bước 3: Cấu hình thông số đề thi
        # ----------------------------------------------------
        base_view.render_header(breadcrumbs=["Tạo Đề Thi", selected_subject["info"]["display_name"], selected_type["info"]["name"], "Bước 3: Cấu Hình"])

        print(colors.colorize("  📋 THIẾT LẬP THÔNG SỐ ĐỀ THI", "bright_cyan", bold=True))
        print()

        default_code = selected_type["info"]["default_code"]
        exam_code = default_code

        if exam_type_key != "practice":
            exam_code = input_handler.prompt_text("Nhập mã đề thi", default=default_code)

        auto_compile = input_handler.confirm("Tự động biên dịch sang PDF bằng LaTeX?", default=True)

        selected_tags: Optional[List[str]] = None
        practice_count: Optional[int] = None

        if exam_type_key == "practice":
            # Cho phép lọc tags
            all_q = data_loader.load_all_chapters(folder_name)
            tag_counts = tag_manager.count_questions_per_tag(all_q)
            sorted_tags = sorted(tag_counts.keys())

            filter_tags = input_handler.confirm("Bạn có muốn chọn các tags kiến thức cụ thể không?", default=False)
            if filter_tags and sorted_tags:
                tag_items = []
                for t in sorted_tags:
                    tag_items.append({
                        "label": t,
                        "desc": f"{tag_counts[t]} câu hỏi",
                    })

                tag_indices = input_handler.multi_select_menu(
                    items=tag_items,
                    title="CHỌN CÁC TAGS KIẾN THỨC CẦN ÔN TẬP",
                    width=width,
                )
                if tag_indices:
                    selected_tags = [sorted_tags[i] for i in tag_indices]

            limit_count = input_handler.confirm("Bạn có muốn giới hạn số lượng câu hỏi không?", default=False)
            if limit_count:
                count_str = input_handler.prompt_text("Nhập số lượng câu", default="15")
                try:
                    practice_count = int(count_str)
                except ValueError:
                    practice_count = 15

        # ----------------------------------------------------
        # Bước 4: Tiến trình tạo đề
        # ----------------------------------------------------
        base_view.render_header(breadcrumbs=["Tạo Đề Thi", selected_subject["info"]["display_name"], "Đang xử lý..."])
        print()
        print(f"  {colors.colorize('🚀 ĐANG KHỞI TẠO ĐỀ THI...', 'bright_yellow', bold=True)}")
        print()

        def update_progress(msg: str, pct: float):
            p_bar = components.progress_bar(int(pct * 100), 100, width=30)
            sys.stdout.write(f"\r  {p_bar}  {colors.colorize(msg, 'bright_cyan')}        ")
            sys.stdout.flush()

        result = None
        try:
            if exam_type_key == "midterm":
                result = exam_service.generate_midterm(
                    subject_folder=folder_name,
                    exam_code=exam_code,
                    auto_compile=auto_compile,
                    progress_callback=update_progress,
                )
            elif exam_type_key == "final":
                result = exam_service.generate_final(
                    subject_folder=folder_name,
                    exam_code=exam_code,
                    auto_compile=auto_compile,
                    progress_callback=update_progress,
                )
            elif exam_type_key == "practice":
                result = exam_service.generate_practice(
                    subject_folder=folder_name,
                    selected_tags=selected_tags,
                    count=practice_count,
                    exam_code=exam_code,
                    auto_compile=auto_compile,
                    progress_callback=update_progress,
                )
        except Exception as e:
            result = {"success": False, "error": str(e)}

        print("\n")

        # ----------------------------------------------------
        # Bước 5: Kết quả tạo đề
        # ----------------------------------------------------
        if not result or not result.get("success"):
            err_msg = result.get("error", "Lỗi không xác định") if result else "Không có kết quả"
            print(f"  {colors.badge_error()} {colors.colorize(err_msg, 'bright_red')}")
            base_view.press_any_key()
            continue

        base_view.render_header(breadcrumbs=["Tạo Đề Thi", "Hoàn Tất ★"])

        print(f"  {colors.badge_success(' TẠO ĐỀ THI THÀNH CÔNG! ')}")
        print()

        summary_rows = [
            ("Môn học", f"{selected_subject['info']['display_name']} ({selected_subject['info']['vn_name']})"),
            ("Loại đề thi", selected_type["info"]["name"]),
            ("Mã đề thi", exam_code),
            ("Số lượng câu", f"{result.get('total_count', len(result.get('questions', [])))} câu"),
        ]

        if "total_points" in result:
            summary_rows.append(("Tổng điểm đề", f"{result['total_points']} điểm (Chuẩn Bách Khoa)"))
        if "part1_count" in result and "part2_count" in result:
            summary_rows.append(("Phân bổ", f"Phần I: {result['part1_count']} câu | Phần II: {result['part2_count']} câu"))

        summary_rows.append(("Độ phủ Tags", f"{len(result.get('covered_tags', []))} tags kiến thức"))
        summary_rows.append(("File mã nguồn .tex", str(result["tex_path"])))

        if result.get("pdf_path"):
            summary_rows.append(("File tài liệu .pdf", str(result["pdf_path"])))
        else:
            summary_rows.append(("File PDF", colors.colorize("Chưa biên dịch PDF", "gray")))

        print(components.key_value_card(summary_rows, title="THÔNG TIN ĐỀ THI ĐÃ TẠO"))
        print()

        # Menu thao tác sau khi tạo xong
        post_options = []
        if result.get("pdf_path"):
            post_options.append({
                "key": "1",
                "label": "Mở file PDF ngay",
                "desc": "Xem trực tiếp đề thi trên trình đọc PDF của hệ thống",
                "badge": "PDF",
                "action": "open_pdf",
            })

        post_options.append({
            "key": "2",
            "label": "Mở thư mục chứa file đề thi",
            "desc": "Mở trong Windows File Explorer",
            "badge": "Explorer",
            "action": "open_folder",
        })

        post_options.append({
            "key": "3",
            "label": "Tạo đề thi khác",
            "desc": "Bắt đầu tạo lượt đề mới",
            "badge": "Tiếp tục",
            "action": "again",
        })

        post_options.append({
            "key": "0",
            "label": "Quay về Dashboard chính",
            "desc": "Kết thúc phiên tạo đề",
            "badge": "Hoàn tất",
            "action": "home",
        })

        while True:
            post_idx = input_handler.select_menu(
                options=post_options,
                title="THAO TÁC TIẾP THEO",
                width=width,
            )

            if post_idx is None:
                return

            act = post_options[post_idx]["action"]
            if act == "open_pdf" and result.get("pdf_path"):
                latex_compiler.open_pdf(result["pdf_path"])
            elif act == "open_folder":
                latex_compiler.open_folder(result["tex_path"].parent)
            elif act == "again":
                break
            elif act == "home":
                return
