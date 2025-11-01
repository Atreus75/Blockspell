# tetris_pplay.py
import random
import pygame
from PPlay.window import Window

class Tetris:
    # Tetromino shapes (1 = filled cell)
    SHAPES = [
        [[1,1,1,1]],                 # I
        [[1,0,0],[1,1,1]],           # J
        [[0,0,1],[1,1,1]],           # L
        [[1,1],[1,1]],               # O
        [[0,1,1],[1,1,0]],           # S
        [[0,1,0],[1,1,1]],           # T
        [[1,1,0],[0,1,1]]            # Z
    ]

    COLORS = {
        1: (232, 31, 16),   # Red
        2: (43, 227, 36),   # Green 
        3: (45, 42, 245),   # Blue
        4: (245, 238, 42),  # Yellow
        5: (232, 31, 16),   # Red
        6: (43, 227, 36),   # Green 
        7: (45, 42, 245),   # Blue
        8: (245, 238, 42)   # Yellow
    }

    def __init__(self, window: Window, cols=10, rows=20, cell_size=28, top_left=(40,40)):
        self.last_cleared_color_counts = []
        self.window = window
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.top_left = top_left

        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        self.current = None
        self.next_piece_id = self._rand_piece_id()

        self.fall_interval = 0.8
        self.fall_timer = 0.0

        self.move_cooldown = 0.12
        self.move_timer = 0.0

        self.game_over = False
        
        self.full_grid = False

        self.screen = self.window.get_screen()
        self.keyboard = self.window.get_keyboard()

        self.space_was_pressed = False

    # ---------- Helpers ----------
    def _count_line_color_distribution_dict(self, row_index):
        """
        Conta por ID na linha `row_index` e retorna dicionário:
        { "red": n, "green": n, "blue": n, "yellow": n }
        Compatível com duas possibilidades de mapeamento:
        - se self.COLORS tem 4 entradas (1..4) -> map 1->red,2->green,3->blue,4->yellow
        - se self.COLORS tem >=8 entries (repetições) -> map 1&5->red, 2&6->green, 3&7->blue, 4&8->yellow
        """
        # conta por id (1-based)
        max_id = max((cell for cell in self.grid[row_index]), default=0)
        # make sure we have at least list of zeros for indices
        # build simple id counts
        id_counts = {}
        for val in self.grid[row_index]:
            if val and val > 0:
                id_counts[val] = id_counts.get(val, 0) + 1

        # aggregate into semantic buckets
        red = green = blue = yellow = 0

        # If COLORS length >= 8 we assume repetition pattern 1->red,2->green,3->blue,4->yellow,5->red...
        if len(self.COLORS) >= 8:
            for id_key, cnt in id_counts.items():
                mod = (id_key - 1) % 4  # 0..3 -> red,green,blue,yellow
                if mod == 0:
                    red += cnt
                elif mod == 1:
                    green += cnt
                elif mod == 2:
                    blue += cnt
                elif mod == 3:
                    yellow += cnt
        else:
            # fallback: first four IDs map in order red,green,blue,yellow
            for id_key, cnt in id_counts.items():
                if id_key == 1:
                    red += cnt
                elif id_key == 2:
                    green += cnt
                elif id_key == 3:
                    blue += cnt
                elif id_key == 4:
                    yellow += cnt
                else:
                    # any unexpected id -> fold into closest (safe fallback)
                    fold = (id_key - 1) % 4
                    if fold == 0: red += cnt
                    elif fold == 1: green += cnt
                    elif fold == 2: blue += cnt
                    elif fold == 3: yellow += cnt

        return {"red": red, "green": green, "blue": blue, "yellow": yellow}
    
    
    def _count_line_color_distribution(self, row_index):
        """
            Retorna uma lista de contagens por cor para a linha `row_index` da grid.
            A lista tem tamanho = len(self.COLORS). índice 0 corresponde à cor id=1.
        """
        counts = [0] * len(self.COLORS)
        row = self.grid[row_index]
        for val in row:
            if val != 0:
                idx = val - 1
                if 0 <= idx < len(counts):
                    counts[idx] += 1
        return counts
 


    def _rand_piece_id(self):
        return random.randint(1, len(self.SHAPES))

    def _shape_matrix(self, pid):
        return [row[:] for row in self.SHAPES[pid-1]]

    def _rotate_cw(self, mat):
        return [list(row) for row in zip(*mat[::-1])]

    def _can_place(self, mat, x, y):
        for r, row in enumerate(mat):
            for c, val in enumerate(row):
                if not val:
                    continue
                gx = x + c
                gy = y + r
                if gx < 0 or gx >= self.cols or gy >= self.rows:
                    return False
                if gy >= 0 and self.grid[gy][gx] != 0:
                    return False
        return True

    def spawn_piece(self):
        pid = self.next_piece_id
        self.next_piece_id = self._rand_piece_id()
        mat = self._shape_matrix(pid)
        x = (self.cols - len(mat[0])) // 2
        # Mudança: spawn a partir do topo visível (linha 0). Não mais acima do grid.
        y = 0
        self.current = {"matrix": mat, "x": x, "y": y, "id": pid}

        # Atualiza full_grid com base no estado atual da grade:
        any_full_row = any(all(cell != 0 for cell in row) for row in self.grid)
        top_occupied = any(self.grid[0][c] != 0 for c in range(self.cols))
        self.full_grid = any_full_row or top_occupied

        # Game over se não puder colocar no topo OU se topo já ocupado (full_grid indica isso).
        if not self._can_place(mat, x, y) or top_occupied:
            self.game_over = True

    def _lock_piece(self):
        mat = self.current["matrix"]
        x = self.current["x"]
        y = self.current["y"]
        pid = self.current["id"]

        # escreve bloco na grade
        for r, row in enumerate(mat):
            for c, val in enumerate(row):
                if not val:
                    continue
                gx = x + c
                gy = y + r
                if 0 <= gy < self.rows and 0 <= gx < self.cols:
                    self.grid[gy][gx] = pid

        # Antes de limpar, detecta se alguma fileira estava totalmente ocupada
        any_full_row = any(all(cell != 0 for cell in row) for row in self.grid)
        top_occupied = any(self.grid[0][c] != 0 for c in range(self.cols))
        self.full_grid = any_full_row or top_occupied

        # Limpa linhas completas e recupera as contagens por cor
        cleared_info = self._clear_lines()  # retorna lista de contagens por linha

        # Remove referência à peça atual e tenta spawnar próxima (se não game over)
        self.current = None

        # armazenamos também aqui para fácil acesso imediato
        self.last_cleared_color_counts = cleared_info

        if not self.game_over:
            self.spawn_piece()

        # opcional: retornar as contagens para quem chamou (útil em integrações)
        return cleared_info

    def _clear_lines(self):
        """
        Remove linhas completas. Retorna lista de dicionários:
        [ {"red":..,"green":..,"blue":..,"yellow":..}, ... ]
        E preenche self.last_cleared_color_counts com essa lista.
        """
        cleared_info = []
        new_grid = []
        for row_idx, row in enumerate(self.grid):
            if all(cell != 0 for cell in row):
                # conta por cor semanticamente antes de remover
                counts_dict = self._count_line_color_distribution_dict(row_idx)
                cleared_info.append(counts_dict)
                # não adiciona a row -> efetivamente remove
            else:
                new_grid.append(row)

        # adiciona linhas vazias no topo pelo número de removidas
        for _ in range(len(cleared_info)):
            new_grid.insert(0, [0] * self.cols)

        if cleared_info:
            self.grid = new_grid

        # atualiza full_grid pós clear
        any_full_row = any(all(cell != 0 for cell in row) for row in self.grid)
        top_occupied = any(self.grid[0][c] != 0 for c in range(self.cols))
        self.full_grid = any_full_row or top_occupied

        # guarda resultado
        self.last_cleared_color_counts = cleared_info
        return cleared_info

    # ---------- API ----------
    def reset(self):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.current = None
        self.next_piece_id = self._rand_piece_id()
        self.fall_timer = 0.0
        self.move_timer = 0.0
        self.game_over = False
        self.full_grid = False
        self.spawn_piece()

    def handle_input(self, dt):
        self.move_timer += dt
        kb = self.keyboard
        if kb.key_pressed("left") and self.move_timer >= self.move_cooldown:
            if self.current and self._can_place(self.current["matrix"], self.current["x"] - 1, self.current["y"]):
                self.current["x"] -= 1
            self.move_timer = 0.0
        if kb.key_pressed("right") and self.move_timer >= self.move_cooldown:
            if self.current and self._can_place(self.current["matrix"], self.current["x"] + 1, self.current["y"]):
                self.current["x"] += 1
            self.move_timer = 0.0

        if kb.key_pressed("up") and self.move_timer >= self.move_cooldown:
            if self.current:
                newm = self._rotate_cw(self.current["matrix"])
                kicks = [0, -1, 1, -2, 2]
                for k in kicks:
                    if self._can_place(newm, self.current["x"] + k, self.current["y"]):
                        self.current["matrix"] = newm
                        self.current["x"] += k
                        break
            self.move_timer = 0.0

        # hard drop
        if kb.key_pressed("space") and not self.space_was_pressed:
            if self.current:
                while self._can_place(self.current["matrix"], self.current["x"], self.current["y"] + 1):
                    self.current["y"] += 1
                self._lock_piece()
            self.space_was_pressed = True
        elif not kb.key_pressed("space"):
            self.space_was_pressed = False

    def update(self):
        if self.game_over:
            return

        dt = self.window.delta_time()
        self.handle_input(dt)

        kb = self.keyboard
        if kb.key_pressed("down"):
            fall_speed = 0.03
        else:
            fall_speed = self.fall_interval

        self.fall_timer += dt
        if self.fall_timer >= fall_speed:
            self.fall_timer = 0.0
            if self.current is None:
                self.spawn_piece()
            else:
                if self._can_place(self.current["matrix"], self.current["x"], self.current["y"] + 1):
                    self.current["y"] += 1
                else:
                    self._lock_piece()

    def draw(self):
        screen = self.screen
        bx, by = self.top_left
        board_w = self.cols * self.cell_size
        board_h = self.rows * self.cell_size

        pygame.draw.rect(screen, (40, 40, 40), (bx-4, by-4, board_w+8, board_h+8))
        pygame.draw.rect(screen, (10, 10, 10), (bx, by, board_w, board_h))

        # static blocks
        for r in range(self.rows):
            for c in range(self.cols):
                val = self.grid[r][c]
                if val != 0:
                    color = self.COLORS.get(val, (200,200,200))
                    rx = bx + c * self.cell_size
                    ry = by + r * self.cell_size
                    pygame.draw.rect(screen, color, (rx+1, ry+1, self.cell_size-2, self.cell_size-2))
                    pygame.draw.rect(screen, (20,20,20), (rx+1, ry+1, self.cell_size-2, self.cell_size-2), 2)

        # active piece (não desenha fora do grid)
        if self.current:
            mat = self.current["matrix"]
            pid = self.current["id"]
            color = self.COLORS.get(pid, (200,200,200))
            for r, row in enumerate(mat):
                for c, val in enumerate(row):
                    if not val:
                        continue
                    gx = self.current["x"] + c
                    gy = self.current["y"] + r
                    # se fora horizontalmente ou abaixo do grid, pula
                    if gx < 0 or gx >= self.cols or gy >= self.rows:
                        continue
                    # se acima do topo (gy < 0) o pedido foi que NÃO se desenhe fora do grid
                    if gy < 0:
                        continue
                    rx = bx + gx * self.cell_size
                    ry = by + gy * self.cell_size
                    pygame.draw.rect(screen, color, (rx+1, ry+1, self.cell_size-2, self.cell_size-2))
                    pygame.draw.rect(screen, (20,20,20), (rx+1, ry+1, self.cell_size-2, self.cell_size-2), 2)

        for c in range(self.cols+1):
            x = bx + c * self.cell_size
            pygame.draw.line(screen, (30,30,30), (x, by), (x, by + board_h))
        for r in range(self.rows+1):
            y = by + r * self.cell_size
            pygame.draw.line(screen, (30,30,30), (bx, y), (bx + board_w, y))

        if self.game_over:
            self.window.draw_text("GAME OVER", bx + 10, by + board_h//2 - 20, size=28, color=(255,255,255))
            self.window.draw_text("R to restart", bx + 10, by + board_h//2 + 12, size=16, color=(200,200,200))

        # mostro o estado do atributo full_grid pra você debugar (opcional)
        # Você pode remover essa linha depois.
        self.window.draw_text(f"full_grid: {self.full_grid}", bx, by - 20, size=14, color=(200,200,200))
        self.window.draw_text("← → move   ↑ rotate   ↓ soft   SPACE hard", bx, by + board_h + 8, size=14, color=(200,200,200))

    def run(self, fps=60):
        clock = pygame.time.Clock()
        if self.current is None:
            self.spawn_piece()
        while True:
            self.window.set_background_color((50,50,50))
            self.draw()
            self.window.update()

            # restart on 'r'
            if self.game_over:
                events = pygame.event.get()
                while True:
                    if self.window.get_keyboard().key_pressed('r'):
                        break
            else:
                self.update()
            clock.tick(fps)

if __name__ == "__main__":
    w = Window(360, 720)
    w.set_title("Tetris - PPlay Minigame (com full_grid)")
    t = Tetris(w, cols=10, rows=20, cell_size=28, top_left=(40,40))
    t.reset()
    t.run()
