import pygame

from settings import TILE_SIZE, BLACK, RED, GREEN


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y, game):
        super().__init__()
        self.game = game
        self.item_type = item_type
        self.image = game.images["item_boxes"][self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        player = self.game.player
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == "Health":
                player.health += 25
                self.game.sounds["heal"].play()
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Classic grenade":
                player.classic_grenades += 5
            elif self.item_type == "Atom grenade":
                player.atom_grenades += 2
            elif self.item_type == "Impact grenade":
                player.impact_grenades += 10
            self.kill()


class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health, surface):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(surface, BLACK, (self.x - 2, self.y - 2, 204, 19))
        pygame.draw.rect(surface, RED, (self.x, self.y, 200, 15))
        pygame.draw.rect(surface, GREEN, (self.x, self.y, 200 * ratio, 15))
