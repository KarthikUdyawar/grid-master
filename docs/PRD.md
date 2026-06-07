# Product Requirements Document
## Sudoku Book Generator

**Version:** 2.0  
**Status:** Sprint 2 — In Planning  
**Last Updated:** June 2026

---

## 1. Overview

### Problem Statement
Sudoku enthusiasts and educators need a simple way to generate print-ready Sudoku puzzle books without relying on third-party services, subscriptions, or manual puzzle creation.

### Solution
A local Python CLI tool that generates a complete, styled, print-ready Sudoku book as a PDF — with cover, puzzles, answers, and back cover — in a single command.

### Goal
Minimize friction between "I want a Sudoku book" and "I have a printable PDF."

---

## 2. Users

| User               | Need                                             |
| ------------------ | ------------------------------------------------ |
| Puzzle enthusiast  | Personal practice books at chosen difficulty     |
| Teacher / educator | Classroom activity sheets with answer keys       |
| Event organizer    | Custom puzzle sets for competitions or giveaways |
| Self-publisher     | Ready-to-print booklets without design tools     |

---

## 3. Scope

### Completed (v1.0)
- CLI tool, single Python file
- 5 difficulty levels
- Configurable puzzle count
- PDF output: cover → puzzles → answers → back cover
- Unique-solution guarantee per puzzle
- A4 page size

### In Scope (v2.0 — Sprint 2)
- Mixed-difficulty book (multiple levels in one PDF)
- Custom page size flag (`--pagesize letter|a4|a5`)
- Custom book title and author name on cover

### Out of Scope (Future)
- GUI or web interface
- 2 puzzles per page layout option
- 6×6 or 16×16 grid variants
- Batch export (multiple difficulties at once)
- Export puzzle data as JSON alongside PDF
- Puzzle numbering across difficulty sections

---

## 4. Functional Requirements

### FR-1: Puzzle Generation ✅ (v1.0)
- Generate valid 9×9 Sudoku grids using recursive backtracking
- Each puzzle must have exactly one solution (verified before inclusion)
- Puzzles must be unique within a run (no duplicates)
- Blank count per difficulty:

| Level  | Blanks |
| ------ | ------ |
| Easy   | 32     |
| Medium | 40     |
| Hard   | 48     |
| Expert | 54     |
| Master | 58     |

### FR-2: CLI Interface ✅ (v1.0) — Extended in v2.0
- Accept `--puzzles`, `--difficulty`, `--output` arguments
- Sensible defaults: 10 puzzles, medium, `sudoku_book.pdf`
- Print progress to stdout during generation

**New in v2.0:**
- `--difficulty` accepts a comma-separated list for mixed-difficulty books (e.g. `easy,hard,master`)
- `--puzzles` accepts a matching comma-separated count per difficulty level, or a single count applied to all (e.g. `10` or `5,10,5`)
- `--pagesize` flag: `a4` (default) | `letter` | `a5`
- `--title` flag: custom book title shown on cover (default: `"Sudoku"`)
- `--author` flag: author name shown on cover (default: empty)

### FR-3: PDF Structure ✅ (v1.0) — Extended in v2.0
- **Cover** — title, difficulty badge, puzzle count, styled background
- **Puzzle pages** — 1 puzzle per page, large grid, difficulty badge, page footer
- **Answer pages** — 6 answers per page (2 cols × 3 rows), given vs solved digits distinguished by color
- **Back cover** — matches front cover theme, completion message, decorative grid

**New in v2.0:**
- Mixed-difficulty books include a **section divider page** between difficulty levels (matching that level's accent color)
- Cover displays the difficulty mix as a badge list (e.g. "Easy · Hard · Master") when multiple levels are used
- Cover displays custom `--title` and `--author` if provided
- Grid sizing and margins auto-adjust per page size (A4, Letter, A5)

### FR-4: Visual Design ✅ (v1.0)
- Each difficulty has a distinct accent color (green / blue / orange / red / purple)
- Alternating 3×3 box shading for readability
- Answer section: given digits dark gray, solved digits blue
- Cover and back cover: dark background, color-matched accents

**New in v2.0:**
- Section divider page uses full-bleed accent color with difficulty name centered
- Author name rendered below the title on the cover in a smaller, lighter weight
- A5 layout uses smaller grid (proportional scale-down) with tighter margins; answers fit 4 per page (2×2) instead of 6

---

## 5. Non-Functional Requirements

| Requirement        | Target                                             |
| ------------------ | -------------------------------------------------- |
| Single-file script | `main.py` only, no internal modules                |
| Dependency count   | 1 (`reportlab`)                                    |
| Output format      | PDF, print-ready                                   |
| Page sizes         | A4, Letter, A5                                     |
| Puzzle uniqueness  | 100% — enforced algorithmically                    |
| Generation speed   | ≤ 5s per puzzle at Master level (typical hardware) |
| Python version     | 3.7+                                               |

---

## 6. Technical Design

### v1.0 Flow
```text
CLI args
   │
   ▼
generate N puzzles
   │  ┌─ fill_board()      → backtracking solver
   │  └─ make_puzzle()     → remove cells + uniqueness check
   ▼
render PDF (ReportLab canvas)
   │  ┌─ draw_cover()
   │  ├─ draw_puzzle_page()  × N
   │  ├─ draw_answer_section()
   │  └─ draw_back_cover()
   ▼
output .pdf
```

### v2.0 Flow (additions highlighted)
```text
CLI args  ← NEW: --pagesize, --title, --author
           ← NEW: --difficulty accepts comma list
           ← NEW: --puzzles accepts comma list
   │
   ▼
resolve page dimensions from --pagesize       ← NEW
   │
   ▼
generate puzzle groups per difficulty level   ← NEW: loop per level
   │  ┌─ fill_board()
   │  └─ make_puzzle()
   ▼
render PDF (ReportLab canvas)
   │  ┌─ draw_cover()          ← UPDATED: title, author, multi-difficulty badge
   │  ├─ draw_section_divider() × (num_levels - 1)   ← NEW
   │  ├─ draw_puzzle_page()    × N (per section)
   │  ├─ draw_answer_section()
   │  └─ draw_back_cover()
   ▼
output .pdf
```

### Key Algorithms
- **Board fill:** recursive backtracking with shuffled digit order for randomness
- **Uniqueness check:** `count_solutions()` with early exit at 2 — if result > 1, cell removal is reverted
- **PDF layout:** all positions computed from page dimensions and gap constants — no hardcoded coords
- **Page sizing (new):** `PAGE_W, PAGE_H = {"a4": A4, "letter": LETTER, "a5": A5}[args.pagesize]` — all layout functions receive page dimensions as parameters, enabling single-pass rescaling

### CLI Parsing — v2.0 Examples
```bash
# Single difficulty (unchanged behaviour)
uv run main.py --puzzles 20 --difficulty hard

# Mixed difficulty — equal count per level
uv run main.py --puzzles 10 --difficulty easy,medium,hard

# Mixed difficulty — custom count per level
uv run main.py --puzzles 5,10,5 --difficulty easy,medium,hard

# Custom title and author
uv run main.py --title "Grandma's Puzzle Book" --author "Alex" --difficulty easy --puzzles 30

# Letter size output
uv run main.py --pagesize letter --output book_letter.pdf
```

---

## 7. File Structure

```text
.
├── docs/
│   ├── PRD.md           # This document
│   └── TODO.md          # Sprint task tracker
├── output/              # Generated PDFs (gitignored)
├── main.py              # Core script (generator + renderer)
├── README.md            # Usage documentation
├── pyproject.toml       # Project metadata
└── uv.lock              # Dependency lock file
```

---

## 8. Sprint 2 Task Breakdown

### SUB-7 — Page Size Support
- Refactor all layout functions to accept `(page_w, page_h)` as parameters instead of using module-level constants
- Add `--pagesize` argument with choices `a4`, `letter`, `a5`
- Adjust answer grid layout: 6/page for A4 and Letter, 4/page for A5
- Test all three sizes end-to-end

### SUB-8 — Custom Title & Author
- Add `--title` argument (default: `"Sudoku"`)
- Add `--author` argument (default: `""`)
- Update `draw_cover()` to render title in large weight and author name below in smaller/lighter style
- Update `draw_back_cover()` to optionally show author credit

### SUB-9 — Mixed-Difficulty Book
- Extend `--difficulty` parser to split on commas and validate each token
- Extend `--puzzles` parser to accept either a single int or a comma-separated list matching difficulty count
- Generate puzzle groups as an ordered list of `(difficulty_config, [puzzles])` tuples
- Implement `draw_section_divider()` — full-bleed accent color page with difficulty name and puzzle range
- Update `draw_cover()` to render multi-difficulty badge row
- Update `draw_answer_section()` to group answers by section with matching color headers
- Update `draw_back_cover()` summary to reflect total count and level mix

### SUB-10 — Documentation Update
- Update `README.md` with new CLI args and mixed-difficulty examples
- Update `PRD.md` (this document)
- Update `TODO.md` with Sprint 2 tasks

---

## 9. Future Roadmap

| Priority | Feature                                   |
| -------- | ----------------------------------------- |
| Medium   | 2 puzzles per page layout option          |
| Low      | GUI (Tkinter or web)                      |
| Low      | 6×6 grid mode for kids                    |
| Low      | Export puzzle data as JSON alongside PDF  |
| Low      | Batch export (all 5 difficulties at once) |

---

## 10. Success Metrics

### v1.0 (Achieved)
- Generates valid, unique puzzles 100% of the time
- PDF opens and prints correctly on standard A4
- Single command from install to finished PDF
- No crashes on puzzle counts from 1 to 200

### v2.0 (Target)
- Mixed-difficulty PDFs render correct section dividers and grouped answer pages
- All three page sizes (A4, Letter, A5) produce correctly proportioned grids with no overflow
- Custom title and author render on cover without layout breakage for long strings (truncate gracefully at 40 chars)
- No regression on any v1.0 success metrics
