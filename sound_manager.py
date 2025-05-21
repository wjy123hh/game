import os
os.environ["SDL_AUDIODRIVER"] = "directsound"
import pygame


pygame.mixer.init()

explode_sound = pygame.mixer.Sound("explode.mp3")

class ExplodeSoundManager:
    def __init__(self):
        self.count = 0  # 剩余需要播放的爆炸音效数
        self.timer = 0
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
