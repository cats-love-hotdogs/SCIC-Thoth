"""
config.py - Cấu hình hệ thống Thoth CLI.
Tự chứa 100% trong ICSC_CLI: có thư mục input, output, logs, data và templates riêng biệt.
Có thể di chuyển thư mục ICSC_CLI sang bất kỳ vị trí nào mà vẫn hoạt động độc lập.
"""

import os
from pathlib import Path

# ============================================================
# Thông tin ứng dụng
# ============================================================
APP_NAME = "Thoth"
APP_TITLE = "HỆ THỐNG TẠO ĐỀ & QUẢN LÝ NGÂN HÀNG CÂU HỎI THOTH"
APP_SUBTITLE = "Thoth Intelligent Exam System - Interactive CLI"
APP_VERSION = "2.0.0"

# ============================================================
# Đường dẫn thư mục tự chứa (Self-Contained Architecture)
# ============================================================
CLI_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CLI_DIR.parent

# 1. Thư mục Input / Output / Logs độc lập của Thoth
INPUT_DIR = CLI_DIR / "input"
OUTPUT_DIR = CLI_DIR / "output"
LOG_DIR = CLI_DIR / "logs"
CLI_LOG_FILE = LOG_DIR / "exam_history.json"
ROOT_LOG_FILE = PROJECT_ROOT / "logs" / "exam_history.json"

# Tự động khởi tạo các thư mục độc lập nếu chưa có
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 2. Dữ liệu ngân hàng câu hỏi (Ưu tiên nội bộ trong ICSC_CLI/data)
DATA_DIR = CLI_DIR / "data"
LOCAL_SORTED_DIR = DATA_DIR / "sorted"
PARENT_SORTED_DIR = PROJECT_ROOT / "Initializing" / "sorting" / "sorted"
SORTED_DIR = LOCAL_SORTED_DIR if LOCAL_SORTED_DIR.exists() else PARENT_SORTED_DIR

# 3. Từ điển Tags kiến thức
LOCAL_TAGS_FILE = DATA_DIR / "tags_01_v2.md"
PARENT_TAGS_FILE = PROJECT_ROOT / "resource" / "tags_01_v2.md"
TAGS_FILE = LOCAL_TAGS_FILE if LOCAL_TAGS_FILE.exists() else PARENT_TAGS_FILE

# 4. Thư mục Templates LaTeX
TEMPLATES_DIR = CLI_DIR / "templates"
TEMPLATE_MIDTERM_DIR = (TEMPLATES_DIR / "midterm") if (TEMPLATES_DIR / "midterm").exists() else (PROJECT_ROOT / "template_midterm")
TEMPLATE_FINAL_DIR = (TEMPLATES_DIR / "final") if (TEMPLATES_DIR / "final").exists() else (PROJECT_ROOT / "template_final_term")
TEMPLATE_PRACTICE_DIR = (TEMPLATES_DIR / "practice") if (TEMPLATES_DIR / "practice").exists() else (PROJECT_ROOT / "template_practice")

# 5. Pipeline OCR & Sorter độc lập
PIPELINE_DIR = CLI_DIR / "pipeline"
OCR_INPUT_DIR = INPUT_DIR
OCR_OUTPUT_DIR = DATA_DIR / "ocr_output"
OCR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OCR_SCRIPT = (PIPELINE_DIR / "OCR.py") if (PIPELINE_DIR / "OCR.py").exists() else (PROJECT_ROOT / "Initializing" / "OCR" / "OCR.py")
SORTER_SCRIPT = (PIPELINE_DIR / "SORTER.py") if (PIPELINE_DIR / "SORTER.py").exists() else (PROJECT_ROOT / "Initializing" / "sorting" / "SORTER.py")

OCR_ENV_FILE = (CLI_DIR / ".env") if (CLI_DIR / ".env").exists() else (PROJECT_ROOT / "Initializing" / "OCR" / ".env")
OCR_PROCESSED_LOG = DATA_DIR / ".ocr_processed.json"
SORTER_PROCESSED_LOG = DATA_DIR / ".sorter_processed.json"

# Cài đặt output mặc định
USE_INTERNAL_OUTPUT = True


def get_output_dir() -> Path:
    """Trả về thư mục output đang được kích hoạt."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def get_log_file() -> Path:
    """Trả về file log của CLI."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return CLI_LOG_FILE


# ============================================================
# Danh mục môn học
# ============================================================
SUBJECTS = {
    "1": {
        "key": "calculus_1",
        "display_name": "Calculus 1",
        "vn_name": "Giải tích 1",
        "folder": "calculus_1",
        "latex_cmd": "\\CalOne",
        "latex_code": "\\CalOneCode",
        "color": "cyan",
        "default_midterm_chapters": [1],
    },
    "2": {
        "key": "calculus_2",
        "display_name": "Calculus 2",
        "vn_name": "Giải tích 2",
        "folder": "calculus_2",
        "latex_cmd": "\\CalTwo",
        "latex_code": "\\CalTwoCode",
        "color": "blue",
        "default_midterm_chapters": [1, 2],
    },
    "3": {
        "key": "calculus_3",
        "display_name": "Calculus 3",
        "vn_name": "Giải tích 3",
        "folder": "calculus_3",
        "latex_cmd": "\\CalThree",
        "latex_code": "\\CalThreeCode",
        "color": "magenta",
        "default_midterm_chapters": [1],
    },
    "4": {
        "key": "algebra",
        "display_name": "Algebra",
        "vn_name": "Đại số tuyến tính",
        "folder": "algebra",
        "latex_cmd": "\\Algebra",
        "latex_code": "\\AlgebraCode",
        "color": "yellow",
        "default_midterm_chapters": [1, 2],
    },
}

SUBJECT_BY_FOLDER = {info["folder"]: info for info in SUBJECTS.values()}

# ============================================================
# Danh mục loại đề thi
# ============================================================
EXAM_TYPES = {
    "1": {
        "key": "midterm",
        "name": "Giữa kỳ (Midterm)",
        "badge": "[ Giữa kỳ ]",
        "spec": "15 câu (10 MCQ_SA + 5 TFQ/MCQ_MA)",
        "default_code": "102",
        "description": "Đề thi giữa kỳ trắc nghiệm chuẩn BK, giới hạn theo chương đầu",
    },
    "2": {
        "key": "final",
        "name": "Cuối kỳ (Final)",
        "badge": "[ Cuối kỳ ]",
        "spec": "Tự luận FRQ (Chuẩn 10 điểm, ≥50% câu 1 điểm)",
        "default_code": "1",
        "description": "Đề thi cuối kỳ tự luận chuẩn BK, phủ toàn bộ chương trình",
    },
    "3": {
        "key": "practice",
        "name": "Tự luyện (Practice)",
        "badge": "[ Tự luyện ]",
        "spec": "Tùy chọn lọc theo Chương / Tags kiến thức",
        "default_code": "PRACTICE",
        "description": "Bộ câu hỏi ôn tập chuyên sâu theo từng chủ đề hoặc toàn diện",
    },
}

# ============================================================
# Cấu hình đề thi chi tiết
# ============================================================
MIDTERM_PART1_COUNT = 10     # 10 câu trắc nghiệm đơn đáp án (MCQ_SA)
MIDTERM_PART2_COUNT = 5      # 5 câu đúng/sai hoặc nhiều đáp án (TFQ, MCQ_MA)
MIDTERM_TOTAL_COUNT = 15     # Tổng 15 câu

FINAL_TOTAL_POINTS = 10      # Tổng 10 điểm
FINAL_MAX_FRQ_MP_PARTS = 2   # Câu tự luận nhiều ý chỉ tối đa 2 ý a, b

LOG_HISTORY_SIZE = 10        # Giữ 10 đề gần nhất để deduplication câu hỏi

MCQ_TYPES = {"MCQ_SA", "MCQ_MA", "TFQ"}
FRQ_TYPES = {"FRQ_SP", "FRQ_MP"}
