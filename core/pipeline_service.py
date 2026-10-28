"""
pipeline_service.py - Quản lý và điều phối luồng thu thập dữ liệu (OCR và SORTER).
Kiểm tra biến môi trường Gemini API Key, quét file đầu vào và chạy pipeline trực quan.
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from .. import config


def check_api_key_status() -> Dict[str, Any]:
    """Kiểm tra xem GEMINI_API_KEY đã được thiết lập chưa."""
    # Kiểm tra biến môi trường
    key = os.environ.get("GEMINI_API_KEY")
    source = "environment"

    # Kiểm tra file .env
    if not key and config.OCR_ENV_FILE.exists():
        try:
            content = config.OCR_ENV_FILE.read_text(encoding="utf-8")
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    source = ".env file"
                    break
        except Exception:
            pass

    return {
        "configured": bool(key),
        "source": source if key else "Chưa cấu hình",
        "masked_key": f"{key[:6]}...{key[-4:]}" if key and len(key) > 10 else ("Có sẵn" if key else "None"),
    }


def get_input_files_status() -> List[Dict[str, Any]]:
    """Lấy danh sách các file ảnh / PDF trong thư mục input kèm trạng thái xử lý."""
    if not config.OCR_INPUT_DIR.exists():
        return []

    # Đọc danh sách đã xử lý
    processed_set = set()
    if config.OCR_PROCESSED_LOG.exists():
        try:
            with open(config.OCR_PROCESSED_LOG, "r", encoding="utf-8") as f:
                processed_set = set(json.load(f))
        except Exception:
            pass

    supported_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".pdf"}
    files = []

    for f in sorted(config.OCR_INPUT_DIR.iterdir()):
        if f.is_file() and f.suffix.lower() in supported_exts:
            size_kb = f.stat().st_size / 1024
            is_processed = f.name in processed_set
            files.append({
                "name": f.name,
                "size_kb": f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB",
                "ext": f.suffix.lower(),
                "is_processed": is_processed,
                "path": str(f),
            })

    return files


def run_pipeline(
    run_ocr: bool = True,
    run_sort: bool = True,
    subject: Optional[str] = None,
    reprocess: bool = False,
) -> Dict[str, Any]:
    """
    Thực thi pipeline OCR và/hoặc SORTER.
    """
    result = {
        "ocr_success": None,
        "ocr_output": "",
        "sorter_success": None,
        "sorter_output": "",
    }

    # 1. Chạy OCR.py
    if run_ocr and config.OCR_SCRIPT.exists():
        cmd = [sys.executable, str(config.OCR_SCRIPT)]
        if subject:
            cmd.extend(["--subject", subject])
        if reprocess:
            cmd.append("--reprocess")

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(config.OCR_SCRIPT.parent),
                capture_output=True,
                text=True,
                timeout=300,
            )
            result["ocr_success"] = (proc.returncode == 0)
            result["ocr_output"] = proc.stdout + "\n" + proc.stderr
        except Exception as e:
            result["ocr_success"] = False
            result["ocr_output"] = str(e)

    # 2. Chạy SORTER.py
    if run_sort and config.SORTER_SCRIPT.exists():
        cmd = [sys.executable, str(config.SORTER_SCRIPT)]
        if reprocess:
            cmd.append("--reprocess")
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(config.SORTER_SCRIPT.parent),
                capture_output=True,
                text=True,
                timeout=120,
            )
            result["sorter_success"] = (proc.returncode == 0)
            result["sorter_output"] = proc.stdout + "\n" + proc.stderr
        except Exception as e:
            result["sorter_success"] = False
            result["sorter_output"] = str(e)

    return result
