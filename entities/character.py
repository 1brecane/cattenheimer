import os
import random

import pygame

from core.settings import GRAVITY
from world.collision import check_terrain_collision, slope_surface_y


class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, health, sprinting_possibility, game):
        super().__init__()
        self.game = game
        self.tmx_data = game.tmx_data
        self.alive = True
        self.sprinting_possibility = sprinting_possibility
        self.char_type = char_type
        self.speed = speed
        self.classic_grenades = 0
        self.atom_grenades = 0
        self.impact_grenades = 0
        self.health = health
        self.max_health = self.health
        self.stamina = 100
        self.max_stamina = 100
        self.exhausted = False
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
        self.vision = pygame.Rect(0, 0, 200, 20)
        self.hurt_cooldown = 0
        self.contact_damage = 10
        self.knockback = 0.0
        # i nemici non salgono i gradini automaticamente: restano nella loro zona
        self.steps_up = True
        # se impostato, il frame è scelto dalla fisica (salto/caduta)
        # invece che dal timer dell'animazione
        self.manual_frame = None
        self.landing_timer = 0
        # stato AI (solo nemici)
        self.chase_mult = 1.2
        self.speed_mult = 1.0
        self.idle_timer = 0
        self.patrol_dist = 0

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
        if self.hurt_cooldown > 0:
            self.hurt_cooldown -= 1

    def hit(self, damage, source_x=None):
        """Applica danno con frame di invulnerabilità, knockback e suono."""
        if self.hurt_cooldown > 0 or not self.alive:
            return
        self.health -= damage
        self.hurt_cooldown = 45
        if source_x is not None:
            # spinta via dalla sorgente del danno, con piccolo balzo
            self.knockback = 6.0 if self.rect.centerx >= source_x else -6.0
            self.vel_y = -4
            self.in_air = True
        self.game.sounds["hurt"].play()

    def check_collision(self):
        return check_terrain_collision(
            self.rect, self.tmx_data, self.game.terrain_layer_index, self.game.terrain_hitboxes
        )

    def can_sprint(self):
        return self.sprinting_possibility and not self.exhausted and self.stamina > 0

    def move(self, moving_left, moving_right, sprinting=False):
        dx = 0
        dy = 0
        sprint_active = sprinting and self.can_sprint() and (moving_left or moving_right)

        base_speed = self.speed * self.speed_mult
        if moving_left:
            dx = -base_speed * 2 if sprint_active else -base_speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = base_speed * 2 if sprint_active else base_speed
            self.flip = False
            self.direction = 1

        # spinta da knockback, si smorza da sola
        if abs(self.knockback) > 0.5:
            dx += self.knockback
        self.knockback *= 0.85

        # stamina: si consuma correndo e saltando, si rigenera altrimenti;
        # a zero lo sprint resta bloccato finché non si ricarica un po'
        if sprint_active:
            self.stamina -= 0.4
            if self.stamina <= 0:
                self.stamina = 0
                self.exhausted = True
        else:
            self.stamina = min(self.stamina + 0.4, self.max_stamina)
            if self.exhausted and self.stamina >= 20:
                self.exhausted = False

        if self.jump and not self.in_air:
            self.game.sounds["jump"].play()
            JUMP_COST = 12
            if self.stamina >= JUMP_COST:
                self.stamina -= JUMP_COST
                self.vel_y = -10
            else:
                # senza stamina il salto riesce comunque, ma più debole
                self.stamina = 0
                self.vel_y = -7
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        self.rect.y += dy
        landed = False
        collision_rect = self.check_collision()
        if collision_rect:
            if dy > 0:
                self.rect.bottom = collision_rect.top
                self.vel_y = 0
                landed = True
            elif dy < 0:
                self.rect.top = collision_rect.bottom
                self.vel_y = 0

        self.rect.x += dx
        collision_rect = self.check_collision()
        if collision_rect:
            stepped = False
            if dx != 0 and not self.in_air and self.steps_up:
                stepped = self.try_step_up(collision_rect)
            if not stepped:
                if dx > 0:
                    self.rect.right = collision_rect.left
                elif dx < 0:
                    self.rect.left = collision_rect.right

        # pendii: i piedi seguono il profilo del terreno
        if self.vel_y >= 0:
            surf = self.slope_surface()
            if surf is not None:
                sink = self.rect.bottom - surf
                if 0 <= sink <= self.tmx_data.tileheight * 2 or \
                        (not self.in_air and -16 <= sink < 0):
                    self.rect.bottom = surf
                    self.vel_y = 0
                    landed = True

        # stato a terra: in salita si è sempre in aria, altrimenti sonda
        # 2px sotto i piedi (così camminare giù da un bordo attiva la caduta)
        if self.vel_y < 0:
            self.in_air = True
        elif landed:
            self.in_air = False
        else:
            self.in_air = not self.is_on_ground()

        # limiti orizzontali della mappa e morte per caduta nel vuoto
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.game.map_width)
        if self.rect.top > self.game.map_height:
            self.health = 0

    def slope_surface(self):
        return slope_surface_y(
            self.rect, self.tmx_data, self.game.terrain_layer_index, self.game.terrain_heightmaps
        )

    def is_on_ground(self):
        probe = self.rect.move(0, 2)
        if check_terrain_collision(
            probe, self.tmx_data, self.game.terrain_layer_index, self.game.terrain_hitboxes
        ):
            return True
        surf = self.slope_surface()
        return surf is not None and abs(surf - self.rect.bottom) <= 2

    def try_step_up(self, collision_rect):
        """Sale automaticamente gradini alti al massimo un tile, se c'è spazio sopra."""
        step_height = self.rect.bottom - collision_rect.top
        if not 0 < step_height <= self.tmx_data.tileheight * 2:
            return False
        old_y = self.rect.y
        self.rect.bottom = collision_rect.top
        if self.check_collision():
            self.rect.y = old_y
            return False
        return True

    def cliff_ahead(self, direction):
        """True se un passo in quella direzione porta nel vuoto."""
        if self.in_air:
            return False
        front_x = self.rect.right + 6 if direction > 0 else self.rect.left - 6
        probe = pygame.Rect(front_x - 3, self.rect.bottom, 6, self.tmx_data.tileheight * 2)
        if check_terrain_collision(
            probe, self.tmx_data, self.game.terrain_layer_index, self.game.terrain_hitboxes
        ):
            return False
        shallow = pygame.Rect(front_x - 3, self.rect.bottom - 2, 6, 2)
        surf = slope_surface_y(
            shallow, self.tmx_data, self.game.terrain_layer_index,
            self.game.terrain_heightmaps, probe=self.tmx_data.tileheight * 2,
        )
        return surf is None

    def ai(self, player):
        if not (self.alive and player.alive):
            return

        # attacco a contatto
        if self.rect.colliderect(player.rect):
            player.hit(self.contact_damage, self.rect.centerx)
            self.update_action(3)
            self.idle_timer = 45
            return

        # il campo visivo segue sempre la direzione dello sguardo
        self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

        if self.vision.colliderect(player.rect):
            # inseguimento (i boss sono più rapidi), senza buttarsi nel vuoto
            self.idle_timer = 0
            self.speed_mult = self.chase_mult
            toward_right = self.rect.centerx < player.rect.centerx
            if self.cliff_ahead(1 if toward_right else -1):
                self.update_action(0)
            else:
                self.move(not toward_right, toward_right)
                self.update_action(1)
            return

        # pattugliamento
        self.speed_mult = 1.0
        if self.idle_timer > 0:
            self.idle_timer -= 1
            self.update_action(0)
            return
        if random.randint(1, 240) == 1:
            self.idle_timer = 90
            return

        if self.cliff_ahead(self.direction):
            self.direction *= -1
            self.patrol_dist = 0

        old_x = self.rect.x
        self.move(self.direction < 0, self.direction > 0)
        self.update_action(1)
        self.patrol_dist += abs(self.rect.x - old_x)
        if self.rect.x == old_x or self.patrol_dist > 160:
            # muro davanti o fine del giro di ronda: torna indietro
            self.direction *= -1
            self.patrol_dist = 0

    def update_animation(self):
        if self.manual_frame is not None:
            frames = self.animation_list[self.action]
            self.frame_index = min(self.manual_frame, len(frames) - 1)
            self.image = frames[self.frame_index]
            return
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
            self.manual_frame = None
            self.update_action(5)
