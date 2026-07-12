import os
import random

import pygame

from core.settings import GRAVITY, TILE_SIZE
from world.collision import check_terrain_collision


class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, health, sprinting_possibility, game):
        super().__init__()
        self.game = game
        self.tmx_data = game.tmx_data
        self.alive = True
        self.action_done = False
        self.sprinting_possibility = sprinting_possibility
        self.char_type = char_type
        self.speed = speed
        self.classic_grenades = 0
        self.atom_grenades = 0
        self.impact_grenades = 0
        self.shoot_cooldown = 0
        self.start_grenades = 0
        self.health = health
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.still_cooldown = 400
        self.jump_count = 0
        self.move_count = 0
        self.vision = pygame.Rect(0, 0, 200, 20)
        self.idling = False
        self.idling_count = 0

        animation_types = ["Idle", "Walking", "Jumping", "Action", "Running", "Death", "Cleaning"]
        idle_frames = None
        for animation in animation_types:
            sprite_dir = f"Assets/Sprites/{self.char_type}/{animation}"
            if os.path.isdir(sprite_dir):
                temp_list = []
                num_of_frames = len(os.listdir(sprite_dir))
                for i in range(num_of_frames):
                    img = pygame.image.load(f"{sprite_dir}/{i}.png").convert_alpha()
                    img = pygame.transform.scale(
                        img, (int(img.get_width() * scale), int(img.get_height() * scale))
                    )
                    temp_list.append(img)
                if idle_frames is None:
                    idle_frames = temp_list
            else:
                temp_list = idle_frames
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def check_collision(self):
        return check_terrain_collision(self.rect, self.tmx_data, self.game.terrain_layer_index)

    def move(self, moving_left, moving_right, sprinting=False):
        dx = 0
        dy = 0

        if moving_left:
            if sprinting and self.sprinting_possibility:
                dx = -self.speed * 2
            else:
                dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            if sprinting and self.sprinting_possibility:
                dx = self.speed * 2
            else:
                dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump and not self.in_air:
            self.game.sounds["jump"].play()
            if self.jump_count <= 3:
                self.vel_y = -10
            else:
                self.vel_y = -10 + self.jump_count * 0.9
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        self.rect.y += dy
        collision_rect = self.check_collision()
        if collision_rect:
            if dy > 0:
                self.rect.bottom = collision_rect.top
                self.vel_y = 0
                self.in_air = False
            elif dy < 0:
                self.rect.top = collision_rect.bottom
                self.vel_y = 0

        self.rect.x += dx
        collision_rect = self.check_collision()
        if collision_rect:
            if dx > 0:
                self.rect.right = collision_rect.left
                if not self.in_air and self.can_step_up(collision_rect):
                    self.rect.y -= TILE_SIZE
            elif dx < 0:
                self.rect.left = collision_rect.right
                if not self.in_air and self.can_step_up(collision_rect):
                    self.rect.y -= TILE_SIZE

    def can_step_up(self, collision_rect):
        tile_w2 = self.tmx_data.tilewidth * 2
        tile_h2 = self.tmx_data.tileheight * 2
        x = collision_rect.left // tile_w2
        y = (collision_rect.top // tile_h2) - 1
        tile_above = self.tmx_data.get_tile_image(x, y, self.game.terrain_layer_index)
        return tile_above is None

    def ai(self, player):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_count = 150

            if self.rect.colliderect(player.rect):
                player.health -= 1
                self.game.sounds["hurt"].play()
                self.update_action(3)
                self.idling = True
                self.idling_count = 100

            if self.vision.colliderect(player.rect):
                self.idling = False
                if self.rect.centerx < player.rect.centerx:
                    ai_moving_right = True
                    ai_moving_left = False
                else:
                    ai_moving_right = False
                    ai_moving_left = True
                self.move(ai_moving_left, ai_moving_right)
                self.update_action(1)
                self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
            else:
                self.idling = True
                self.idling_count -= 1
                if self.idling_count <= 0:
                    self.idling = False
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_count += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_count > TILE_SIZE:
                        self.direction *= -1
                        self.move_count *= -1
                else:
                    self.idling_count -= 1
                    if self.idling_count == 0:
                        self.idling = False

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(5)

    def draw(self, surface):
        surface.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
