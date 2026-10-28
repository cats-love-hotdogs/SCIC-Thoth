"""
home_view.py - Màn hình chính Dashboard trực quan của ICSC CLI.
Hiển thị tổng quan trạng thái hệ thống, kho câu hỏi và menu điều hướng chính.
"""

from typing import Optional
from .. import config
from ..ui import colors
from ..ui import terminal
from ..ui import components
from ..ui import input_handler
from ..core import data_loader
from ..core import latex_compiler
from ..core import pipeline_service
from . import base_view


def show_home() -> Optional[str]:
    """
    Hiển thị giao diện Dashboard chính.
    Returns: action_key được người dùng chọn ('exam', 'explorer', 'ingestion', 'history', 'tags', 'settings', 'exit').
    """
    base_view.render_header(breadcrumbs=["Dashboard"], show_banner=True)
    width = terminal.get_terminal_width()

    # 1. Thu thập dữ liệu trạng thái
    stats = data_loader.get_stats_summary()
    total_q = stats["total_questions"]

    latex_info = latex_compiler.get_latex_info()
    api_info = pipeline_service.check_api_key_status()

    # 2. Vẽ bảng trạng thái hệ thống (Quick Status Bar)
    compiler_badge = (
        colors.badge_success("LaTeX: Sẵn sàng")
        if latex_info["found"]
        else colors.badge_warn("LaTeX: Chưa cài")
    )

    api_badge = (
        colors.badge_success("Gemini API: Đã kết nối")
        if api_info["configured"]
        else colors.badge_warn("Gemini API: Chưa có key")
    )

    q_badge = colors.badge(f"Ngân hàng: {total_q} câu hỏi", bg_color="cyan", fg_color="black")

    status_line = f"  {q_badge}   {compiler_badge}   {api_badge}"
    print(status_line)
    print()

    # 3. Menu điều hướng chính
    menu_options = [
        {
            "key": "1",
            "icon": "🎓",
            "label": "Tạo Đề Thi Tự Động (Exam Generator)",
            "desc": "Tạo đề Giữa kỳ, Cuối kỳ hoặc Tự luyện kèm biên dịch PDF tự động",
            "badge": "Chính",
            "action": "exam",
        },
        {
            "key": "2",
            "icon": "📊",
            "label": "Khám Phá Ngân Hàng Câu Hỏi (Question Explorer)",
            "desc": "Xem thống kê, duyệt chi tiết câu hỏi theo môn/chương/dạng bài",
            "badge": f"{total_q} câu",
            "action": "explorer",
        },
        {
            "key": "3",
            "icon": "⚡",
            "label": "Thu Thập & Phân Loại Câu Hỏi (OCR & Sorter)",
            "desc": "Quét ảnh/PDF đề thi qua Gemini AI và tự động sắp xếp vào kho",
            "badge": "Pipeline",
            "action": "ingestion",
        },
        {
            "key": "4",
            "icon": "📜",
            "label": "Lịch Sử Đề Thi Đã Tạo (Exam History)",
            "desc": "Xem danh sách các đề thi gần nhất và mở nhanh file PDF/TeX",
            "badge": "Lịch sử",
            "action": "history",
        },
        {
            "key": "5",
            "icon": "🏷️",
            "label": "Ma Trận Kiến Thức & Tags (Knowledge Matrix)",
            "desc": "Tra cứu cây tags chuẩn, độ phủ kiến thức và các chủ đề còn thiếu",
            "badge": "Tags",
            "action": "tags",
        },
        {
            "key": "6",
            "icon": "⚙️",
            "label": "Chẩn Đoán & Thiết Lập (Diagnostics & Settings)",
            "desc": "Kiểm tra môi trường MiKTeX, đường dẫn lưu file và dọn dẹp cache",
            "badge": "Hệ thống",
            "action": "settings",
        },
        {
            "key": "0",
            "icon": "🚪",
            "label": "Thoát chương trình",
            "desc": "Đóng ứng dụng ICSC Terminal",
            "badge": "Thoát",
            "action": "exit",
        },
    ]

    choice_idx = input_handler.select_menu(
        options=menu_options,
        title="MENU ĐIỀU KHIỂN CHÍNH",
        prompt_help="Dùng [↑/↓] hoặc bấm số [1-6], nhấn [Enter] để vào tính năng, [0/q] để thoát",
        width=width,
    )

    if choice_idx is None:
        return "exit"

    return menu_options[choice_idx]["action"]
