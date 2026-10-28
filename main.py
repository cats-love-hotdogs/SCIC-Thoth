#!/usr/bin/env python3
"""
main.py - Điểm khởi chạy chính (Entry Point) cho ứng dụng Thoth CLI.
Hoạt động 100% độc lập, có thể di chuyển thư mục ICSC_CLI sang bất kỳ vị trí nào.

Cách sử dụng:
    python main.py
    python thoth.py
    thoth
"""

import sys
import os
import types
from pathlib import Path

# Đảm bảo đường dẫn import hoạt động độc lập tuyệt đối từ bất kỳ đâu
CLI_DIR = Path(__file__).resolve().parent
PARENT_DIR = CLI_DIR.parent

for p in [str(PARENT_DIR), str(CLI_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Đảm bảo package ICSC_CLI luôn tồn tại trong sys.modules bất kể vị trí hay tên thư mục
if "ICSC_CLI" not in sys.modules:
    pkg = types.ModuleType("ICSC_CLI")
    pkg.__path__ = [str(CLI_DIR)]
    pkg.__file__ = str(CLI_DIR / "__init__.py")
    sys.modules["ICSC_CLI"] = pkg

from ICSC_CLI.ui import terminal
from ICSC_CLI.ui import colors
from ICSC_CLI.views import home_view
from ICSC_CLI.views import exam_view
from ICSC_CLI.views import explorer_view
from ICSC_CLI.views import ingestion_view
from ICSC_CLI.views import history_view
from ICSC_CLI.views import tags_view
from ICSC_CLI.views import diagnostics_view


def main():
    """Hàm khởi chạy vòng lặp tương tác chính."""
    terminal.init_terminal()

    try:
        while True:
            action = home_view.show_home()

            if action == "exam":
                exam_view.show_exam_generator()
            elif action == "explorer":
                explorer_view.show_explorer()
            elif action == "ingestion":
                ingestion_view.show_ingestion()
            elif action == "history":
                history_view.show_history()
            elif action == "tags":
                tags_view.show_tags_matrix()
            elif action == "settings":
                diagnostics_view.show_diagnostics()
            elif action == "exit" or action is None:
                terminal.clear_screen()
                print()
                print(colors.colorize("  ╔════════════════════════════════════════════════════╗", "bright_cyan"))
                print(colors.colorize("  ║       CẢM ƠN BẠN ĐÃ SỬ DỤNG THOTH TERMINAL PRO!    ║", "bright_cyan", bold=True))
                print(colors.colorize("  ║     Thoth Intelligent Exam System • Tạm biệt!      ║", "bright_cyan"))
                print(colors.colorize("  ╚════════════════════════════════════════════════════╝", "bright_cyan"))
                print()
                break
    except KeyboardInterrupt:
        terminal.show_cursor()
        print("\n\n  Đã dừng chương trình. Tạm biệt! 👋\n")
    finally:
        terminal.show_cursor()


if __name__ == "__main__":
    main()
