"""
OCR.py - Standalone OCR Engine cho Thoth CLI.
Quét ảnh/PDF trong folder ICSC_CLI/input, gửi cho Gemini và xuất JSON vào ICSC_CLI/data/ocr_output.
Tự chứa 100% trong ICSC_CLI, không phụ thuộc đường dẫn bên ngoài.
"""

from __future__ import annotations

import argparse
import datetime
import json
import mimetypes
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# ──────────────────────────── Paths ────────────────────────────
PIPELINE_DIR = Path(__file__).resolve().parent       # ICSC_CLI/pipeline/
CLI_DIR = PIPELINE_DIR.parent                        # ICSC_CLI/
INPUT_DIR = CLI_DIR / "input"
DATA_DIR = CLI_DIR / "data"
OUTPUT_DIR = DATA_DIR / "ocr_output"
RESOURCE_DIR = DATA_DIR
PROCESSED_LOG = DATA_DIR / ".ocr_processed.json"
ENV_FILE = CLI_DIR / ".env"

# ──────────────────────────── Config ───────────────────────────
MODEL_NAME = "gemini-3.8-flash"
SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
SUPPORTED_PDF_EXTS = {".pdf"}
SUPPORTED_EXTS = SUPPORTED_IMAGE_EXTS | SUPPORTED_PDF_EXTS


# ──────────────────────────── Helpers ──────────────────────────
def load_processed() -> set[str]:
    """Đọc danh sách file đã xử lý trước đó."""
    if PROCESSED_LOG.exists():
        try:
            data = json.loads(PROCESSED_LOG.read_text(encoding="utf-8"))
            return set(data)
        except Exception:
            return set()
    return set()


def save_processed(processed: set[str]) -> None:
    """Lưu danh sách file đã xử lý."""
    PROCESSED_LOG.write_text(
        json.dumps(sorted(processed), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def collect_new_files(processed: set[str]) -> list[Path]:
    """Thu thập các file ảnh/PDF mới trong input/."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_files: list[Path] = []
    for f in sorted(INPUT_DIR.iterdir()):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS:
            if f.name not in processed:
                new_files.append(f)
    return new_files


def build_resource_prompt() -> str:
    """Ghép template_v3.md và tags_01_v2.md thành prompt chuẩn."""
    parts: list[str] = []
    for fname in ["template_v3.md", "tags_01_v2.md"]:
        md_file = RESOURCE_DIR / fname
        if md_file.exists():
            parts.append(f"--- {md_file.name} ---\n{md_file.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def upload_file_for_api(client: genai.Client, file_path: Path) -> types.Part:
    """Upload file lên Gemini Files API."""
    mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    uploaded = client.files.upload(
        file=file_path,
        config=types.UploadFileConfig(mime_type=mime),
    )
    while uploaded.state == "PROCESSING":
        time.sleep(2)
        uploaded = client.files.get(name=uploaded.name)

    if uploaded.state == "FAILED":
        raise RuntimeError(f"File upload failed for {file_path.name}")
    return types.Part.from_uri(file_uri=uploaded.uri, mime_type=uploaded.mime_type)


def prepare_file_parts(client: genai.Client, files: list[Path]) -> list[types.Part]:
    """Chuẩn bị Parts cho Gemini."""
    parts: list[types.Part] = []
    for f in files:
        if f.suffix.lower() in SUPPORTED_PDF_EXTS:
            parts.append(upload_file_for_api(client, f))
        else:
            mime = mimetypes.guess_type(str(f))[0] or "image/png"
            parts.append(types.Part.from_bytes(data=f.read_bytes(), mime_type=mime))
    return parts


def clean_json_response(raw_text: str) -> str:
    """Bóc markdown fenced code block nếu có."""
    text = raw_text.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


def run_ocr(subject: str | None = None, reprocess: bool = False) -> None:
    # Nạp API key
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY chưa được đặt!")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    processed = set() if reprocess else load_processed()
    new_files = [f for f in sorted(INPUT_DIR.iterdir()) if f.suffix.lower() in SUPPORTED_EXTS] if reprocess else collect_new_files(processed)

    if not new_files:
        print("Không có file mới nào trong thư mục input/")
        return

    print(f"Tìm thấy {len(new_files)} file cần OCR.")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    resource_prompt = build_resource_prompt()
    system_instruction = (
        "Bạn là chuyên gia số hoá đề thi toán học sang cấu trúc JSON chuẩn.\n"
        "Hãy tuân thủ tuyệt đối quy cách và danh mục tags sau đây:\n\n"
        f"{resource_prompt}"
    )

    contents: list[types.Part | str] = prepare_file_parts(client, new_files)
    prompt_text = "Hãy OCR toàn bộ các câu hỏi toán học trong tài liệu sau sang định dạng JSON."
    if subject:
        prompt_text += f"\nLưu ý: Môn học được chỉ định là: {subject}"
    contents.append(prompt_text)

    print("Đang gửi yêu cầu lên Gemini API...")
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    cleaned_json = clean_json_response(response.text)
    # Kiểm tra JSON hợp lệ
    parsed = json.loads(cleaned_json)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    out_file = OUTPUT_DIR / f"{timestamp}.json"
    out_file.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã lưu kết quả OCR vào: {out_file}")

    for f in new_files:
        processed.add(f.name)
    save_processed(processed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", type=str, default=None)
    parser.add_argument("--reprocess", action="store_true")
    args = parser.parse_args()
    run_ocr(subject=args.subject, reprocess=args.reprocess)
