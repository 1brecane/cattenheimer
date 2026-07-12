import pygame

from core.settings import TILE_SIZE, BLACK, RED, GREEN, YELLOW
from entities.weapons import GRENADE_TYPES

GRENADE_ITEMS = {
    "Classic grenade": "classic",
    "Atom grenade": "atom",
    "Impact grenade": "impact",
}


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
        if not pygame.sprite.collide_rect(self, player):
            return
        if self.item_type == "Health":
            player.health = min(player.health + 25, player.max_health)
            self.game.sounds["heal"].play()
        else:
            key = GRENADE_ITEMS[self.item_type]
            cfg = GRENADE_TYPES[key]
            setattr(player, cfg["ammo_attr"], getattr(player, cfg["ammo_attr"]) + cfg["pickup_amount"])
            # if the selected type is empty, switch to the one just picked up
            selected = GRENADE_TYPES[self.game.selected_grenade]
            if getattr(player, selected["ammo_attr"]) == 0:
                self.game.selected_grenade = key
            self.game.sounds["action"].play()
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


class StaminaBar:
    def __init__(self, x, y, max_stamina):
        self.x = x
        self.y = y
        self.max_stamina = max_stamina

    def draw(self, stamina, exhausted, surface):
        ratio = stamina / self.max_stamina
        pygame.draw.rect(surface, BLACK, (self.x - 2, self.y - 2, 204, 12))
        pygame.draw.rect(surface, (60, 60, 60), (self.x, self.y, 200, 8))
        color = RED if exhausted else YELLOW
        pygame.draw.rect(surface, color, (self.x, self.y, 200 * ratio, 8))
