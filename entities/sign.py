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
        text_pos = self.game.camera.apply(self).topleft
        lines = self.text.split(", ")
        x_offset = 50
        y_offset = -100
        for i, line in enumerate(lines):
            draw_text(
                line,
                self.game.fonts["small"],
                WHITE,
                text_pos[0] + x_offset,
                text_pos[1] + y_offset + (i * 20),
                self.game.window,
            )
