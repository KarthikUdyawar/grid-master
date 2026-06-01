# Sudoku Book Generator — Sprint 1: MVP

**Duration:** Week 1 (Days 1–7)  
**Goal:** A working CLI tool that generates a print-ready Sudoku PDF book with cover, puzzles, answers, and back cover.

**Branch strategy:** Direct commit to `master` (v1.0)

---

## Sprint Goal

> *A user can run a single command and receive a complete, print-ready Sudoku PDF book with their chosen difficulty and puzzle count — with all puzzles guaranteed to have a unique solution.*

---

## Backlog

### 🏗️ SUB-1 — Sudoku Engine
**Branch:** `master`

- [x] Implement `fill_board()` — recursive backtracking with randomized digit order
- [x] Implement `is_valid()` — row, column, and 3×3 box constraint check
- [x] Implement `count_solutions()` — uniqueness verifier with early exit at 2
- [x] Implement `make_puzzle()` — remove cells one by one, revert if uniqueness breaks
- [x] Verify 100% unique-solution guarantee across all difficulty levels

---

### ⚙️ SUB-2 — CLI Interface
**Branch:** `master`

- [x] Add `--puzzles` argument (default: 10)
- [x] Add `--difficulty` argument with choices: `easy`, `medium`, `hard`, `expert`, `master`
- [x] Add `--output` argument (default: `sudoku_book.pdf`)
- [x] Print per-puzzle progress to stdout during generation

---

### 🗄️ SUB-3 — Difficulty Configuration
**Branch:** `master`

- [x] Define 5 levels with blank count and accent color
- [x] Easy — 32 blanks (green)
- [x] Medium — 40 blanks (blue)
- [x] Hard — 48 blanks (orange)
- [x] Expert — 54 blanks (red)
- [x] Master — 58 blanks (purple)

---

### 🎨 SUB-4 — PDF Layout & Rendering
**Branch:** `master`

- [x] Set up ReportLab canvas on A4 pagesize
- [x] Implement `draw_cover()` — dark background, title, difficulty badge, puzzle count
- [x] Implement `draw_puzzle_page()` — large grid (460px), compact header/footer, no wasted whitespace
- [x] Implement `draw_answer_section()` — 6 grids per page (2 cols × 3 rows), auto-sized to fit
- [x] Implement `draw_back_cover()` — matching dark theme, accent bars, decorative grid, completion message
- [x] Implement `draw_grid()` — alternating 3×3 box shading, bold thick box borders, thin cell lines

---

### 🖌️ SUB-5 — Visual Design
**Branch:** `master`

- [x] Difficulty-specific accent color applied to cover, badges, answer labels, back cover
- [x] Answer section: given digits in dark gray, solved digits in blue
- [x] Puzzle page: difficulty badge under title, puzzle number, footer with page count
- [x] Cover: faint decorative grid overlay on dark background
- [x] Back cover: top + bottom accent bars, tagline, puzzle count summary

---

### 📄 SUB-6 — Documentation
**Branch:** `master`

- [x] Write `README.md` — install, usage, CLI args, difficulty table, PDF structure, customization
- [x] Write `PRD.md` — problem, users, scope, requirements, tech design, roadmap, success metrics
- [x] Write `TODO.md` — this document

---

## Definition of Done

- [x] Single command generates valid PDF end-to-end
- [x] All puzzles have unique solutions (algorithmically enforced)
- [x] PDF contains: cover → puzzles → answers (6/page) → back cover
- [x] All 5 difficulty levels tested and working
- [x] `README.md`, `PRD.md`, and `TODO.md` written
- [x] No crashes on puzzle counts from 1 to 200

---

## Out of Scope (→ Sprint 2)

- Mixed-difficulty book (multiple levels in one PDF)
- Custom page size flag (`--pagesize letter|a4|a5`)
- 2 puzzles per page layout option
- Custom book title and author name on cover
- GUI (Tkinter or web)
- 6×6 grid mode for kids / beginners
- Export puzzle data as JSON alongside PDF
- Batch export (generate all 5 difficulties in one run)

---

## Decision Log

| Decision                                 | Reason                                                                        |
| ---------------------------------------- | ----------------------------------------------------------------------------- |
| Single `.py` file, no modules            | Simplicity — easy to share, run, and modify with zero project overhead        |
| ReportLab over other PDF libs            | Mature, pure-Python, no system dependencies, precise canvas control           |
| Uniqueness check via `count_solutions()` | Guarantees puzzle quality — stops removal the moment a second solution exists |
| 6 answers per page (2×3) over 4 (2×2)    | Better paper efficiency while keeping grids readable                          |
| Direct commit to `master`                | v1.0 MVP — no parallel feature work, branching overhead not justified yet     |
| A4 only (no Letter)                      | Single clear target for v1.0; page size flag deferred to Sprint 2             |
