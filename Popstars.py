import os
import random
import sys
import math
import pygame

# 检查音效文件是否存在
if not os.path.exists("explode.mp3"):
    raise FileNotFoundError("explode.mp3 文件未找到，请确保文件存在且路径正确。")

pygame.mixer.init()
explode_sound = pygame.mixer.Sound("explode.mp3")
explode_sound.set_volume(0.5)  # 设置音量为 50%

class ExplodeSoundManager:
    def __init__(self):
        self.count = 0  # 剩余需要播放的爆炸音效数
        self.delay = 100  # 毫秒
        self.last_play_time = 0

    def trigger(self, count):
        self.count += count
        self.last_play_time = pygame.time.get_ticks() - self.delay  # 立刻开始播放

    def update(self):
        now = pygame.time.get_ticks()
        if self.count > 0 and now - self.last_play_time >= self.delay:
            explode_sound.play()
            self.count -= 1
            self.last_play_time = now

explode_manager = ExplodeSoundManager()

def play_explode_sound(count):
    explode_manager.trigger(count)

# 初始化 Pygame
pygame.init()
particles = []

def draw_star(surface, fill_color, border_color, center, radius):
    points = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        r = radius if i % 2 == 0 else radius * 0.4
        x = center[0] + math.cos(angle) * r
        y = center[1] + math.sin(angle) * r
        points.append((x, y))

    # 创建一个带alpha通道的Surface用于绘制阴影
    shadow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    shadow_points = [(x + 1.5, y + 1.5) for (x, y) in points]
    pygame.draw.polygon(shadow_surf, (0, 0, 0, 60), shadow_points)
    surface.blit(shadow_surf, (0, 0))

    pygame.draw.polygon(surface, border_color, points)
    pygame.draw.polygon(surface, fill_color, points, width=0)

# 爆炸粒子生成函数
def explode(x, y, color):
    new_particles = []
    for _ in range(20):  # 生成20个粒子
        new_particles.append(Particle(x, y, color))
    return new_particles

WIDTH, HEIGHT = 400, 500
ROWS, COLS = 10, 10
STAR_SIZE = 40
MARGIN = 5
TOP_MARGIN = 100
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("消灭星星 - 卡通版")
CLOCK = pygame.time.Clock()

BG_COLOR = (230, 245, 255)
TEXT_COLOR = (60, 60, 60)
STAR_COLORS = [
    ((255, 120, 120), (255, 60, 60)),
    ((120, 255, 120), (60, 200, 60)),
    ((120, 200, 255), (50, 150, 255)),
    ((255, 255, 150), (255, 220, 50)),
    ((220, 150, 255), (180, 100, 255))
]

font = pygame.font.SysFont("SimHei", 26)

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
        center_x = self.col * STAR_SIZE + STAR_SIZE // 2
        center_y = int(self.row) * STAR_SIZE + STAR_SIZE // 2 + TOP_MARGIN
        radius = int((STAR_SIZE - MARGIN * 2) // 2 * self.scale)

        box_size = STAR_SIZE - MARGIN
        box_left = self.col * STAR_SIZE + MARGIN
        box_top = int(self.row) * STAR_SIZE + TOP_MARGIN + MARGIN

        inner_color, outer_color = STAR_COLORS[self.color_index]
        box_color = tuple(min(255, c + 40) for c in inner_color)
        shadow_color = tuple(max(0, c - 50) for c in outer_color)
        highlight_color = tuple(min(255, c + 70) for c in box_color)

        shadow_rect = pygame.Rect(box_left + 2, box_top + 2, box_size, box_size)
        pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=10)
        highlight_rect = pygame.Rect(box_left, box_top, box_size, box_size)
        pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255, 30), highlight_rect, width=1, border_radius=10)
        main_rect = pygame.Rect(box_left + 1, box_top + 1, box_size - 2, box_size - 2)
        pygame.draw.rect(surface, box_color, main_rect, border_radius=10)

        draw_star(surface, inner_color, outer_color, (center_x, center_y), radius)

    def update(self):
        if self.removed and self.scale > 0:
            self.scale -= 0.1
            if self.scale < 0:
                self.scale = 0
        if self.falling:
            self.fall_speed = 2.0  # 超快速度
            # 判断是否会越过目标位置
            if self.row + self.fall_speed >= self.fall_target:
                self.row = self.fall_target
                self.falling = False
            else:
                self.row += self.fall_speed

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 4
        self.life = 30
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(2, 5)

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.life -= 1
        self.radius = max(0, int(self.radius - 0.13))

    def draw(self, surface):
        if self.radius > 0 and self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

def create_grid():
    return [[Star(r, c, random.randint(0, 4)) for c in range(COLS)] for r in range(ROWS)]

def has_removable(grid):
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c].removed:
                continue
            color_index = grid[r][c].color_index
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 检查上下左右
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    if not grid[nr][nc].removed and grid[nr][nc].color_index == color_index:
                        return True
    return False

def get_connected(grid, r, c, color_index, visited):
    if r < 0 or r >= ROWS or c < 0 or c >= COLS:
        return []
    if (r, c) in visited or grid[r][c].removed or grid[r][c].color_index != color_index:
        return []

    visited.add((r, c))
    connected = [(r, c)]
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        connected += get_connected(grid, r + dr, c + dc, color_index, visited)
    return connected

def explode_star(star, particles):
    if not star.removed:
        x = star.col * STAR_SIZE + STAR_SIZE // 2
        y = int(star.row) * STAR_SIZE + TOP_MARGIN + STAR_SIZE // 2
        particles.extend(explode(x, y, STAR_COLORS[star.color_index][0]))
        star.removed = True

def explode_all_stars(grid, particles):
    for row in grid:
        for star in row:
            explode_star(star, particles)

def explode_column(grid, col, particles):
    for r in range(ROWS):
        explode_star(grid[r][col], particles)

def remove_stars(grid, connected, particles):
    for r, c in connected:
        star = grid[r][c]
        explode_star(star, particles)

def collapse(grid):
    for c in range(COLS):
        non_removed = [grid[r][c] for r in range(ROWS) if not grid[r][c].removed]
        for i in range(ROWS - 1, -1, -1):
            if non_removed:
                star = non_removed.pop()
                target_row = i
                star.fall_target = float(target_row)
                star.falling = True
                distance = star.fall_target - star.row
                star.fall_speed = distance / 10.0 if distance > 0 else 0
                grid[i][c] = star
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
    exploding_cols = None  # 当前爆炸的列索引，None表示不爆炸
    exploding_timer = 0  # 计时器，用于列与列之间的延迟

    while True:
        CLOCK.tick(FPS)
        SCREEN.fill(BG_COLOR)
        draw_score(score)
        draw_reset_button()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if WIDTH - 120 <= x <= WIDTH - 20 and 20 <= y <= 56:
                    grid = create_grid()
                    score = 0
                    particles.clear()
                    removing = False
                    remove_timer = 0
                    exploding_cols = None
                    exploding_timer = 0
                    continue

                c = x // STAR_SIZE
                r = (y - TOP_MARGIN) // STAR_SIZE
                if 0 <= r < ROWS and 0 <= c < COLS:
                    star = grid[r][c]
                    if not star.removed:
                        connected = get_connected(grid, r, c, star.color_index, set())
                        if len(connected) >= 2:
                            remove_stars(grid, connected, particles)
                            score += len(connected) ** 2
                            removing = True
                            remove_timer = 10
                            play_explode_sound(len(connected))  # 触发音效

        # 更新爆炸管理器
        explode_manager.update()

        if removing:
            remove_timer -= 1
            if remove_timer <= 0:
                collapse(grid)
                shift_left(grid)
                removing = False

        # 更新星星
        for row in grid:
            for star in row:
                star.update()
                star.draw(SCREEN)

        # 更新粒子
        to_remove = []
        for p in particles:
            p.update()
            p.draw(SCREEN)
            if p.life <= 0 or p.radius <= 0:
                to_remove.append(p)
        for p in to_remove:
            particles.remove(p)

        # 爆炸列动画逻辑
        if not removing and not has_removable(grid) and len(particles) == 0:
            if exploding_cols is None:
                exploding_cols = COLS - 1
                exploding_timer = 0

        if exploding_cols is not None:
            exploding_timer += 1
            if exploding_timer >= 20:
                explode_column(grid, exploding_cols, particles)
                exploding_cols -= 1
                exploding_timer = 0
                if exploding_cols < 0:
                    collapse(grid)
                    shift_left(grid)
                    exploding_cols = None
                    removing = False

        pygame.display.flip()

if __name__ == "__main__":
    main()
