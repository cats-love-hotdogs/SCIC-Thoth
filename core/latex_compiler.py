"""
latex_compiler.py - Tìm kiếm và thực thi biên dịch LaTeX sang PDF.
Hỗ trợ dọn dẹp các file phụ, xử lý lỗi trên Windows và mở nhanh file PDF/TeX.
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any

_COMMON_PATHS = [
    os.path.join(os.environ.get("PROGRAMFILES", ""), "MiKTeX", "miktex", "bin", "x64", "pdflatex.exe"),
    os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "MiKTeX", "miktex", "bin", "x64", "pdflatex.exe"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "MiKTeX", "miktex", "bin", "x64", "pdflatex.exe"),
    "C:\\texlive\\2026\\bin\\windows\\pdflatex.exe",
    "C:\\texlive\\2025\\bin\\windows\\pdflatex.exe",
    "C:\\texlive\\2024\\bin\\windows\\pdflatex.exe",
]


def find_pdflatex() -> Optional[str]:
    """Tìm đường dẫn tới pdflatex trên hệ thống."""
    path = shutil.which("pdflatex")
    if path:
        return path

    for p in _COMMON_PATHS:
        if os.path.isfile(p):
            return p

    return None


def get_latex_info() -> Dict[str, Any]:
    """Lấy thông tin phiên bản và trạng thái của LaTeX compiler."""
    cmd = find_pdflatex()
    if not cmd:
        return {
            "found": False,
            "path": None,
            "version": "Không tìm thấy pdflatex",
            "status": "Chưa cài đặt LaTeX",
        }

    try:
        proc = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
        first_line = proc.stdout.split("\n")[0] if proc.stdout else "pdflatex"
        return {
            "found": True,
            "path": cmd,
            "version": first_line.strip(),
            "status": "Sẵn sàng",
        }
    except Exception as e:
        return {
            "found": True,
            "path": cmd,
            "version": str(e),
            "status": "Có thể dùng",
        }


def _cleanup_aux_files(tex_path: Path) -> None:
    """Dọn dẹp các file phụ (.aux, .log, .fls, .fdb_latexmk, .synctex.gz)."""
    parent_dir = tex_path.parent
    base_stem = tex_path.stem
    aux_exts = [".aux", ".log", ".fls", ".fdb_latexmk", ".synctex.gz"]

    time.sleep(0.3)  # Nhả file lock trên Windows

    for ext in aux_exts:
        f = parent_dir / f"{base_stem}{ext}"
        if f.exists():
            for _ in range(3):
                try:
                    f.unlink()
                    break
                except PermissionError:
                    time.sleep(0.2)
                except Exception:
                    break


def compile_latex(tex_path: Path, runs: int = 2) -> Optional[Path]:
    """
    Biên dịch file .tex thành PDF bằng pdflatex.
    """
    tex_path = Path(tex_path).resolve()
    if not tex_path.exists():
        print(f"  [Lỗi] File .tex không tồn tại: {tex_path}")
        return None

    pdflatex_bin = find_pdflatex()
    if not pdflatex_bin:
        print("  [Cảnh báo] Không tìm thấy pdflatex trên hệ thống!")
        return None

    work_dir = tex_path.parent
    tex_filename = tex_path.name
    pdf_filename = tex_path.with_suffix(".pdf").name
    expected_pdf = work_dir / pdf_filename

    # Lệnh biên dịch
    cmd = [
        pdflatex_bin,
        "-interaction=nonstopmode",
        "-file-line-error",
        tex_filename,
    ]

    for run_idx in range(runs):
        try:
            res = subprocess.run(
                cmd,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if res.returncode != 0 and run_idx == runs - 1:
                # Gặp lỗi khi biên dịch lần cuối
                error_lines = [
                    l for l in res.stdout.split("\n")
                    if l.startswith("!") or "Error" in l or "Fatal error" in l
                ]
                if error_lines:
                    print(f"  [Lỗi LaTeX] {error_lines[0]}")
        except subprocess.TimeoutExpired:
            print("  [Lỗi] Quá thời gian biên dịch (Timeout)!")
            return None
        except Exception as e:
            print(f"  [Lỗi biên dịch] {e}")
            return None

    # Dọn dẹp file phụ
    _cleanup_aux_files(tex_path)

    if expected_pdf.exists():
        return expected_pdf
    return None


def open_pdf(pdf_path: Path) -> bool:
    """Mở file PDF bằng ứng dụng mặc định của hệ thống."""
    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.exists():
        return False

    try:
        if sys.platform == "win32":
            os.startfile(str(pdf_path))  # type: ignore
            return True
        elif sys.platform == "darwin":
            subprocess.run(["open", str(pdf_path)])
            return True
        else:
            subprocess.run(["xdg-open", str(pdf_path)])
            return True
    except Exception as e:
        print(f"  [Không thể mở file trực tiếp] {e}")
        return False


def open_folder(folder_path: Path) -> bool:
    """Mở thư mục chứa file trong File Explorer."""
    folder_path = Path(folder_path).resolve()
    if not folder_path.exists():
        return False

    try:
        if sys.platform == "win32":
            os.startfile(str(folder_path))  # type: ignore
            return True
        elif sys.platform == "darwin":
            subprocess.run(["open", str(folder_path)])
            return True
        else:
            subprocess.run(["xdg-open", str(folder_path)])
            return True
    except Exception:
        return False
