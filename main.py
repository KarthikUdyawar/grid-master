"""
Sudoku Book Generator
Usage: python main.py --puzzles 10 --difficulty medium --output sudoku_book.pdf
Difficulties: easy, medium, hard, expert, master
"""

import argparse
import random
import copy
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ─── Difficulty Config ───────────────────────────────────────────────────────
DIFFICULTY = {
    "easy": {"blanks": 32, "label": "Easy", "color": (0.2, 0.6, 0.2)},
    "medium": {"blanks": 40, "label": "Medium", "color": (0.1, 0.4, 0.8)},
    "hard": {"blanks": 48, "label": "Hard", "color": (0.8, 0.5, 0.0)},
    "expert": {"blanks": 54, "label": "Expert", "color": (0.8, 0.1, 0.1)},
    "master": {"blanks": 58, "label": "Master", "color": (0.4, 0.0, 0.6)},
}

# ─── Sudoku Generator ────────────────────────────────────────────────────────


def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False
    br, bc = 3 * (row // 3), 3 * (col // 3)
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == num:
                return False
    return True


def fill_board(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if fill_board(board):
                            return True
                        board[row][col] = 0
                return False
    return True


def count_solutions(board, limit=2):
    count = [0]

    def solve(b):
        if count[0] >= limit:
            return
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    for n in range(1, 10):
                        if is_valid(b, r, c, n):
                            b[r][c] = n
                            solve(b)
                            b[r][c] = 0
                    return
        count[0] += 1

    solve([row[:] for row in board])
    return count[0]


def make_puzzle(blanks):
    board = [[0] * 9 for _ in range(9)]
    fill_board(board)
    solution = copy.deepcopy(board)

    puzzle = copy.deepcopy(board)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    removed = 0
    for r, c in cells:
        if removed >= blanks:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        if count_solutions(puzzle) == 1:
            removed += 1
        else:
            puzzle[r][c] = backup

    return puzzle, solution


# ─── Page Size ───────────────────────────────────────────────────────────────


def resolve_page_size(size: str) -> tuple:
    from reportlab.lib.pagesizes import A4, A5, LETTER

    sizes = {
        "a4": A4,
        "letter": LETTER,
        "a5": A5,
    }
    if size not in sizes:
        raise ValueError(f"Unknown page size: '{size}'. Choose from: {list(sizes)}")
    return sizes[size]


# ─── Title / Author ──────────────────────────────────────────────────────────

MAX_TITLE_CHARS = 40


def truncate_title(title: str, max_chars: int = MAX_TITLE_CHARS) -> str:
    if len(title) <= max_chars:
        return title
    return title[: max_chars - 1] + "…"


# ─── Difficulty Parsing ──────────────────────────────────────────────────────


def parse_difficulty(raw: str) -> list:
    tokens = [t.strip().lower() for t in raw.split(",")]
    for token in tokens:
        if token not in DIFFICULTY:
            raise ValueError(
                f"Unknown difficulty: '{token}'. Choose from: {list(DIFFICULTY)}"
            )
    return tokens


def parse_puzzle_counts(raw: str, num_levels: int) -> list:
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) == 1:
        count = int(parts[0])
        return [count] * num_levels
    counts = [int(p) for p in parts]
    if len(counts) != num_levels:
        raise ValueError(
            f"Got {len(counts)} counts but {num_levels} difficulty levels. "
            "Provide one count or one per level."
        )
    return counts


# ─── Puzzle Groups ───────────────────────────────────────────────────────────

from collections import namedtuple

PuzzleGroup = namedtuple("PuzzleGroup", ["config", "puzzles", "solutions"])


def build_puzzle_groups(difficulties: list, counts: list) -> list:
    groups = []
    for difficulty, count in zip(difficulties, counts):
        config = DIFFICULTY[difficulty]
        puzzles, solutions = [], []
        for i in range(count):
            print(f"  [{config['label']}] Puzzle {i+1}/{count}...", end="\r")
            p, s = make_puzzle(config["blanks"])
            puzzles.append(p)
            solutions.append(s)
        print()
        groups.append(PuzzleGroup(config=config, puzzles=puzzles, solutions=solutions))
    return groups


# ─── PDF Drawing ─────────────────────────────────────────────────────────────

ANSWERS_PER_PAGE_DEFAULT = 6  # 2 cols × 3 rows
ANSWERS_PER_PAGE_A5 = 4  # 2 cols × 2 rows


def _answers_layout(page_w, page_h):
    """Return (n_cols, n_rows, per_page) based on page dimensions."""
    is_a5 = page_h < 600
    if is_a5:
        return 2, 2, ANSWERS_PER_PAGE_A5
    return 2, 3, ANSWERS_PER_PAGE_DEFAULT


def draw_grid(c, ox, oy, board, solution_board=None, size=190):
    cell = size / 9

    c.setFillColorRGB(0.98, 0.98, 0.98)
    c.rect(ox, oy, size, size, fill=1, stroke=0)

    c.setFillColorRGB(0.93, 0.93, 0.95)
    for br in range(3):
        for bc in range(3):
            if (br + bc) % 2 == 0:
                c.rect(
                    ox + bc * 3 * cell,
                    oy + br * 3 * cell,
                    3 * cell,
                    3 * cell,
                    fill=1,
                    stroke=0,
                )

    board_to_draw = solution_board if solution_board else board
    font_size = max(8, int(size / 18))
    for row in range(9):
        for col in range(9):
            val = board_to_draw[row][col]
            if val != 0:
                x = ox + col * cell + cell / 2
                y = oy + (8 - row) * cell + cell / 2 - font_size * 0.35
                if solution_board:
                    if board[row][col] != 0:
                        c.setFillColorRGB(0.2, 0.2, 0.2)
                    else:
                        c.setFillColorRGB(0.1, 0.4, 0.8)
                else:
                    c.setFillColorRGB(0.1, 0.1, 0.1)
                c.setFont(
                    "Helvetica-Bold" if board[row][col] != 0 else "Helvetica", font_size
                )
                c.drawCentredString(x, y, str(val))

    for i in range(10):
        lw = 2.5 if i % 3 == 0 else 0.5
        c.setLineWidth(lw)
        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        c.line(ox, oy + i * cell, ox + size, oy + i * cell)
        c.line(ox + i * cell, oy, ox + i * cell, oy + size)


def draw_puzzle_page(c, puzzle, solution, config, puzzle_num, total, page_w, page_h):
    margin = 25
    header_h = 80
    footer_h = 30

    c.setFillColorRGB(*config["color"])
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(page_w / 2, page_h - 45, f"Puzzle #{puzzle_num}")

    badge_x, badge_y = page_w / 2 - 45, page_h - 68
    c.setFillColorRGB(*config["color"])
    c.roundRect(badge_x, badge_y, 90, 20, 6, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(page_w / 2, badge_y + 6, config["label"])

    available_h = page_h - header_h - footer_h
    available_w = page_w - 2 * margin
    grid_sz = int(min(available_w, available_h))
    ox = (page_w - grid_sz) / 2
    oy = footer_h + (available_h - grid_sz) / 2
    draw_grid(c, ox, oy, puzzle, size=grid_sz)

    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 8)
    c.drawCentredString(
        page_w / 2, 18, f"Puzzle {puzzle_num} of {total}  •  Answers at back"
    )


def draw_cover(c, groups, title, author, page_w, page_h):
    c.setFillColorRGB(0.05, 0.05, 0.15)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    c.setStrokeColorRGB(1, 1, 1, 0.05)
    c.setLineWidth(0.3)
    for i in range(0, int(page_w), 30):
        c.line(i, 0, i, page_h)
    for j in range(0, int(page_h), 30):
        c.line(0, j, page_w, j)

    display_title = truncate_title(title)
    first_color = groups[0].config["color"]

    c.setFillColorRGB(*first_color)
    c.setFont("Helvetica-Bold", 52)
    c.drawCentredString(page_w / 2, page_h - 160, display_title.upper())

    author_y = page_h - 200
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica", 22)
    c.drawCentredString(page_w / 2, author_y, "Puzzle Book")

    if author:
        author_y -= 32
        c.setFillColorRGB(0.7, 0.7, 0.7)
        c.setFont("Helvetica", 14)
        c.drawCentredString(page_w / 2, author_y, f"by {author}")

    # Multi-level badge row
    badge_labels = [g.config["label"] for g in groups]
    badge_text = "  ·  ".join(badge_labels).upper()
    badge_w = max(160, len(badge_text) * 8)
    badge_x = page_w / 2 - badge_w / 2
    badge_y = page_h / 2 + 40
    c.setFillColorRGB(*first_color)
    c.roundRect(badge_x, badge_y, badge_w, 40, 12, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_w / 2, badge_y + 14, badge_text)

    total = sum(len(g.puzzles) for g in groups)
    c.setFillColorRGB(0.8, 0.8, 0.8)
    c.setFont("Helvetica", 14)
    c.drawCentredString(page_w / 2, page_h / 2 - 10, f"{total} Unique Puzzles")
    c.drawCentredString(page_w / 2, page_h / 2 - 35, "Answers Included")

    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.setFont("Helvetica", 10)
    c.drawCentredString(page_w / 2, 40, "All puzzles have a unique solution")


def draw_section_divider(c, config, page_w, page_h):
    c.setFillColorRGB(*config["color"])
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(page_w / 2, page_h / 2 + 20, config["label"].upper())

    c.setFont("Helvetica", 18)
    c.drawCentredString(page_w / 2, page_h / 2 - 20, "— Puzzles —")


def draw_answer_section(c, groups, page_w, page_h):
    n_cols, n_rows, per_page = _answers_layout(page_w, page_h)
    label_h = 14
    col_gap = 14
    row_gap = 24
    header_h = 52
    margin_x = 28
    margin_bottom = 22

    usable_w = page_w - 2 * margin_x
    usable_h = page_h - header_h - margin_bottom
    ans_w = (usable_w - (n_cols - 1) * col_gap) / n_cols
    ans_h = (usable_h - (n_rows - 1) * row_gap - n_rows * label_h) / n_rows
    ans_size = int(min(ans_w, ans_h))
    total_w = n_cols * ans_size + (n_cols - 1) * col_gap
    x0 = (page_w - total_w) / 2

    def grid_y(row):
        return (
            page_h
            - header_h
            - label_h
            - ans_size
            - row * (ans_size + label_h + row_gap)
        )

    global_idx = 0
    page_num = 0

    for group in groups:
        config = group.config
        for batch_start in range(0, len(group.puzzles), per_page):
            c.showPage()
            page_num += 1

            c.setFillColorRGB(*config["color"])
            c.setFont("Helvetica-Bold", 20)
            section_header = f"Answers — {config['label']}"
            c.drawCentredString(page_w / 2, page_h - 36, section_header)
            c.setStrokeColorRGB(*config["color"])
            c.setLineWidth(1.2)
            c.line(margin_x, page_h - 44, page_w - margin_x, page_h - 44)

            batch = list(
                zip(
                    group.puzzles[batch_start : batch_start + per_page],
                    group.solutions[batch_start : batch_start + per_page],
                )
            )

            for idx, (puzzle, solution) in enumerate(batch):
                col = idx % n_cols
                row = idx // n_cols
                ox = x0 + col * (ans_size + col_gap)
                oy = grid_y(row)
                pnum = global_idx + batch_start + idx + 1
                c.setFillColorRGB(*config["color"])
                c.setFont("Helvetica-Bold", 9)
                c.drawCentredString(ox + ans_size / 2, oy + ans_size + 4, f"#{pnum}")
                draw_grid(c, ox, oy, puzzle, solution_board=solution, size=ans_size)

            c.setFillColorRGB(0.6, 0.6, 0.6)
            c.setFont("Helvetica", 7)
            c.drawCentredString(page_w / 2, 12, f"Answers — Page {page_num}")

        global_idx += len(group.puzzles)


def draw_back_cover(c, groups, author, page_w, page_h):
    total = sum(len(g.puzzles) for g in groups)
    cfg = groups[0].config

    c.setFillColorRGB(0.05, 0.05, 0.15)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    c.setStrokeColorRGB(1, 1, 1, 0.04)
    c.setLineWidth(0.3)
    for i in range(0, int(page_w), 30):
        c.line(i, 0, i, page_h)
    for j in range(0, int(page_h), 30):
        c.line(0, j, page_w, j)

    c.setFillColorRGB(*cfg["color"])
    c.rect(0, page_h - 8, page_w, 8, fill=1, stroke=0)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(page_w / 2, page_h - 120, "Thanks for Solving!")

    level_summary = " · ".join(g.config["label"] for g in groups)
    c.setFillColorRGB(0.75, 0.75, 0.75)
    c.setFont("Helvetica", 13)
    c.drawCentredString(
        page_w / 2, page_h - 155, f"You completed {total} puzzles: {level_summary}."
    )

    if author:
        c.setFillColorRGB(0.6, 0.6, 0.6)
        c.setFont("Helvetica", 11)
        c.drawCentredString(page_w / 2, page_h - 178, f"by {author}")

    c.setStrokeColorRGB(*cfg["color"])
    c.setLineWidth(1.5)
    divider_y = page_h - 195
    c.line(page_w / 2 - 80, divider_y, page_w / 2 + 80, divider_y)

    gs = 160
    cell = gs / 9
    ox = (page_w - gs) / 2
    oy = page_h / 2 - gs / 2 + 20
    c.setFillColorRGB(1, 1, 1, 0.04)
    c.rect(ox, oy, gs, gs, fill=1, stroke=0)
    for i in range(10):
        lw = 1.8 if i % 3 == 0 else 0.4
        c.setLineWidth(lw)
        c.setStrokeColorRGB(*cfg["color"], 0.5 if i % 3 == 0 else 0.2)
        c.line(ox, oy + i * cell, ox + gs, oy + i * cell)
        c.line(ox + i * cell, oy, ox + i * cell, oy + gs)

    c.setFillColorRGB(*cfg["color"])
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_w / 2, oy - 28, "SUDOKU  •  PUZZLE BOOK")

    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 10)
    c.drawCentredString(
        page_w / 2,
        oy - 48,
        f"{level_summary}  •  {total} Unique Puzzles  •  Answers Included",
    )

    c.setFillColorRGB(*cfg["color"])
    c.rect(0, 0, page_w, 8, fill=1, stroke=0)


# ─── Book Generation ─────────────────────────────────────────────────────────


def generate_book(difficulties, counts, title, author, pagesize, output):
    page_w, page_h = resolve_page_size(pagesize)
    total = sum(counts)
    print(f"Generating {total} puzzles across {len(difficulties)} level(s)...")

    groups = build_puzzle_groups(difficulties, counts)
    print(f"All puzzles generated. Writing PDF...")

    c = canvas.Canvas(output, pagesize=(page_w, page_h))
    c.setTitle(f"{title} — Sudoku Book")

    draw_cover(c, groups, title=title, author=author, page_w=page_w, page_h=page_h)

    for group_idx, group in enumerate(groups):
        if group_idx > 0:
            c.showPage()
            draw_section_divider(c, group.config, page_w, page_h)

        puzzle_offset = sum(len(groups[i].puzzles) for i in range(group_idx))
        total_puzzles = sum(len(g.puzzles) for g in groups)

        for i, (puzzle, solution) in enumerate(zip(group.puzzles, group.solutions)):
            c.showPage()
            draw_puzzle_page(
                c,
                puzzle,
                solution,
                group.config,
                puzzle_offset + i + 1,
                total_puzzles,
                page_w,
                page_h,
            )

    draw_answer_section(c, groups, page_w, page_h)

    c.showPage()
    draw_back_cover(c, groups, author=author, page_w=page_w, page_h=page_h)

    c.save()
    print(f"Done! Saved to: {output}")


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Sudoku PDF book")
    parser.add_argument(
        "--puzzles", default="10", help="Puzzle count (single or comma list)"
    )
    parser.add_argument(
        "--difficulty", default="medium", help="Difficulty (single or comma list)"
    )
    parser.add_argument("--output", default="sudoku_book.pdf")
    parser.add_argument("--pagesize", default="a4", choices=["a4", "letter", "a5"])
    parser.add_argument("--title", default="Sudoku")
    parser.add_argument("--author", default="")
    args = parser.parse_args()

    difficulties = parse_difficulty(args.difficulty)
    counts = parse_puzzle_counts(args.puzzles, len(difficulties))
    generate_book(
        difficulties, counts, args.title, args.author, args.pagesize, args.output
    )
