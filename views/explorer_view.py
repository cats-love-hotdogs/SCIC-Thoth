"""
explorer_view.py - Màn hình khám phá và duyệt ngân hàng câu hỏi toán học ICSC.
Hỗ trợ xem bảng thống kê số lượng câu, duyệt từng câu với công thức LaTeX và đáp án.
"""

from typing import List, Dict, Any, Optional
from .. import config
from ..ui import colors
from ..ui import terminal
from ..ui import components
from ..ui import input_handler
from ..ui import table
from ..ui import viewer
from ..core import data_loader
from . import base_view


def show_explorer() -> None:
    """Màn hình chính của Question Bank Explorer."""
    while True:
        base_view.render_header(breadcrumbs=["Ngân Hàng Câu Hỏi", "Tổng Quan"])
        width = terminal.get_terminal_width()

        stats = data_loader.get_stats_summary()

        # Bảng tổng quan các môn
        headers = ["STT", "Môn Học", "Số Chương", "Tổng Số Câu", "MCQ (Đơn)", "MCQ (Nhiều)", "Đúng/Sai", "Tự luận Đơn", "Tự luận Ý"]
        rows = []
        for idx, (f_name, s_data) in enumerate(stats["subjects"].items(), 1):
            ch_count = len(s_data["chapters"])
            rows.append([
                str(idx),
                f"{s_data['display_name']} ({s_data['vn_name']})",
                f"{ch_count} ch" if ch_count else "-",
                colors.colorize(str(s_data["total"]), "bright_yellow", bold=True),
                str(s_data["mcq_sa"]),
                str(s_data["mcq_ma"]),
                str(s_data["tfq"]),
                str(s_data["frq_sp"]),
                str(s_data["frq_mp"]),
            ])

        print(table.render_table(
            headers=headers,
            rows=rows,
            alignments=["center", "left", "center", "center", "center", "center", "center", "center", "center"],
            border_color="cyan",
            header_color="bright_white",
            max_width=width,
        ))
        print()

        # Menu thao tác
        options = [
            {
                "key": "1",
                "label": "Duyệt câu hỏi theo môn học & chương",
                "desc": "Xem chi tiết đề bài, công thức toán và các phương án",
                "badge": "Xem câu hỏi",
                "action": "browse",
            },
            {
                "key": "2",
                "label": "Tìm kiếm câu hỏi theo Tag",
                "desc": "Lọc danh sách các câu hỏi theo mã kiến thức",
                "badge": "Tìm kiếm",
                "action": "search",
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
            title="THAO TÁC KHÁM PHÁ NGÂN HÀNG CÂU HỎI",
            width=width,
        )

        if choice_idx is None or options[choice_idx]["action"] == "back":
            break

        act = options[choice_idx]["action"]
        if act == "browse":
            _browse_questions_flow()
        elif act == "search":
            _search_questions_flow()


def _browse_questions_flow() -> None:
    """Luồng chọn môn học và chương để duyệt câu hỏi."""
    width = terminal.get_terminal_width()

    # Chọn môn
    subj_opts = []
    for k, s in config.SUBJECTS.items():
        folder = s["folder"]
        all_q = data_loader.load_all_chapters(folder)
        subj_opts.append({
            "key": k,
            "label": f"{s['display_name']} ({s['vn_name']})",
            "desc": f"{len(all_q)} câu hỏi",
            "folder": folder,
            "name": s["display_name"],
        })
    subj_opts.append({"key": "0", "label": "Quay lại", "folder": None})

    s_idx = input_handler.select_menu(subj_opts, title="CHỌN MÔN HỌC ĐỂ DUYỆT", width=width)
    if s_idx is None or subj_opts[s_idx]["folder"] is None:
        return

    folder = subj_opts[s_idx]["folder"]
    subj_name = subj_opts[s_idx]["name"]

    # Chọn chương
    chapters = data_loader.get_available_chapters(folder)
    if not chapters:
        print(f"\n  {colors.badge_warn()} Môn này chưa có file chapter nào!")
        base_view.press_any_key()
        return

    ch_opts = []
    for ch in chapters:
        q_list = data_loader.load_chapter(folder, ch)
        ch_opts.append({
            "key": str(ch),
            "label": f"Chương {ch} (Chapter {ch})",
            "desc": f"{len(q_list)} câu hỏi",
            "ch_num": ch,
        })
    ch_opts.append({
        "key": "A",
        "label": "Tất cả các chương (All chapters)",
        "desc": "Tải toàn bộ câu hỏi của môn",
        "ch_num": "all",
    })
    ch_opts.append({"key": "0", "label": "Quay lại", "ch_num": None})

    ch_idx = input_handler.select_menu(ch_opts, title=f"CHỌN CHƯƠNG ({subj_name})", width=width)
    if ch_idx is None or ch_opts[ch_idx]["ch_num"] is None:
        return

    chosen_ch = ch_opts[ch_idx]["ch_num"]
    if chosen_ch == "all":
        questions = data_loader.load_all_chapters(folder)
        title_context = f"{subj_name} - Tất cả các chương"
    else:
        questions = data_loader.load_chapter(folder, chosen_ch)
        title_context = f"{subj_name} - Chương {chosen_ch}"

    if not questions:
        print(f"\n  {colors.badge_warn()} Không có câu hỏi nào trong mục đã chọn!")
        base_view.press_any_key()
        return

    # Duyệt từng câu (Pagination)
    _paginate_questions(questions, title_context)


def _paginate_questions(questions: List[Dict[str, Any]], context_title: str) -> None:
    """Trình lật trang câu hỏi tương tác."""
    current_idx = 0
    total = len(questions)
    width = terminal.get_terminal_width()

    while True:
        base_view.render_header(breadcrumbs=["Ngân Hàng Câu Hỏi", context_title, f"Câu {current_idx + 1}/{total}"])

        q = questions[current_idx]
        print(viewer.render_question_detail(q, index=current_idx + 1, width=width))
        print()

        nav_options = [
            {"key": "n", "label": "Câu tiếp theo [Next ▶]", "action": "next"},
            {"key": "p", "label": "Câu trước đó [◀ Prev]", "action": "prev"},
            {"key": "j", "label": "Nhảy tới số câu [Jump]", "action": "jump"},
            {"key": "0", "label": "Thoát trình xem", "action": "exit"},
        ]

        choice_idx = input_handler.select_menu(
            options=nav_options,
            title=f"ĐIỀU HƯỚNG CÂU HỎI ({current_idx + 1}/{total})",
            prompt_help="Nhấn [n] xem câu sau, [p] xem câu trước, [j] nhảy số câu, [0/Esc] thoát",
            width=width,
        )

        if choice_idx is None or nav_options[choice_idx]["action"] == "exit":
            break

        act = nav_options[choice_idx]["action"]
        if act == "next":
            current_idx = (current_idx + 1) % total
        elif act == "prev":
            current_idx = (current_idx - 1) % total
        elif act == "jump":
            val = input_handler.prompt_text(f"Nhập số câu (1 - {total})", default=str(current_idx + 1))
            try:
                num = int(val)
                if 1 <= num <= total:
                    current_idx = num - 1
            except ValueError:
                pass


def _search_questions_flow() -> None:
    """Tìm kiếm câu hỏi theo từ khóa trong Tag."""
    base_view.render_header(breadcrumbs=["Ngân Hàng Câu Hỏi", "Tìm Kiếm Tag"])
    tag_keyword = input_handler.prompt_text("Nhập từ khóa tag cần tìm (vd: dao_ham, tich_phan, c1)")
    if not tag_keyword:
        return

    tag_keyword = tag_keyword.lower()
    matched_questions = []

    for f_name in config.SUBJECT_BY_FOLDER.keys():
        all_q = data_loader.load_all_chapters(f_name)
        for q in all_q:
            tags = [t.lower() for t in q.get("section_tags", [])]
            if any(tag_keyword in t for t in tags):
                matched_questions.append(q)

    if not matched_questions:
        print(f"\n  {colors.badge_warn()} Không tìm thấy câu hỏi nào khớp với từ khóa '{tag_keyword}'!")
        base_view.press_any_key()
        return

    print(f"\n  {colors.badge_success()} Tìm thấy {len(matched_questions)} câu hỏi phù hợp!")
    base_view.press_any_key("Nhấn phím bất kỳ để duyệt các câu hỏi tìm được...")
    _paginate_questions(matched_questions, f"Kết quả tìm kiếm '{tag_keyword}'")
