# Thoth - Giao Diện Dòng Lệnh Trực Quan & Tự Chứa (Standalone Terminal UI)

> **Phiên bản**: 2.0.0 Pro  
> **Tên ứng dụng**: **Thoth** (Vị thần trí tuệ, toán học và ghi chép)  
> **Kiến trúc tự chứa 100%**: Thư mục `ICSC_CLI` hoàn toàn độc lập. Bạn có thể sao chép hoặc di chuyển thư mục `ICSC_CLI` sang bất kỳ ổ đĩa, thư mục nào khác (kể cả đổi tên thành `Thoth`), chương trình vẫn hoạt động đầy đủ mà **không phụ thuộc vào thư mục `ICSC` gốc**.

---

## 1. Khởi chạy chương trình

### Nếu vẫn ở trong thư mục dự án `ICSC`:
- **Nhanh nhất (từ thư mục gốc)**: Gõ `thoth` hoặc `python thoth.py`
- **Chạy dạng module**: Gõ `python -m ICSC_CLI`

### Nếu di chuyển thư mục `ICSC_CLI` ra bên ngoài:
Bạn chỉ cần mở terminal bên trong thư mục đó và gõ:
```powershell
python main.py
# hoặc
python thoth.py
# hoặc
.\thoth.bat
```

> **Mẹo nâng cao**: Thêm đường dẫn thư mục `ICSC_CLI` vào biến môi trường `PATH` của Windows để có thể gõ lệnh `thoth` từ bất kỳ thư mục nào trong PowerShell hoặc CMD.

---

## 2. Cấu trúc thư mục tự chứa (Self-Contained Architecture)

```
ICSC_CLI/
├── input/                    # [MỚI] Thư mục nhận ảnh/PDF đề thi đầu vào (hoàn toàn riêng biệt)
├── output/                   # [MỚI] Thư mục xuất bản file đề thi .pdf và .tex
├── logs/                     # [MỚI] Nhật ký các đề thi đã tạo (exam_history.json)
├── data/                     # [TỰ CHỨA] Ngân hàng câu hỏi và từ điển Tags chuẩn
│   ├── sorted/               # Kho câu hỏi phân loại theo môn (Calculus 1, Algebra...)
│   ├── tags_01_v2.md         # Quy chuẩn Tags kiến thức môn học
│   ├── template_v3.md        # Prompt mẫu cấu trúc đề thi cho Gemini OCR
│   └── ocr_output/           # Kết quả OCR JSON cục bộ
├── templates/                # [TỰ CHỨA] Các mẫu định dạng LaTeX và macro thoth.sty
│   ├── thoth.sty             # File macro LaTeX tổng hợp
│   ├── midterm/thoth.sty     # Macro đề giữa kỳ
│   ├── final/thoth.sty       # Macro đề cuối kỳ
│   └── practice/thoth.sty    # Macro đề tự luyện
├── pipeline/                 # [TỰ CHỨA] Bộ công cụ OCR & Sorter độc lập
│   ├── OCR.py                # Quét file trong input/ gửi Gemini AI xuất vào data/ocr_output/
│   └── SORTER.py             # Phân loại JSON từ data/ocr_output/ vào data/sorted/
├── ui/                       # Engine giao diện trực quan ANSI / Unicode
│   ├── colors.py             # Bảng màu ANSI, Gradient, Badges, Icons Unicode
│   ├── terminal.py           # Kích hoạt Virtual Terminal Windows, tính toán độ rộng ký tự
│   ├── input_handler.py      # Bắt phím điều hướng (khung viền căn lề chuẩn 100%, không lệch viền)
│   ├── table.py              # Bộ dựng bảng Unicode căn lề chuẩn tuyệt đối
│   ├── components.py         # Panel tự động ngắt dòng thông minh (KHÔNG cắt cụt văn bản)
│   └── viewer.py             # Trình hiển thị câu hỏi và công thức toán học LaTeX trực quan
├── core/                     # Tầng dịch vụ logic & thuật toán
│   ├── data_loader.py        # Tải JSON có Caching, thống kê kho câu hỏi, chuẩn hóa điểm
│   ├── question_selector.py  # Thuật toán Greedy tối đa độ phủ Tags & Deduplication
│   ├── latex_renderer.py     # Renderer LaTeX chuẩn (hỗ trợ display_system, OnePointQues...)
│   ├── latex_compiler.py     # Tự động tìm pdflatex, biên dịch PDF, dọn file phụ và mở PDF
│   ├── exam_log.py           # Quản lý nhật ký các đề đã sinh
│   ├── tag_manager.py        # Phân tích cây tags chuẩn và tính toán độ phủ kiến thức
│   ├── exam_service.py       # Điều phối tạo đề Giữa kỳ, Cuối kỳ, Tự luyện
│   └── pipeline_service.py   # Giám sát thư mục input, kiểm tra Gemini API key và điều phối OCR / Sorter
├── views/                    # Các màn hình tương tác người dùng
│   ├── base_view.py          # Header đồng nhất, thanh Breadcrumbs điều hướng
│   ├── home_view.py          # Dashboard chính hiển thị trạng thái hệ thống
│   ├── exam_view.py          # Wizard tạo đề thi 5 bước
│   ├── explorer_view.py      # Khám phá ngân hàng câu hỏi (Pagination, tìm kiếm)
│   ├── ingestion_view.py     # Giám sát file ảnh/PDF đầu vào, chạy OCR Gemini & SORTER
│   ├── history_view.py       # Xem lịch sử đề thi đã tạo và mở nhanh PDF / File Explorer
│   ├── tags_view.py          # Xem ma trận kiến thức & xem câu hỏi theo từng Tag
│   └── diagnostics_view.py   # Kiểm tra môi trường MiKTeX, quản lý thư mục Input/Output
├── config.py                 # File cấu hình trung tâm (tự động nhận diện đường dẫn cục bộ)
├── main.py                   # Điểm khởi chạy chính
├── thoth.py                  # Entry point alias
├── thoth.bat                 # Script chạy nhanh cho Windows CMD / PowerShell
└── .env                      # Lưu trữ khóa GEMINI_API_KEY
```

---

## 3. Các điểm nâng cấp quan trọng

1. **Hiển thị đầy đủ 100% nội dung câu hỏi**:
   - Khung hiển thị câu hỏi (`panel`) được trang bị thuật toán **tự động xuống dòng thông minh (`wrap_text_ansi`)**.
   - Bất kể câu hỏi, công thức toán hay các ý con dài bao nhiêu dòng, nội dung sẽ được tự động ngắt dòng êm ái, bảo toàn căn lề và thụt đầu dòng, **tuyệt đối không bao giờ bị cắt cụt bằng `...`**.
2. **Khung viền xanh liền mạch 100%**:
   - Menu lựa chọn được khóa cứng độ rộng với cơ chế phân bổ không gian tự động, không bị vỡ khung hoặc nhảy dòng khi mô tả dài.
3. **Thư mục `input` và `output` độc lập**:
   - `input/`: Thả các file ảnh hoặc PDF đề thi mới vào đây để chạy OCR.
   - `output/`: Toàn bộ đề thi được sinh ra kèm file `.pdf` và `.tex` được lưu gọn gàng tại đây.
   - Không bị lẫn lộn dữ liệu với thư mục `ICSC` gốc.
4. **Hỗ trợ đầy đủ xem câu hỏi theo Tags**:
   - Trong màn hình **Ma trận kiến thức (`tags_view.py`)**, bạn có thể nhập mã Tag bất kỳ để xem toàn bộ danh sách câu hỏi thuộc chủ đề đó.
