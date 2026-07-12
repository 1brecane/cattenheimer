import pygame

from core.settings import TILE_SIZE, WHITE
from world.renderer import draw_text


class Sign(pygame.sprite.Sprite):
    def __init__(self, x, y, text, game):
        super().__init__()
        self.game = game
        self.image = pygame.image.load("Assets/Sprites/Enemy2/Death/14.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        self.text = text
        self.player_nearby = False

    def update(self):
        self.player_nearby = pygame.sprite.collide_rect(self, self.game.player)

    def draw_text_overlay(self):
        if not self.player_nearby:
            return
        font = self.game.fonts["small"]
        lines = self.text.split(", ")
        line_height = 20
        text_width = max(font.size(line)[0] for line in lines)

        panel = pygame.Rect(0, 0, text_width + 20, len(lines) * line_height + 14)
        sign_pos = self.game.camera.apply(self)
        panel.midbottom = (sign_pos.centerx, sign_pos.top - 8)
        panel.clamp_ip(self.game.window.get_rect())

        overlay = pygame.Surface(panel.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.game.window.blit(overlay, panel.topleft)
        for i, line in enumerate(lines):
            draw_text(
                line, font, WHITE,
                panel.x + 10, panel.y + 8 + i * line_height,
                self.game.window,
            )
