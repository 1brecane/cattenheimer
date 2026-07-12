import os

import pygame

from core.settings import GRAVITY, TILE_SIZE
from world.collision import check_terrain_collision


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, timer, grenade_type, expl_type, speed, bounce, impact, damage, game):
        super().__init__()
        self.game = game
        self.tmx_data = game.tmx_data
        self.timer = timer
        self.damage = damage
        self.vel_y = -10
        self.speed = speed
        self.image = grenade_type
        self.expl_type = expl_type
        self.impact = impact
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.bounce = bounce
        self.bounce_factor = -0.5

    def check_collision(self):
        return check_terrain_collision(self.rect, self.tmx_data, self.game.terrain_layer_index)

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        self.rect.y += dy
        collision_rect = self.check_collision()
        if collision_rect:
            if dy > 0:
                self.rect.bottom = collision_rect.top
                dy = collision_rect.top - self.rect.bottom + 0.01
                if self.impact:
                    self.explosion_function()
                if self.bounce:
                    self.vel_y *= self.bounce_factor
                    self.speed -= 1
                else:
                    self.speed = 0
                if self.speed <= 0:
                    self.speed = 0
            elif dy < 0:
                self.rect.top = collision_rect.bottom
                self.vel_y = 0
                if self.impact:
                    self.explosion_function()
                if self.bounce:
                    self.vel_y *= self.bounce_factor
                    self.speed -= 1
                else:
                    self.speed = 0
                if self.speed <= 0:
                    self.speed = 0

        self.rect.x += dx
        collision_rect = self.check_collision()
        if collision_rect:
            if dx > 0:
                self.rect.right = collision_rect.left
                if self.impact:
                    self.explosion_function()
                if self.bounce:
                    self.direction *= -1
                else:
                    self.speed = 0
            elif dx < 0:
                self.rect.left = collision_rect.right
                if self.impact:
                    self.explosion_function()
                if self.bounce:
                    self.direction *= -1
                else:
                    self.speed = 0

        if self.impact:
            for enemy in self.game.enemy_group:
                if enemy.alive:
                    if pygame.sprite.spritecollide(enemy, self.game.grenade_group, False):
                        self.explosion_function()
                    else:
                        self.timer -= 1
                        if self.timer <= 0:
                            self.explosion_function()
        else:
            self.timer -= 1
            if self.timer <= 0:
                self.explosion_function()

    def explosion_function(self):
        self.game.sounds["explosion"].play()
        explosion = Explosion(self.rect.centerx, self.rect.bottom, 1.5, self.expl_type, self.damage)
        self.kill()
        self.game.explosion_group.add(explosion)
        self.game.all_sprites.add(explosion)

        player = self.game.player
        if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
            player.health -= self.damage
            self.game.sounds["hurt"].play()

        for enemy in self.game.enemy_group:
            if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                enemy.health -= self.damage
                self.game.sounds["hurt"].play()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, expl_type, damage):
        super().__init__()
        self.images = []
        self.num_of_frames = len(os.listdir(f"Assets/Sprites/Explosions/Pack/explosion-1-{expl_type}"))
        for num in range(self.num_of_frames):
            img = pygame.image.load(
                f"Assets/Sprites/Explosions/Pack/explosion-1-{expl_type}/{num}.png"
            ).convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y + 3
        self.counter = 0
        self.damage = damage

    def update(self):
        EXPLOSION_SPEED = 10
        self.counter += 1
        self.image = self.images[self.frame_index]
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
        if self.frame_index >= self.num_of_frames:
            self.kill()
        else:
            self.image = self.images[self.frame_index]
