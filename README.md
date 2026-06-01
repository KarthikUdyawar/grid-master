# Sudoku Book Generator

A Python script that generates print-ready Sudoku puzzle books as PDF files. Each book includes a cover page, unique puzzles, an answer section, and a back cover.

---

## Features

- 5 difficulty levels based on blank count and solving technique complexity
- All puzzles are valid with a **unique solution** (verified algorithmically)
- Clean A4 PDF layout — large puzzle grids, minimal whitespace
- Answer section: 6 mini grids per page (2 columns × 3 rows)
- Styled cover and back cover matching the difficulty color theme

---

## Requirements

- Python 3.7+
- [uv](https://docs.astral.sh/uv/) — fast Python package manager
- [ReportLab](https://pypi.org/project/reportlab/)

### Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup project

```bash
# Install dependencies from lockfile
uv sync

# Or add reportlab manually
uv add reportlab
```

---

## Usage

```bash
uv run main.py --puzzles <N> --difficulty <level> --output <file.pdf>
```

### Arguments

| Argument       | Required | Default           | Description                   |
| -------------- | -------- | ----------------- | ----------------------------- |
| `--puzzles`    | No       | `10`              | Number of puzzles to generate |
| `--difficulty` | No       | `medium`          | Difficulty level (see below)  |
| `--output`     | No       | `sudoku_book.pdf` | Output PDF filename           |

### Examples

```bash
# 10 medium puzzles (default)
uv run main.py

# 20 easy puzzles
uv run main.py --puzzles 20 --difficulty easy --output easy_book.pdf

# 50 master puzzles
uv run main.py --puzzles 50 --difficulty master --output master_book.pdf
```

---

## Difficulty Levels

| Level    | Blanks | Color  | Description                        |
| -------- | ------ | ------ | ---------------------------------- |
| `easy`   | 32     | Green  | Solvable by direct elimination     |
| `medium` | 40     | Blue   | Requires some scanning techniques  |
| `hard`   | 48     | Orange | Needs advanced row/col elimination |
| `expert` | 54     | Red    | Requires naked/hidden pairs        |
| `master` | 58     | Purple | Near-minimal clues, complex chains |

---

## PDF Structure

```
Page 1        → Cover
Pages 2–N+1   → Puzzles (1 per page)
Pages N+2–end → Answers (6 per page, 2 cols × 3 rows)
Last page     → Back cover
```

---

## How It Works

1. **Board generation** — fills a valid 9×9 grid using recursive backtracking with randomized number order.
2. **Puzzle creation** — removes cells one by one, checking after each removal that the puzzle still has exactly one solution.
3. **PDF rendering** — uses ReportLab canvas to draw grids, text, and styled covers on A4 pages.

---

## Customization

You can edit `DIFFICULTY` at the top of the script to adjust blank counts or colors:

```python
DIFFICULTY = {
    "easy":   {"blanks": 32, "label": "Easy",   "color": (0.2, 0.6, 0.2)},
    "medium": {"blanks": 40, "label": "Medium",  "color": (0.1, 0.4, 0.8)},
    ...
}
```

To change page size, update:

```python
from reportlab.lib.pagesizes import A4, LETTER
PAGE_W, PAGE_H = A4  # swap to LETTER if needed
```

---

## Notes

- Generation time scales with puzzle count and difficulty. Master-level puzzles take longer due to uniqueness verification.
- All puzzles are randomly generated each run — no two books are the same.
- Answers highlight given digits in dark gray and solved digits in blue for easy reading.
