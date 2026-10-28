"""
SORTER.py - Standalone Sorter Engine cho Thoth CLI.
Đọc các JSON trong ICSC_CLI/data/ocr_output, phân loại theo section_tags và gán mã câu hỏi
vào ICSC_CLI/data/sorted/<subject>/chapter_N.json.
Tự chứa 100% trong ICSC_CLI.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from collections import defaultdict

PIPELINE_DIR = Path(__file__).resolve().parent
CLI_DIR = PIPELINE_DIR.parent
OCR_OUTPUT_DIR = CLI_DIR / "data" / "ocr_output"
SORTED_DIR = CLI_DIR / "data" / "sorted"
PROCESSED_LOG = CLI_DIR / "data" / ".sorter_processed.json"

SUBJECT_MAP = {
    "Calculus 1": "calculus_1",
    "Calculus 2": "calculus_2",
    "Calculus 3": "calculus_3",
    "Algebra": "algebra",
}

TAG_PREFIX_TO_CHAPTER = {
    "c1": 1,
    "c2": 2,
    "c3": 3,
    "c4": 4,
    "c5": 5,
}


def load_processed_log() -> list[str]:
    if PROCESSED_LOG.exists():
        try:
            return json.loads(PROCESSED_LOG.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_processed_log(processed: list[str]) -> None:
    PROCESSED_LOG.write_text(json.dumps(processed, ensure_ascii=False, indent=2), encoding="utf-8")


def load_chapter(path: Path) -> list:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_chapter(path: Path, data: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_chapters_from_tags(section_tags: list[str]) -> set[int]:
    chapters = set()
    for tag in section_tags:
        prefix = tag.split("_")[0].lower()
        if prefix in TAG_PREFIX_TO_CHAPTER:
            chapters.add(TAG_PREFIX_TO_CHAPTER[prefix])
    return chapters


def process_file(filepath: Path) -> bool:
    data = json.loads(filepath.read_text(encoding="utf-8"))
    metadata = data.get("metadata", {})
    subject = metadata.get("subject")
    date = metadata.get("date")

    # Fallback: nếu date trong metadata bị null/rỗng, dùng timestamp từ tên file OCR
    if not date:
        date = filepath.stem
        print(f"  [Thông tin] '{filepath.name}' thiếu date trong metadata -> Dùng fallback: {date}")

    if not subject:
        print(f"  [Bỏ qua] Thiếu subject trong {filepath.name}")
        return False

    folder_name = SUBJECT_MAP.get(subject)
    if not folder_name:
        print(f"  [Bỏ qua] Không nhận diện được môn '{subject}' trong {filepath.name}")
        return False

    subject_dir = SORTED_DIR / folder_name
    body = data.get("body", [])
    if not body:
        print(f"  [Bỏ qua] Body rỗng trong {filepath.name}")
        return False

    chapter_order: dict[int, int] = defaultdict(int)
    added_count = 0

    for item in body:
        section_tags = item.get("section_tags", [])
        chapters = get_chapters_from_tags(section_tags)
        if not chapters:
            continue

        for ch_num in sorted(chapters):
            chapter_order[ch_num] += 1
            order = chapter_order[ch_num]
            item_copy = dict(item)
            item_copy["question_code"] = f"{date}-{order}"

            chapter_path = subject_dir / f"chapter_{ch_num}.json"
            existing = load_chapter(chapter_path)

            # Kiểm tra trùng lặp
            existing_codes = {q.get("question_code") for q in existing}
            if item_copy["question_code"] not in existing_codes:
                existing.append(item_copy)
                save_chapter(chapter_path, existing)
                added_count += 1
                print(f"  ✓ Đã thêm {item_copy['question_code']} vào {folder_name}/chapter_{ch_num}.json")

    print(f"  -> Hoàn tất phân loại {added_count} câu hỏi từ {filepath.name}")
    return True


def run_sorter(reprocess: bool = False) -> None:
    if not OCR_OUTPUT_DIR.exists():
        print(f"Thư mục OCR output không tồn tại: {OCR_OUTPUT_DIR}")
        return

    processed = set() if reprocess else set(load_processed_log())
    files = [f for f in sorted(OCR_OUTPUT_DIR.glob("*.json")) if reprocess or f.name not in processed]

    if not files:
        print("Không có file JSON mới nào cần phân loại.")
        return

    print(f"Bắt đầu phân loại {len(files)} file OCR output...")
    for f in files:
        print(f"Đang xử lý: {f.name}")
        try:
            success = process_file(f)
            if success:
                processed.add(f.name)
        except Exception as e:
            print(f"  [Lỗi] {f.name}: {e}")

    save_processed_log(sorted(processed))
    print("Hoàn tất phân loại vào chapters!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reprocess", action="store_true", help="Phân loại lại toàn bộ file")
    args = parser.parse_args()
    run_sorter(reprocess=args.reprocess)
