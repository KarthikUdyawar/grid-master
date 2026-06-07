# Sudoku Book Generator — Sprint 2: Customization

**Duration:** Week 2 (Days 8–14)
**Goal:** Mixed-difficulty books, multi-page-size support, custom title/author on cover.

**Branch strategy:** Direct commit to `master` (v2.0)

---

## Sprint Goal

> *User runs one command and gets a print-ready PDF with mixed difficulty levels, correct page size, and their own title/author — with zero layout breakage.*

---

## Backlog

### 📐 SUB-7 — Page Size Support
**Branch:** `master`

**Behaviors to test (TDD order):**
- [ ] `resolve_page_size("a4")` → `(595, 842)`
- [ ] `resolve_page_size("letter")` → `(612, 792)`
- [ ] `resolve_page_size("a5")` → `(420, 595)`
- [ ] Unknown size → raises `ValueError`
- [ ] A5 answer section → 4 grids/page (2×2), not 6
- [ ] Grid dims scale proportionally per page size

**Tasks:**
- [ ] Extract `resolve_page_size(size: str) -> tuple` — single responsibility, no side effects
- [ ] Refactor all layout fns: replace module-level `PAGE_W/H` constants with `(page_w, page_h)` params
- [ ] `draw_answer_section()` → branch on page size: A5 → 2×2, else → 2×3
- [ ] Add `--pagesize` arg: choices `["a4", "letter", "a5"]`, default `"a4"`
- [ ] Test all 3 sizes end-to-end, verify no grid overflow

**Clean Code notes:**
- `resolve_page_size` = pure fn, no globals
- Layout fns: `page_w, page_h` as explicit params, not globals mutated at runtime
- Name: `grid_cell_size` not `s` or `sz`

---

### 🖊️ SUB-8 — Custom Title & Author
**Branch:** `master`

**Behaviors to test (TDD order):**
- [ ] Cover renders `--title` value (default `"Sudoku"`)
- [ ] Cover renders `--author` when provided; hidden when empty
- [ ] Title >40 chars → truncated gracefully, no layout break
- [ ] Back cover renders author credit when `--author` set

**Tasks:**
- [ ] Add `--title` arg (default `"Sudoku"`)
- [ ] Add `--author` arg (default `""`)
- [ ] `draw_cover(title, author, ...)` — author line conditional on non-empty string
- [ ] `truncate_title(title: str, max_chars: int = 40) -> str` — clean fn, tested independently
- [ ] `draw_back_cover(author, ...)` — add small author credit if set

**Clean Code notes:**
- `truncate_title` = pure fn, one thing, no side effects
- No magic `40` inline — extract `MAX_TITLE_CHARS = 40`
- `draw_cover` signature: keyword args for `title` and `author`, not positional

---

### 🔀 SUB-9 — Mixed-Difficulty Book
**Branch:** `master`

**Behaviors to test (TDD order):**
- [ ] `parse_difficulty("easy")` → `["easy"]`
- [ ] `parse_difficulty("easy,hard,master")` → `["easy", "hard", "master"]`
- [ ] Invalid level → raises `ValueError` with clear message
- [ ] `parse_puzzle_counts("10", 3)` → `[10, 10, 10]` (broadcast single)
- [ ] `parse_puzzle_counts("5,10,5", 3)` → `[5, 10, 5]`
- [ ] Count list len ≠ difficulty list len → raises `ValueError`
- [ ] Mixed PDF → section divider page between each difficulty level
- [ ] Cover badge → multi-level list (e.g. `"Easy · Hard · Master"`)
- [ ] Answer section → grouped by level, color-matched headers

**Tasks:**
- [ ] `parse_difficulty(raw: str) -> list[str]` — split + validate each token
- [ ] `parse_puzzle_counts(raw: str, num_levels: int) -> list[int]` — broadcast or split
- [ ] `draw_section_divider(difficulty_config, page_w, page_h)` — full-bleed accent, centered name
- [ ] `build_puzzle_groups(difficulties, counts) -> list[PuzzleGroup]` — named tuple/dataclass, one fn per concern
- [ ] Update `draw_cover()` — render badge row for multiple levels
- [ ] Update `draw_answer_section()` — iterate by group, inject divider label per section
- [ ] Update `draw_back_cover()` — summary reflects total + level breakdown

**Clean Code notes:**
- `PuzzleGroup = namedtuple("PuzzleGroup", ["config", "puzzles"])` — no raw dicts
- `parse_*` fns = pure, tested independently, no I/O
- `draw_section_divider` = one fn, one responsibility, no conditional branching inside
- Do One Thing: `build_puzzle_groups` builds; `generate_puzzles` generates; never both

---

### 📄 SUB-10 — Documentation Update
**Branch:** `master`

- [ ] `README.md` — add `--pagesize`, `--title`, `--author`, mixed-difficulty examples
- [ ] `PRD.md` — already updated (v2.0, June 2026)
- [ ] `TODO.md` — this document

---

## TDD Cycle Order (recommended)

```
SUB-7: resolve_page_size → layout param refactor → A5 answer layout → CLI arg
SUB-8: truncate_title → draw_cover title → draw_cover author → back cover credit
SUB-9: parse_difficulty → parse_puzzle_counts → build_puzzle_groups → draw_section_divider → cover badge → answer grouping
```

One behavior → one test → minimal impl → next. No horizontal slicing.

---

## Definition of Done

- [ ] All 3 page sizes render without grid overflow
- [ ] Mixed-difficulty PDF: correct dividers, grouped answers, multi-badge cover
- [ ] `--title` and `--author` render; long title truncated gracefully
- [ ] All new fns: <20 lines, single responsibility, intention-revealing names
- [ ] Every new behavior has a corresponding passing test
- [ ] Zero regression on v1.0: single difficulty, A4, default title still works
- [ ] `README.md` updated with new CLI args and examples

---

## Decision Log

| Decision                                         | Reason                                                              |
| ------------------------------------------------ | ------------------------------------------------------------------- |
| `resolve_page_size` as pure fn                   | Testable without ReportLab; no global mutation                      |
| `page_w, page_h` explicit params                 | Layout fns stay pure; no implicit global dependency                 |
| `parse_difficulty` / `parse_puzzle_counts` split | Single responsibility; each independently testable                  |
| `PuzzleGroup` namedtuple over raw dict           | Intention-revealing; no magic key strings                           |
| `MAX_TITLE_CHARS = 40` constant                  | No magic numbers inline; single source of truth                     |
| TDD vertical slices, not horizontal              | Prevents testing imagined behavior; each test responds to real impl |
