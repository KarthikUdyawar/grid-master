# Product Requirements Document
## Sudoku Book Generator

**Version:** 1.0  
**Status:** MVP Complete  
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

### In Scope (v1.0)
- CLI tool, single Python file
- 5 difficulty levels
- Configurable puzzle count
- PDF output: cover → puzzles → answers → back cover
- Unique-solution guarantee per puzzle
- A4 page size

### Out of Scope (Future)
- GUI or web interface
- Multiple page sizes (Letter, A5, pocket)
- Mixed difficulty in one book
- 6×6 or 16×16 grid variants
- Custom titles, author names, or branding
- Batch export (multiple difficulties at once)
- Puzzle numbering across difficulty sections

---

## 4. Functional Requirements

### FR-1: Puzzle Generation
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

### FR-2: CLI Interface
- Accept `--puzzles`, `--difficulty`, `--output` arguments
- Sensible defaults: 10 puzzles, medium, `sudoku_book.pdf`
- Print progress to stdout during generation

### FR-3: PDF Structure
- **Cover** — title, difficulty badge, puzzle count, styled background
- **Puzzle pages** — 1 puzzle per page, large grid, difficulty badge, page footer
- **Answer pages** — 6 answers per page (2 cols × 3 rows), given digits vs solved digits distinguished by color
- **Back cover** — matches front cover theme, completion message, decorative grid

### FR-4: Visual Design
- Each difficulty has a distinct accent color (green / blue / orange / red / purple)
- Alternating 3×3 box shading for readability
- Answer section: given digits dark gray, solved digits blue
- Cover and back cover: dark background, color-matched accents

---

## 5. Non-Functional Requirements

| Requirement        | Target                                             |
| ------------------ | -------------------------------------------------- |
| Single-file script | `main.py` only, no internal modules                |
| Dependency count   | 1 (`reportlab`)                                    |
| Output format      | PDF, A4, print-ready                               |
| Puzzle uniqueness  | 100% — enforced algorithmically                    |
| Generation speed   | ≤ 5s per puzzle at Master level (typical hardware) |
| Python version     | 3.7+                                               |

---

## 6. Technical Design

```
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

### Key Algorithms
- **Board fill:** recursive backtracking with shuffled digit order for randomness
- **Uniqueness check:** `count_solutions()` with early exit at 2 — if result > 1, cell removal is reverted
- **PDF layout:** all positions computed from page dimensions and gap constants — no hardcoded coords

---

## 7. File Structure

```
.
├── main.py          # Core script (generator + renderer)
├── README.md        # Usage documentation
├── PRD.md           # This document
├── pyproject.toml   # Project metadata
└── uv.lock          # Dependency lock file
```

---

## 8. Future Roadmap

| Priority | Feature                                             |
| -------- | --------------------------------------------------- |
| High     | Mixed-difficulty book (e.g. 10 easy + 10 hard)      |
| High     | Custom page size flag (`--pagesize letter\|a4\|a5`) |
| Medium   | 2 puzzles per page layout option                    |
| Medium   | Custom book title and author name on cover          |
| Low      | GUI (Tkinter or web)                                |
| Low      | 6×6 grid mode for kids                              |
| Low      | Export puzzle data as JSON alongside PDF            |

---

## 9. Success Metrics

- Generates valid, unique puzzles 100% of the time
- PDF opens and prints correctly on standard A4
- Single command from install to finished PDF
- No crashes on puzzle counts from 1 to 200
