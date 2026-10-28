---
name = "template for JSON file"
description = "Structured JSON format for storing math problems with LaTeX"
draft = "03"
---

# CRITICAL: LaTeX Backslash Rule
Every `\` in LaTeX MUST be doubled (`\\`) in JSON output. This applies to ALL `inline_math` and `display_math` values.
- `\sin x` → `"\\sin x"`
- `\frac{1}{2}` → `"\\frac{1}{2}"`
- `\int_0^1` → `"\\int_0^1"`
- `(1, +\infty)` → `"(1, +\\infty)"`

**NEVER output a single `\` in any math value.**

# Task
Convert math problems from images into one JSON file. Output raw JSON only — no markdown, no explanation.

# Rules
- Preserve original language of question text.
- If info is not visible, use `null`. Always infer `section_tags`.
- No leading/trailing whitespace in strings.
- Strip page numbers, headers, ordinal labels (e.g. "Câu 5"). Extract points (e.g. "1đ") to `"point"`.
- Images are sequential; a question may span images — combine into one entry.

# TEXT_BLOCK
A flat `{}` object storing segmented text with keys: `{prefix}_{type}_{line}_{seq}`
- `prefix`: empty or letter (`a`, `b`...) for sub-parts
- `type`: `line` | `inline_math` | `display_math`
- `line`/`seq`: two-digit numbers (01, 02...). Line increments after `display_math` or line break.

Example — *"Cho hàm số $f(x)=x^2$. Tính"* then $$\int_0^1 f(x)dx$$ then *"Kết quả là $A$."*:
```json
{
  "line_01_01": "Cho hàm số",
  "inline_math_01_01": "f(x)=x^2",
  "line_01_02": ". Tính",
  "display_math_01_01": "\\int_0^1 f(x)dx",
  "line_02_01": "Kết quả là",
  "inline_math_02_01": "A",
  "line_02_02": "."
}
```
⚠️ Note `\\int` above — backslashes are doubled.

Sub-parts use prefixed keys: `a_line_01_01`, `a_inline_math_01_01`, `b_line_01_01`...

# JSON Structure

```json
{
  "metadata": {
    "title": "string or null",
    "date": "YYYY-MM-DD-HH-MM (GMT+7)",
    "subject": "Calculus 1|Calculus 2|Calculus 3|Algebra"
  },
  "body": [ /* array of question objects */ ]
}
```

Each question object has:
```json
{
  "question_code": null,
  "question_type": "FRQ_SP|FRQ_MP|MCQ_SA|MCQ_MA|TFQ",
  "section_tags": ["tag1"],
  "point": null or "1"|"1.5"|"2"|"2.5"|"3",
  ...type-specific fields below...
}
```

**FRQ_SP**: `"question": {TEXT_BLOCK}`, `"solution": null`
**FRQ_MP**: `"main": {TEXT_BLOCK}`, `"part": {prefixed TEXT_BLOCK}`, `"end": null|{TEXT_BLOCK}`, `"solution": {"a": null, "b": null}`
**MCQ_SA**: `"question": {TEXT_BLOCK}`, `"choices": {prefixed TEXT_BLOCK}`, `"solution": null|"letter"|{"answer":"letter","full":{TEXT_BLOCK}}`
**MCQ_MA**: same as MCQ_SA but answer has multiple letters
**TFQ**: `"question": {TEXT_BLOCK}`, `"statements": {prefixed TEXT_BLOCK}`, `"solution": null|["T","F",...]|{"answer":["T","F",...],"full":{TEXT_BLOCK}}`

# MATRIX type
For matrices, determinants, vectors — use `matrix` object instead of raw LaTeX string in `display_math`.
Key format: `{prefix}_{type}_{line}_{seq}` where `type` = `inline_matrix` or `display_matrix`.
Naming follows the same `line`/`seq` rules as `inline_math`/`display_math`.

Value is an object with:
- `"style"`: `"pmatrix"` | `"bmatrix"` | `"vmatrix"` | `"Vmatrix"` | `"Bmatrix"` | `"matrix"` | `"smallmatrix"` | `"array"`
- `"rows"`: 2D array — each inner array is one row, each element is a LaTeX string (double-escaped)
- `"col_spec"` (only when `style` = `"array"`): column specification string, e.g. `"ccc|c"`

Example — *"Cho ma trận $A$"* then $$\begin{pmatrix}1&2\\3&4\end{pmatrix}$$:
```json
{
  "line_01_01": "Cho ma trận",
  "inline_math_01_01": "A",
  "display_matrix_02_01": {
    "style": "pmatrix",
    "rows": [["1", "2"], ["3", "4"]]
  }
}
```

Augmented matrix example:
```json
"display_matrix_01_01": {
  "style": "array",
  "col_spec": "ccc|c",
  "rows": [
    ["1", "2", "3", "4"],
    ["5", "6", "7", "8"]
  ]
}
```

# SYSTEM type
For systems of equations, piecewise functions — use `system` object instead of raw LaTeX string.
Key format: `{prefix}_{type}_{line}_{seq}` where `type` = `inline_system` or `display_system`.
Naming follows the same `line`/`seq` rules as `inline_math`/`display_math`.

Value is an object with:
- `"style"`: `"cases"` | `"rcases"` | `"dcases"` | `"aligned"` | `"array"`
- `"eqs"`: 1D array — each element is one equation/line as a LaTeX string (double-escaped)
- `"col_spec"` (only when `style` = `"array"`): column specification string, e.g. `"l"`

Example — *"Giải hệ phương trình"* then $$\begin{cases}x+y=5\\x-y=1\end{cases}$$:
```json
{
  "line_01_01": "Giải hệ phương trình",
  "display_system_01_01": {
    "style": "cases",
    "eqs": ["x + y = 5", "x - y = 1"]
  }
}
```

Piecewise function example:
```json
"display_system_01_01": {
  "style": "cases",
  "eqs": [
    "x^2, \\quad x \\geq 0",
    "-x^2, \\quad x < 0"
  ]
}
```

# When to use matrix vs system
- **matrix**: each row has distinct columns (matrices, determinants, vectors, augmented matrices) → 2D `rows` with auto `&` between elements
- **system**: each row is a single expression (systems of equations, piecewise definitions, conditions) → 1D `eqs`, no auto `&`
