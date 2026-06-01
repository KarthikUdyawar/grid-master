"""
Sudoku Book Generator
Usage: python sudoku_book.py --puzzles 10 --difficulty medium --output sudoku_book.pdf
Difficulties: easy, medium, hard, expert, master
"""

import argparse
import random
import copy
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ─── Difficulty Config ───────────────────────────────────────────────────────
# blanks = number of cells removed
# techniques = solving techniques required (for labeling)
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
    """Count solutions up to limit (used to verify uniqueness)."""
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
    """Generate solved board + puzzle with exactly `blanks` cells removed, unique solution."""
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
            puzzle[r][c] = backup  # revert if uniqueness breaks

    return puzzle, solution


# ─── PDF Drawing ─────────────────────────────────────────────────────────────

PAGE_W, PAGE_H = A4
GRID_SIZE = 460  # bigger grid, less whitespace
CELL = GRID_SIZE / 9


def draw_grid(c, ox, oy, board, solution_board=None, small=False, size=None):
    """Draw a 9x9 sudoku grid at origin (ox, oy). small=True for answer section."""
    if size is None:
        size = GRID_SIZE if not small else 190
    cell = size / 9

    # Background
    c.setFillColorRGB(0.98, 0.98, 0.98)
    c.rect(ox, oy, size, size, fill=1, stroke=0)

    # Box shading for 3x3
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

    # Numbers
    board_to_draw = solution_board if solution_board else board
    font_size = 18 if not small else int(size / 18)
    for row in range(9):
        for col in range(9):
            val = board_to_draw[row][col]
            if val != 0:
                x = ox + col * cell + cell / 2
                y = oy + (8 - row) * cell + cell / 2 - font_size * 0.35
                if solution_board:
                    # answer mode: color given vs solved
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

    # Grid lines
    for i in range(10):
        lw = 2.5 if i % 3 == 0 else 0.5
        c.setLineWidth(lw)
        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        # horizontal
        c.line(ox, oy + i * cell, ox + size, oy + i * cell)
        # vertical
        c.line(ox + i * cell, oy, ox + i * cell, oy + size)


def draw_puzzle_page(c, puzzle, solution, difficulty, puzzle_num, total):
    cfg = DIFFICULTY[difficulty]

    # Header — tight to top
    c.setFillColorRGB(*cfg["color"])
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 45, f"Puzzle #{puzzle_num}")

    # Difficulty badge — smaller, right under title
    badge_x, badge_y = PAGE_W / 2 - 45, PAGE_H - 68
    c.setFillColorRGB(*cfg["color"])
    c.roundRect(badge_x, badge_y, 90, 20, 6, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W / 2, badge_y + 6, cfg["label"])

    # Grid — max size, centered in remaining space
    margin = 25
    available = PAGE_H - 75 - 30  # top header ~75, bottom footer ~30
    grid_sz = min(GRID_SIZE, PAGE_W - 2 * margin, available)
    ox = (PAGE_W - grid_sz) / 2
    oy = 30 + (available - grid_sz) / 2  # vertically center in available area
    draw_grid(c, ox, oy, puzzle, size=grid_sz)

    # Footer — tight to bottom
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 8)
    c.drawCentredString(
        PAGE_W / 2, 18, f"Puzzle {puzzle_num} of {total}  •  Answers at back"
    )


def draw_cover(c, total, difficulty):
    cfg = DIFFICULTY[difficulty]
    # Gradient-like background via rectangles
    c.setFillColorRGB(0.05, 0.05, 0.15)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Decorative grid pattern (faint)
    c.setStrokeColorRGB(1, 1, 1, 0.05)
    c.setLineWidth(0.3)
    for i in range(0, int(PAGE_W), 30):
        c.line(i, 0, i, PAGE_H)
    for j in range(0, int(PAGE_H), 30):
        c.line(0, j, PAGE_W, j)

    # Title
    c.setFillColorRGB(*cfg["color"])
    c.setFont("Helvetica-Bold", 52)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 160, "SUDOKU")
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica", 22)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 200, "Puzzle Book")

    # Badge
    c.setFillColorRGB(*cfg["color"])
    c.roundRect(PAGE_W / 2 - 80, PAGE_H / 2 + 40, 160, 40, 12, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 55, cfg["label"].upper() + " LEVEL")

    # Stats
    c.setFillColorRGB(0.8, 0.8, 0.8)
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 10, f"{total} Unique Puzzles")
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 35, "Answers Included")

    # Bottom
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_W / 2, 40, "All puzzles have a unique solution")


def draw_answer_section(c, puzzles, solutions, difficulty):
    """Draw answer pages: 6 mini grids per page, 3 cols x 2 rows."""
    cfg = DIFFICULTY[difficulty]
    per_page = 6
    n_cols, n_rows = 2, 3
    label_h = 14  # height above each grid for puzzle number
    col_gap = 14
    row_gap = 24
    header_h = 52  # "Answers" header
    margin_x = 28
    margin_bottom = 22

    usable_w = PAGE_W - 2 * margin_x
    usable_h = PAGE_H - header_h - margin_bottom

    # Calc grid size to fit exactly 3 cols x 2 rows
    ans_w = (usable_w - (n_cols - 1) * col_gap) / n_cols
    ans_h = (usable_h - (n_rows - 1) * row_gap - n_rows * label_h) / n_rows
    ans_size = int(min(ans_w, ans_h))

    # Recompute gaps to center nicely
    total_w = n_cols * ans_size + (n_cols - 1) * col_gap
    x0 = (PAGE_W - total_w) / 2

    # Top of first grid row (reportlab Y = bottom of grid)
    # row 0 grid bottom = PAGE_H - header_h - label_h - ans_size
    def grid_y(row):
        return (
            PAGE_H
            - header_h
            - label_h
            - ans_size
            - row * (ans_size + label_h + row_gap)
        )

    page_num = 0
    for page_start in range(0, len(puzzles), per_page):
        c.showPage()
        page_num += 1

        # Header
        c.setFillColorRGB(*cfg["color"])
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 36, "Answers")
        c.setStrokeColorRGB(*cfg["color"])
        c.setLineWidth(1.2)
        c.line(margin_x, PAGE_H - 44, PAGE_W - margin_x, PAGE_H - 44)

        page_slice = list(
            zip(
                puzzles[page_start : page_start + per_page],
                solutions[page_start : page_start + per_page],
            )
        )

        for idx, (puzzle, solution) in enumerate(page_slice):
            col = idx % n_cols
            row = idx // n_cols
            ox = x0 + col * (ans_size + col_gap)
            oy = grid_y(row)

            pnum = page_start + idx + 1
            c.setFillColorRGB(*cfg["color"])
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(ox + ans_size / 2, oy + ans_size + 4, f"#{pnum}")
            draw_grid(
                c, ox, oy, puzzle, solution_board=solution, small=True, size=ans_size
            )

        # Footer
        c.setFillColorRGB(0.6, 0.6, 0.6)
        c.setFont("Helvetica", 7)
        c.drawCentredString(PAGE_W / 2, 12, f"Answers — Page {page_num}")


def draw_back_cover(c, total, difficulty):
    cfg = DIFFICULTY[difficulty]

    # Dark background
    c.setFillColorRGB(0.05, 0.05, 0.15)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Faint grid pattern
    c.setStrokeColorRGB(1, 1, 1, 0.04)
    c.setLineWidth(0.3)
    for i in range(0, int(PAGE_W), 30):
        c.line(i, 0, i, PAGE_H)
    for j in range(0, int(PAGE_H), 30):
        c.line(0, j, PAGE_W, j)

    # Top accent bar
    c.setFillColorRGB(*cfg["color"])
    c.rect(0, PAGE_H - 8, PAGE_W, 8, fill=1, stroke=0)

    # "Thank you" message
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 120, "Thanks for Solving!")

    c.setFillColorRGB(0.75, 0.75, 0.75)
    c.setFont("Helvetica", 13)
    c.drawCentredString(
        PAGE_W / 2, PAGE_H - 155, f"You completed {total} {cfg['label']} puzzles."
    )

    # Divider
    c.setStrokeColorRGB(*cfg["color"])
    c.setLineWidth(1.5)
    c.line(PAGE_W / 2 - 80, PAGE_H - 175, PAGE_W / 2 + 80, PAGE_H - 175)

    # Mini decorative sudoku grid (empty, just lines)
    gs = 160
    cell = gs / 9
    ox = (PAGE_W - gs) / 2
    oy = PAGE_H / 2 - gs / 2 + 20
    c.setFillColorRGB(1, 1, 1, 0.04)
    c.rect(ox, oy, gs, gs, fill=1, stroke=0)
    for i in range(10):
        lw = 1.8 if i % 3 == 0 else 0.4
        c.setLineWidth(lw)
        c.setStrokeColorRGB(*cfg["color"], 0.5 if i % 3 == 0 else 0.2)
        c.line(ox, oy + i * cell, ox + gs, oy + i * cell)
        c.line(ox + i * cell, oy, ox + i * cell, oy + gs)

    # Tagline
    c.setFillColorRGB(*cfg["color"])
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(PAGE_W / 2, oy - 28, "SUDOKU  •  PUZZLE BOOK")

    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 10)
    c.drawCentredString(
        PAGE_W / 2,
        oy - 48,
        f"{cfg['label']} Level  •  {total} Unique Puzzles  •  Answers Included",
    )

    # Bottom accent bar
    c.setFillColorRGB(*cfg["color"])
    c.rect(0, 0, PAGE_W, 8, fill=1, stroke=0)


# ─── Main ────────────────────────────────────────────────────────────────────


def generate_book(num_puzzles, difficulty, output):
    print(f"Generating {num_puzzles} {difficulty} puzzles...")
    blanks = DIFFICULTY[difficulty]["blanks"]

    puzzles, solutions = [], []
    for i in range(num_puzzles):
        print(f"  Puzzle {i+1}/{num_puzzles}...", end="\r")
        p, s = make_puzzle(blanks)
        puzzles.append(p)
        solutions.append(s)
    print(f"\nAll {num_puzzles} puzzles generated. Writing PDF...")

    c = canvas.Canvas(output, pagesize=A4)
    c.setTitle(f"Sudoku Book — {DIFFICULTY[difficulty]['label']}")

    # Cover
    draw_cover(c, num_puzzles, difficulty)

    # Puzzle pages
    for i, (puzzle, solution) in enumerate(zip(puzzles, solutions)):
        c.showPage()
        draw_puzzle_page(c, puzzle, solution, difficulty, i + 1, num_puzzles)

    # Answer section
    draw_answer_section(c, puzzles, solutions, difficulty)

    # Back cover
    c.showPage()
    draw_back_cover(c, num_puzzles, difficulty)

    c.save()
    print(f"Done! Saved to: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Sudoku PDF book")
    parser.add_argument("--puzzles", type=int, default=10, help="Number of puzzles")
    parser.add_argument("--difficulty", choices=DIFFICULTY.keys(), default="medium")
    parser.add_argument("--output", default="sudoku_book.pdf")
    args = parser.parse_args()
    generate_book(args.puzzles, args.difficulty, args.output)
