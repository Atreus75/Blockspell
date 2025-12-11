# tetris.py
# Refatorado para API manual: spawn_piece_manual(forma:str, cor:str)
# Suporta formas: "O","I","T","L","S","."  ( "." => 1x1 bloco )
# Cores esperadas (português, minúsculo): "verde","azul","vermelho","amarelo"
# "amarelo" é tratado internamente como "yellow" (compatibilidade)
#
# Rotação e controles ficam a cargo do jogador (up,left,right,down,space).
# Nenhuma peça será gerada sem a chamada spawn_piece_manual.
#
# Leve otimização: evita cópias/iteração extra sempre que possível, mas mantém legibilidade.

import random
import pygame
from time import time
from PPlay.window import Window

# ---------- Helpers ----------
def _now_s():
    return time()

# map semantic color -> RGB for drawing in grid
_COLOR_RGB = {
    "verde": (0, 200, 0),
    "azul": (0, 120, 255),
    "vermelho": (200, 30, 30),
    # internal gold (we store as 'yellow' internally to keep previous integration)
    "yellow": (245, 238, 42),
}

# valid portuguese color inputs -> internal color key
_COLOR_INPUT_MAP = {
    "verde": "verde",
    "azul": "azul",
    "vermelho": "vermelho",
    "amarelo": "yellow",  # maps to internal 'yellow' for compatibility with blocklib expectation
}

# ---------- Tetris class ----------
class Tetris:
    """
    Tetris minimal, manual spawn API.
    Methods of interest:
      - spawn_piece_manual(forma:str, cor:str) -> bool
      - update(), draw(), reset()
      - get_last_cleared() -> list of dicts [{"red":..,"green":..,"blue":..,"yellow":..}, ...]
    """

    # shape matrices (1 = cell). Indexing pid starting at 1.
    # Order chosen: 1:I, 2:L, 3:O, 4:S, 5:T, 6:dot (.), adjust mapping below
    SHAPES = {
        # I (4x1)
        "I": [[1,1,1,1]],
        # L (2x3 representation matching earlier)
        "L": [[0,0,1],[1,1,1]],
        # O (2x2)
        "O": [[1,1],[1,1]],
        # S (2x3)
        "S": [[0,1,1],[1,1,0]],
        # T (2x3)
        "T": [[0,1,0],[1,1,1]],
        # single cell
        ".": [[1]],
    }

    # mapping from format string -> canonical format (upper-case) and pid not needed now (we use format)
    ALLOWED_FORMS = set(["O","I","T","L","S","."])

    # default fallback
    DEFAULT_FORM = "O"
    DEFAULT_COLOR_INPUT = "verde"

    def __init__(self, window: Window, cols=10, rows=15, cell_size=28, top_left=(40,40), log=False):
        # essentials
        self.last_locked_piece = 0
        self.window = window
        self.screen = window.get_screen()
        self.key = window.get_keyboard()

        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.top_left = top_left
        self.x, self.y = top_left

        # grid stores either 0 (empty) or tuple (format_str, color_internal)
        # color_internal will be one of "verde","azul","vermelho","yellow"
        self.grid = [[0]*self.cols for _ in range(self.rows)]

        # current piece dict or None
        # structure: {"form":str, "matrix":list[list[int]], "x":int, "y":int, "color":str_internal}
        self.current = None
        self.falling_piece = False


        # timers
        self.fall_interval = 0.8
        self.fall_timer = 0.0
        self.move_cooldown = 0.12
        self.move_timer = 0.0

        # flags
        self.game_over = False
        self.full_grid = False

        # last cleared lines info (list of dicts)
        self.last_cleared_color_counts = []

        # logging
        self.log_enabled = bool(log)

    # -------------------------
    # API: spawn_piece_manual
    # -------------------------
    def spawn_piece_manual(self, forma: str, cor: str) -> bool:
        """
        Spawns a piece immediately at the top-center and it starts falling.
        Parameters:
          forma: "O","I","T","L","S","."
          cor: "verde","azul","vermelho","amarelo" (português minúsculo)
        Returns True if spawn succeeded, False otherwise (e.g. immediate collision -> game over).
        If invalid inputs, substitutes defaults ("O","verde") per user's choice.
        """

        # normalize inputs
        if not isinstance(forma, str):
            forma = self.DEFAULT_FORM
        form = forma.strip().upper()
        if form not in self.ALLOWED_FORMS:
            if self.log_enabled:
                print(f"[TETRIS] spawn_piece_manual: formato inválido '{forma}', usando padrão '{self.DEFAULT_FORM}'")
            form = self.DEFAULT_FORM

        if not isinstance(cor, str):
            cor = self.DEFAULT_COLOR_INPUT
        color_in = cor.strip().lower()
        color_internal = _COLOR_INPUT_MAP.get(color_in)
        if color_internal is None:
            # fallback per option 9.B -> substitute default
            if self.log_enabled:
                print(f"[TETRIS] spawn_piece_manual: cor inválida '{cor}', usando padrão '{self.DEFAULT_COLOR_INPUT}'")
            color_internal = _COLOR_INPUT_MAP[self.DEFAULT_COLOR_INPUT]

        # get matrix copy (we store fresh list to avoid shared refs)
        base = self.SHAPES.get(form)
        if base is None:
            base = self.SHAPES[self.DEFAULT_FORM]
        # shallow copy rows to avoid mutation issues
        mat = [row[:] for row in base]

        # compute start x so piece is centered horizontally
        width = len(mat[0])
        start_x = (self.cols - width) // 2
        start_y = 0

        # if cannot place immediately -> game over
        if not self._can_place(mat, start_x, start_y):
            self.game_over = True
            if self.log_enabled:
                print("[TETRIS] spawn_piece_manual: colisão imediata -> GAME OVER")
            return False

        # create current piece
        self.current = {"form": form, "matrix": mat, "x": start_x, "y": start_y, "color": color_internal}
        self.fall_timer = 0.0
        self.move_timer = 0.0
        self.falling_piece = True 


        if self.log_enabled:
            print(f"[TETRIS] spawn_piece_manual: spawned form={form} color_internal={color_internal} at x={start_x},y={start_y}")
        return True

    # -------------------------
    # placement helpers
    # -------------------------
    def _can_place(self, mat, x, y):
        # check quickly
        rows = len(mat)
        cols = len(mat[0])
        if x < -cols or x > self.cols:  # fast reject
            return False
        for r in range(rows):
            row = mat[r]
            gy = y + r
            for c in range(cols):
                if row[c] == 0:
                    continue
                gx = x + c
                if gx < 0 or gx >= self.cols or gy >= self.rows:
                    return False
                if gy >= 0 and self.grid[gy][gx] != 0:
                    return False
        return True

    # -------------------------
    # locking and clearing
    # -------------------------
    def _lock_piece(self):
        cur = self.current
        if not cur:
            return []
        mat = cur["matrix"]
        x0 = cur["x"]
        y0 = cur["y"]
        color = cur["color"]
        form = cur["form"]

        placed_cells = []
        for r, row in enumerate(mat):
            gy = y0 + r
            for c, val in enumerate(row):
                if not val:
                    continue
                gx = x0 + c
                if 0 <= gx < self.cols and 0 <= gy < self.rows:
                    # store tuple (form, color_internal)
                    self.grid[gy][gx] = (form, color)
                    placed_cells.append((gx, gy))

        # clear lines
        cleared = self._clear_lines()
        self.last_cleared_color_counts = cleared

        # free current
        self.current = None

        # check top row for game-over/full_grid
        top_occupied = any(self.grid[0][c] != 0 for c in range(self.cols))
        self.full_grid = top_occupied
        if top_occupied:
            self.game_over = True

        if self.log_enabled:
            print(f"[TETRIS] locked piece form={form} color={color} placed {len(placed_cells)} cells, cleared_lines={len(cleared)}")
        self.falling_piece = False
        self.last_locked_piece = time()
        return cleared

    def _clear_lines(self):
        """
        Scan rows once, build new grid with removed full rows.
        Returns list of dicts with counts per semantic color {"red","green","blue","yellow"} in the order they were cleared (top->bottom).
        """
        out_counts = []
        write_rows = []  # rows to keep (not full)
        for r in range(self.rows):
            row = self.grid[r]
            full = True
            # check quickly if full
            for cell in row:
                if cell == 0:
                    full = False
                    break
            if full:
                # count colors in this row
                counts = {"red":0,"green":0,"blue":0,"yellow":0}
                for cell in row:
                    if not cell:
                        continue
                    # cell is (form,color_internal)
                    if isinstance(cell, tuple):
                        _, color_internal = cell
                        if color_internal == "verde":
                            counts["green"] += 1
                        elif color_internal == "azul":
                            counts["blue"] += 1
                        elif color_internal == "vermelho":
                            counts["red"] += 1
                        elif color_internal in ("yellow","dourado"):
                            counts["yellow"] += 1
                        else:
                            counts["red"] += 1
                    else:
                        # should not happen in refactored code; fallback map by form char
                        counts["red"] += 1
                out_counts.append(counts)
            else:
                write_rows.append(row)
        # insert empty rows on top
        if out_counts:
            new_grid = [[0]*self.cols for _ in range(len(out_counts))] + write_rows
            # ensure length equals rows
            if len(new_grid) != self.rows:
                # pad if necessary
                while len(new_grid) < self.rows:
                    new_grid.insert(0, [0]*self.cols)
                new_grid = new_grid[-self.rows:]
            self.grid = new_grid
        return out_counts

    # -------------------------
    # input handlers / movement
    # -------------------------
    def _try_move(self, dx):
        if not self.current:
            return
        nx = self.current["x"] + dx
        if self._can_place(self.current["matrix"], nx, self.current["y"]):
            self.current["x"] = nx

    def _try_rotate(self):
        if not self.current:
            return
        mat = self.current["matrix"]
        rotated = [list(row) for row in zip(*mat[::-1])]
        # simple kicks
        for k in (0, -1, 1, -2, 2):
            if self._can_place(rotated, self.current["x"] + k, self.current["y"]):
                self.current["matrix"] = rotated
                self.current["x"] += k
                return

    def _try_soft_drop(self):
        if not self.current:
            return
        if self._can_place(self.current["matrix"], self.current["x"], self.current["y"] + 1):
            self.current["y"] += 1
        else:
            self._lock_piece()

    def _try_hard_drop(self):
        if not self.current:
            return
        while self._can_place(self.current["matrix"], self.current["x"], self.current["y"] + 1):
            self.current["y"] += 1
        self._lock_piece()

    # -------------------------
    # public update & draw
    # -------------------------
    def update(self):
        """Call every frame from host game loop."""

        if self.game_over:
            self.falling_piece = False
            return
        
        if not self.current:
            self.falling_piece = False
        
        dt = self.window.delta_time()
        kb = self.key

        # movement input
        self.move_timer += dt
        if self.current:
            if kb.key_pressed("left") and self.move_timer >= self.move_cooldown:
                self._try_move(-1)
                self.move_timer = 0.0
            if kb.key_pressed("right") and self.move_timer >= self.move_cooldown:
                self._try_move(1)
                self.move_timer = 0.0
            if kb.key_pressed("up") and self.move_timer >= self.move_cooldown:
                self._try_rotate()
                self.move_timer = 0.0

            # drop controls
            fall_speed = 0.03 if kb.key_pressed("down") else self.fall_interval

            self.fall_timer += dt
            if self.fall_timer >= fall_speed:
                self.fall_timer = 0.0
                if self._can_place(self.current["matrix"], self.current["x"], self.current["y"] + 1):
                    self.current["y"] += 1
                else:
                    self._lock_piece()
        else:
            # no current piece: nothing to update for gravity (since spawn is manual)
            pass

        # hard drop
        if kb.key_pressed("space"):
            self._try_hard_drop()

    def draw(self):
        """Draw board and current piece; call before window.update()."""
        screen = self.screen
        bx, by = self.top_left
        board_w = self.cols * self.cell_size
        board_h = self.rows * self.cell_size

        # background
        pygame.draw.rect(screen, (40,40,40), (bx-4, by-4, board_w+8, board_h+8))
        pygame.draw.rect(screen, (10,10,10), (bx, by, board_w, board_h))

        # locked blocks (read color from tuple)
        for r in range(self.rows):
            row = self.grid[r]
            ry = by + r * self.cell_size
            for c in range(self.cols):
                val = row[c]
                if not val:
                    continue
                # val is (form, color_internal)
                if isinstance(val, tuple):
                    _, color_internal = val
                    rgb = _COLOR_RGB.get(color_internal, (200,200,200))
                else:
                    rgb = (200,200,200)
                rx = bx + c * self.cell_size
                pygame.draw.rect(screen, rgb, (rx+1, ry+1, self.cell_size-2, self.cell_size-2))
                pygame.draw.rect(screen, (20,20,20), (rx+1, ry+1, self.cell_size-2, self.cell_size-2), 1)

        # current piece
        if self.current:
            mat = self.current["matrix"]
            color_internal = self.current["color"]
            rgb = _COLOR_RGB.get(color_internal, (200,200,200))
            for r, row in enumerate(mat):
                for c, val in enumerate(row):
                    if not val:
                        continue
                    gx = self.current["x"] + c
                    gy = self.current["y"] + r
                    if gx < 0 or gx >= self.cols or gy >= self.rows or gy < 0:
                        continue
                    rx = bx + gx * self.cell_size
                    ry = by + gy * self.cell_size
                    pygame.draw.rect(screen, rgb, (rx+1, ry+1, self.cell_size-2, self.cell_size-2))
                    pygame.draw.rect(screen, (20,20,20), (rx+1, ry+1, self.cell_size-2, self.cell_size-2), 1)

        # grid lines
        for c in range(self.cols+1):
            x = bx + c * self.cell_size
            pygame.draw.line(screen, (30,30,30), (x, by), (x, by + board_h))
        for r in range(self.rows+1):
            y = by + r * self.cell_size
            pygame.draw.line(screen, (30,30,30), (bx, y), (bx + board_w, y))

    # -------------------------
    # utilities
    # -------------------------
    def reset(self):
        self.grid = [[0]*self.cols for _ in range(self.rows)]
        self.current = None
        self.fall_timer = 0.0
        self.move_timer = 0.0
        self.game_over = False
        self.full_grid = False
        self.last_cleared_color_counts = []
        if self.log_enabled:
            print("[TETRIS] reset called")

    def get_last_cleared(self):
        """Return and clear the last_cleared_color_counts list."""
        out = self.last_cleared_color_counts[:]
        self.last_cleared_color_counts = []
        return out

    # small runner for testing (manual spawn required)
    def run(self, fps=60):
        clock = pygame.time.Clock()
        while True:
            # host should set background externally
            self.draw()
            self.window.update()
            if self.game_over:
                # wait for 'r' to restart
                if self.window.get_keyboard().key_pressed('r'):
                    self.reset()
            else:
                self.update()
            clock.tick(fps)
