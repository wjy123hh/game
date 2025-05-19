import pygame
import random
import sys

pygame.init()

# 画面设置
WIDTH, HEIGHT = 400, 500
ROWS, COLS = 10, 10
STAR_SIZE = 40
MARGIN = 5
TOP_MARGIN = 100
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("消灭星星 - 卡通版")
CLOCK = pygame.time.Clock()

# 风格颜色
BG_COLOR = (230, 245, 255)
TEXT_COLOR = (60, 60, 60)
STAR_COLORS = [
    ((255, 120, 120), (255, 60, 60)),
    ((120, 255, 120), (60, 200, 60)),
    ((120, 200, 255), (50, 150, 255)),
    ((255, 255, 150), (255, 220, 50)),
    ((220, 150, 255), (180, 100, 255))
]

# 字体
font = pygame.font.SysFont("Microsoft YaHei", 26)

# 星星类
class Star:
    def __init__(self, row, col, color_index):
        self.row = float(row)
        self.col = col
        self.color_index = color_index
        self.removed = False
        self.scale = 1.0
        self.falling = False
        self.fall_target = self.row
        self.fall_speed = 0

    def draw(self, surface):
        if self.removed:
            return
        x = self.col * STAR_SIZE + MARGIN
        y = int(self.row) * STAR_SIZE + TOP_MARGIN
        size = int(STAR_SIZE * self.scale)
        offset = (STAR_SIZE - size) // 2
        rect = pygame.Rect(x + offset, y + offset, size - MARGIN, size - MARGIN)

        # 渐变色填充
        inner_color, border_color = STAR_COLORS[self.color_index]
        pygame.draw.rect(surface, border_color, rect, border_radius=10)
        pygame.draw.rect(surface, inner_color, rect.inflate(-6, -6), border_radius=8)

    def update(self):
        if self.removed and self.scale > 0:
            self.scale -= 0.1
            if self.scale < 0:
                self.scale = 0
        if self.falling:
            self.row += self.fall_speed
            if abs(self.row - self.fall_target) < 0.1:
                self.row = self.fall_target
                self.falling = False

def create_grid():
    return [[Star(r, c, random.randint(0, 4)) for c in range(COLS)] for r in range(ROWS)]

def get_connected(grid, r, c, color_index, visited):
    if r < 0 or r >= ROWS or c < 0 or c >= COLS:
        return []
    if (r, c) in visited or grid[int(r)][c].removed or grid[int(r)][c].color_index != color_index:
        return []

    visited.add((r, c))
    connected = [(r, c)]
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        connected += get_connected(grid, r+dr, c+dc, color_index, visited)
    return connected

def remove_stars(grid, connected):
    for r, c in connected:
        grid[int(r)][c].removed = True

def collapse(grid):
    for c in range(COLS):
        non_removed = [grid[int(r)][c] for r in range(ROWS) if not grid[int(r)][c].removed]
        for i in range(ROWS - 1, -1, -1):
            if non_removed:
                star = non_removed.pop()
                target_row = i
                star.fall_target = float(target_row)
                star.falling = True
                star.fall_speed = (star.fall_target - star.row) / 10.0
                grid[i][c] = star
                star.col = c
            else:
                grid[i][c] = Star(float(i), c, random.randint(0, 4))
                grid[i][c].removed = True

def shift_left(grid):
    new_cols = []
    for c in range(COLS):
        if any(not grid[r][c].removed for r in range(ROWS)):
            new_cols.append([grid[r][c] for r in range(ROWS)])

    for c in range(COLS):
        for r in range(ROWS):
            if c < len(new_cols):
                star = new_cols[c][r]
                star.col = c
                grid[r][c] = star
            else:
                grid[r][c] = Star(float(r), c, random.randint(0, 4))
                grid[r][c].removed = True

def draw_score(score):
    score_text = font.render(f"得分：{score}", True, TEXT_COLOR)
    SCREEN.blit(score_text, (20, 20))

def draw_reset_button():
    pygame.draw.rect(SCREEN, (180, 220, 250), (WIDTH - 120, 20, 100, 36), border_radius=8)
    text = font.render("重新开始", True, TEXT_COLOR)
    SCREEN.blit(text, (WIDTH - 115, 22))

def main():
    grid = create_grid()
    score = 0
    removing = False
    remove_timer = 0

    while True:
        CLOCK.tick(FPS)
        SCREEN.fill(BG_COLOR)
        draw_score(score)
        draw_reset_button()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if WIDTH - 120 <= x <= WIDTH - 20 and 20 <= y <= 56:
                    grid = create_grid()
                    score = 0
                    continue

                c = x // STAR_SIZE
                r = (y - TOP_MARGIN) // STAR_SIZE
                if 0 <= r < ROWS and 0 <= c < COLS:
                    star = grid[r][c]
                    if not star.removed:
                        connected = get_connected(grid, r, c, star.color_index, set())
                        if len(connected) >= 2:
                            remove_stars(grid, connected)
                            score += len(connected) ** 2
                            removing = True
                            remove_timer = 10

        if removing:
            remove_timer -= 1
            if remove_timer <= 0:
                collapse(grid)
                shift_left(grid)
                removing = False

        for row in grid:
            for star in row:
                star.update()
                star.draw(SCREEN)

        pygame.display.flip()

if __name__ == "__main__":
    main()
