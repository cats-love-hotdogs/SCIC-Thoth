"""
tags_view.py - Màn hình trực quan hóa Ma trận kiến thức & Độ phủ Tags (Knowledge Matrix).
Tra cứu cây tags chuẩn, tỷ lệ bao phủ của ngân hàng câu hỏi và xem trực tiếp các câu hỏi thuộc từng Tag.
"""

from .. import config
from ..ui import colors
from ..ui import terminal
from ..ui import components
from ..ui import input_handler
from ..ui import table
from ..core import data_loader
from ..core import tag_manager
from . import base_view
from .explorer_view import _paginate_questions


def show_tags_matrix() -> None:
    """Màn hình chính của Ma trận kiến thức."""
    while True:
        base_view.render_header(breadcrumbs=["Ma Trận Kiến Thức", "Chọn Môn"])
        width = terminal.get_terminal_width()

        options = [
            {"key": "1", "label": "Calculus 1 (Giải tích 1)", "desc": "Xem cây tags và độ phủ môn Giải tích 1", "folder": "calculus_1"},
            {"key": "2", "label": "Algebra (Đại số tuyến tính)", "desc": "Xem cây tags và độ phủ môn Đại số", "folder": "algebra"},
            {"key": "0", "label": "Quay lại Dashboard", "desc": "Trở về màn hình chính", "folder": None},
        ]

        choice_idx = input_handler.select_menu(options, title="CHỌN MÔN HỌC TRA CỨU MA TRẬN TAGS", width=width)
        if choice_idx is None or options[choice_idx]["folder"] is None:
            break

        folder = options[choice_idx]["folder"]
        subj_name = options[choice_idx]["label"]
        _show_subject_tags(folder, subj_name)


def _show_subject_tags(subject_folder: str, subject_name: str) -> None:
    """Hiển thị chi tiết bảng tags, thanh độ phủ kiến thức và cho phép xem câu hỏi theo tag."""
    while True:
        base_view.render_header(breadcrumbs=["Ma Trận Kiến Thức", subject_name])
        width = terminal.get_terminal_width()

        all_q = data_loader.load_all_chapters(subject_folder)
        cov_stats = tag_manager.get_tag_coverage_stats(subject_folder, all_q)
        ref = tag_manager.get_tags_reference().get(subject_folder, [])

        if not ref:
            print(f"  {colors.badge_info()} Chưa có thông tin tham chiếu tags chuẩn cho môn {subject_name} trong resource/tags_01_v2.md.")
            base_view.press_any_key()
            return

        # Thanh tiến trình độ phủ
        cov_bar = components.progress_bar(
            cov_stats["covered_tags_count"], cov_stats["total_tags"], width=30
        )
        print(f"  {colors.colorize('TỶ LỆ BAO PHỦ KIẾN THỨC:', 'bright_white', bold=True)} {cov_bar}")
        covered_cnt = cov_stats["covered_tags_count"]
        total_cnt = cov_stats["total_tags"]
        missing_cnt = cov_stats["missing_tags_count"]
        desc_msg = f"Đã có câu hỏi cho {covered_cnt}/{total_cnt} tags chuẩn. Còn thiếu {missing_cnt} tags."
        print(f"  {colors.colorize(desc_msg, 'gray')}")
        print()

        # Bảng chi tiết
        headers = ["Chương", "Mã Tag Chuẩn", "Mô Tả Chủ Đề Kiến Thức", "Số Câu Trong Kho", "Trạng Thái"]
        rows = []
        all_tags_list = []

        for ch_info in ref:
            ch_title = ch_info.get("chapter", "Chapter")
            for item in ch_info.get("tags", []):
                if isinstance(item, dict):
                    t_code = item.get("tag", "")
                    t_desc = item.get("desc", t_code)
                else:
                    t_code = str(item)
                    t_desc = t_code

                all_tags_list.append(t_code)
                cnt = cov_stats["counts"].get(t_code, 0)
                status_badge = (
                    colors.colorize("✔ Đã phủ", "bright_green")
                    if cnt > 0
                    else colors.colorize("✖ Trống", "bright_red")
                )
                rows.append([
                    ch_title,
                    colors.colorize(t_code, "cyan"),
                    t_desc,
                    colors.colorize(str(cnt), "bright_yellow" if cnt > 0 else "gray", bold=(cnt > 0)),
                    status_badge,
                ])

        print(table.render_table(
            headers=headers,
            rows=rows,
            alignments=["left", "left", "left", "center", "center"],
            border_color="cyan",
            max_width=width,
        ))
        print()

        menu_opts = [
            {
                "key": "1",
                "label": "Xem danh sách câu hỏi theo Tag",
                "desc": "Nhập mã tag để duyệt các câu hỏi tương ứng trong ngân hàng",
                "badge": "Xem câu hỏi",
                "action": "view_tag",
            },
            {
                "key": "0",
                "label": "Quay lại danh sách môn học",
                "desc": "Trở về lựa chọn môn học",
                "badge": "Quay lại",
                "action": "back",
            },
        ]

        choice_idx = input_handler.select_menu(menu_opts, title="THAO TÁC MA TRẬN TAGS", width=width)
        if choice_idx is None or menu_opts[choice_idx]["action"] == "back":
            break

        if menu_opts[choice_idx]["action"] == "view_tag":
            tag_input = input_handler.prompt_text("Nhập mã Tag cần xem câu hỏi (vd: c1_curve_sketching, c1_derivatives)")
            if not tag_input:
                continue

            tag_query = tag_input.strip().lower()
            matched_q = [
                q for q in all_q
                if any(tag_query in t.lower() for t in q.get("section_tags", []))
            ]

            if not matched_q:
                print(f"\n  {colors.badge_warn()} Không có câu hỏi nào khớp với tag '{tag_input}' trong môn {subject_name}!")
                base_view.press_any_key()
                continue

            print(f"\n  {colors.badge_success()} Tìm thấy {len(matched_q)} câu hỏi thuộc tag '{tag_input}'!")
            base_view.press_any_key("Nhấn phím bất kỳ để duyệt câu hỏi...")
            _paginate_questions(matched_q, f"{subject_name} • #{tag_input}")
