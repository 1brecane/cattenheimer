import pygame

from ui import button
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE
from core.assets import load_sounds, load_images, load_fonts
from world.camera import Camera
from world.renderer import draw_text, draw_parallax_bg, draw_map, load_map
from entities.character import Character
from entities.items import ItemBox, HealthBar
from entities.weapons import Grenade
from entities.sign import Sign


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.window.fill(WHITE)
        pygame.display.flip()
        self.clock = pygame.time.Clock()

        self.sounds = load_sounds()
        self.images = load_images()
        self.fonts = load_fonts()

        self.tmx_data = load_map("Data/tmx/tutorial.tmx")
        map_width = self.tmx_data.width * self.tmx_data.tilewidth * 2
        map_height = self.tmx_data.height * self.tmx_data.tileheight * 2

        # Pre-compute terrain layer index (avoids repeated lookup every frame)
        terrain_layer = self.tmx_data.get_layer_by_name("terrain")
        visible_layers = list(self.tmx_data.visible_layers)
        self.terrain_layer_index = visible_layers.index(terrain_layer)

        self.camera = Camera(map_width, map_height)

        self.start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2, self.images["start"], 3)
        self.exit_button = button.Button(SCREEN_WIDTH // 2 + 130, SCREEN_HEIGHT // 2, self.images["exit"], 3)
        self.reload_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2, self.images["reload"], 3)

        self.all_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.grenade_group = pygame.sprite.Group()
        self.explosion_group = pygame.sprite.Group()
        self.item_box_group = pygame.sprite.Group()
        self.sign_group = pygame.sprite.Group()

        self.moving_left = False
        self.moving_right = False
        self.grenade = False
        self.grenade_thrown = False
        self.classic_grenade_trow = True
        self.atom_grenade_trow = False
        self.impact_grenade_trow = False
        self.sprinting = False

        self.start_game = False
        self.running = True

        self.setup_level()

    # ------------------------------------------------------------------
    # Level setup / restart
    # ------------------------------------------------------------------

    def setup_level(self):
        item_data = [
            ("Health", 1850, 345),
            ("Atom grenade", 1750, 310),
            ("Classic grenade", 2800, 470),
            ("Classic grenade", 600, 200),
            ("Impact grenade", 2325, 1175),
            ("Impact grenade", 50, 725),
        ]
        for item_type, x, y in item_data:
            box = ItemBox(item_type, x, y, self)
            self.item_box_group.add(box)
            self.all_sprites.add(box)

        self.player = Character("Player", 500, 500, 3, 3, 100, True, self)
        self.all_sprites.add(self.player)
        self.health_bar = HealthBar(10, 10, self.player.health, self.player.health)

        self.enemy1 = Character("Enemy1", 2000, 850, 3, 2, 100, False, self)
        self.enemy2 = Character("Enemy2", 1300, 200, 3, 2, 200, False, self)
        self.enemy_group.add(self.enemy1, self.enemy2)
        self.all_sprites.add(self.enemy1, self.enemy2)

        sign1 = Sign(
            505, 880,
            "Benvenuto!, premi 'a' per andare a sinistra, 'd' per andare a destra e 'space bar' per saltare, "
            "puoi usare 'shift' mentre cammini per correre, procedi verso destra ed entra nella grotta!",
            self,
        )
        sign2 = Sign(
            2000, 1050,
            "Fai attenzione al nemico!, se ti avvicini ti farà danno, prendi le GRANATE AD IMPATTO quì sotto, "
            "premi il tato '3' per selezionarle e poi 'f' per usarle, (è macchinoso lo so ci sto lavorando)",
            self,
        )
        sign3 = Sign(
            2080, 450,
            "Molto bene!, esplora la mappa e cerca altre granate se vuoi, (Per selezionare le GRANATE CLASSICHE "
            "premi '1', per le GRANATE AD ATOMI premi '2', per le GRANATE AD IMPATTO premi '3'), quando sei pronto "
            "affronta il boss salendo nell'isola!",
            self,
        )
        self.sign_group.add(sign1, sign2, sign3)
        self.all_sprites.add(sign1, sign2, sign3)

    def restart_level(self):
        self.all_sprites.empty()
        self.enemy_group.empty()
        self.grenade_group.empty()
        self.explosion_group.empty()
        self.item_box_group.empty()

        item_data = [
            ("Health", 1850, 345),
            ("Atom grenade", 1750, 310),
            ("Classic grenade", 2800, 470),
            ("Impact grenade", 2325, 1175),
        ]
        for item_type, x, y in item_data:
            box = ItemBox(item_type, x, y, self)
            self.item_box_group.add(box)
            self.all_sprites.add(box)

        self.player = Character("Player", 500, 500, 3, 3, 100, True, self)
        self.all_sprites.add(self.player)
        self.health_bar = HealthBar(10, 10, self.player.health, self.player.health)

        self.enemy1 = Character("Enemy1", 2000, 850, 3, 2, 100, False, self)
        self.enemy2 = Character("Enemy2", 1300, 200, 3, 2, 200, False, self)
        self.enemy_group.add(self.enemy1, self.enemy2)
        self.all_sprites.add(self.enemy1, self.enemy2)

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.moving_left = True
                if event.key == pygame.K_d:
                    self.moving_right = True
                if event.key == pygame.K_LSHIFT:
                    if self.player.action == 0:
                        self.sprinting = False
                    else:
                        self.sprinting = True
                if event.key == pygame.K_SPACE:
                    self.player.rect.y -= 1
                    self.player.jump = True
                    if self.player.jump and not self.player.in_air:
                        self.player.jump_count += 1
                if event.key == pygame.K_f:
                    self.grenade = True
                    self.player.action_done = True
                if event.key == pygame.K_1:
                    self.atom_grenade_trow = False
                    self.impact_grenade_trow = False
                    self.classic_grenade_trow = True
                if event.key == pygame.K_2:
                    self.classic_grenade_trow = False
                    self.impact_grenade_trow = False
                    self.atom_grenade_trow = True
                if event.key == pygame.K_3:
                    self.classic_grenade_trow = False
                    self.impact_grenade_trow = True
                    self.atom_grenade_trow = False
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.moving_left = False
                    self.sprinting = False
                if event.key == pygame.K_d:
                    self.moving_right = False
                    self.sprinting = False
                if event.key == pygame.K_LSHIFT:
                    self.sprinting = False
                if event.key == pygame.K_SPACE:
                    self.player.jump = False
                if event.key == pygame.K_f:
                    self.grenade = False
                    self.grenade_thrown = False
                    self.player.action_done = False
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    # ------------------------------------------------------------------
    # Grenade logic
    # ------------------------------------------------------------------

    def handle_grenades(self):
        if self.classic_grenade_trow:
            if self.grenade and not self.grenade_thrown and self.player.classic_grenades > 0:
                g = Grenade(
                    self.player.rect.centerx + (0.3 * self.player.rect.size[0] * self.player.direction),
                    self.player.rect.centery + (0.3 * self.player.rect.size[1]),
                    self.player.direction, 150,
                    self.images["classic_grenade"], "d", 5, True, False, 50, self,
                )
                self.grenade_group.add(g)
                self.all_sprites.add(g)
                self.player.classic_grenades -= 1
                self.grenade_thrown = True

        if self.atom_grenade_trow:
            if self.grenade and not self.grenade_thrown and self.player.atom_grenades > 0:
                g = Grenade(
                    self.player.rect.centerx + (0.3 * self.player.rect.size[0] * self.player.direction),
                    self.player.rect.centery + (0.3 * self.player.rect.size[1]),
                    self.player.direction, 150,
                    self.images["atom_grenade"], "c", 4, True, False, 100, self,
                )
                self.grenade_group.add(g)
                self.all_sprites.add(g)
                self.player.atom_grenades -= 1
                self.grenade_thrown = True

        if self.impact_grenade_trow:
            if self.grenade and not self.grenade_thrown and self.player.impact_grenades > 0:
                g = Grenade(
                    self.player.rect.centerx + (0.3 * self.player.rect.size[0] * self.player.direction),
                    self.player.rect.centery + (0.3 * self.player.rect.size[1]),
                    self.player.direction, 150,
                    self.images["impact_grenade"], "a", 7, False, True, 25, self,
                )
                self.grenade_group.add(g)
                self.all_sprites.add(g)
                self.player.impact_grenades -= 1
                self.grenade_thrown = True

    # ------------------------------------------------------------------
    # Player animation state machine
    # ------------------------------------------------------------------

    def update_player_animation(self):
        if self.player.in_air:
            self.player.update_action(2)
            self.player.still_cooldown = 400
        elif self.sprinting:
            self.player.update_action(4)
            self.player.still_cooldown = 400
        elif self.moving_left or self.moving_right:
            self.player.update_action(1)
            self.player.still_cooldown = 400
            self.player.jump_count -= 0.1
            if self.player.jump_count <= 0:
                self.player.jump_count = 0
        elif self.grenade:
            self.player.update_action(3)
            self.player.still_cooldown = 400
        else:
            self.player.still_cooldown -= 1
            if self.player.still_cooldown >= 0:
                self.player.update_action(0)
                if self.player.still_cooldown == 380:
                    self.player.jump_count = 0
            else:
                self.player.update_action(6)
                self.player.health += 0.01
                if self.player.health >= self.player.max_health:
                    self.player.health = self.player.max_health

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def draw_hud(self):
        self.health_bar.draw(self.player.health, self.window)

        grenade_hud = [
            (self.player.classic_grenades, "GRANATE CLASSICHE: ", "classic_grenade", 190, 35, 32),
            (self.player.atom_grenades, "GRANATE AD ATOMI: ", "atom_grenade", 185, 55, 53),
            (self.player.impact_grenades, "GRANATE AD IMPATTO: ", "impact_grenade", 195, 75, 73),
        ]
        for count, label, img_key, icon_x, text_y, icon_y in grenade_hud:
            if count > 0:
                draw_text(label, self.fonts["small"], WHITE, 10, text_y, self.window)
                for i in range(count):
                    self.window.blit(self.images[img_key], (icon_x + (i * 10), icon_y))

    def draw_sprites(self):
        for entity in self.all_sprites:
            if hasattr(entity, "flip"):
                self.window.blit(
                    pygame.transform.flip(entity.image, entity.flip, False),
                    self.camera.apply(entity),
                )
            else:
                self.window.blit(entity.image, self.camera.apply(entity))

    # ------------------------------------------------------------------
    # Main game loop
    # ------------------------------------------------------------------

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            if not self.start_game:
                draw_parallax_bg(self.camera, self.images["bg_layers"], self.window)
                draw_text(
                    "CATTENHEIMER", self.fonts["big"], WHITE,
                    SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 - 100, self.window,
                )
                if self.start_button.draw(self.window):
                    self.sounds["action"].play()
                    self.start_game = True
                if self.exit_button.draw(self.window):
                    self.sounds["action"].play()
                    self.running = False
            else:
                self.camera.update(self.player)
                draw_parallax_bg(self.camera, self.images["bg_layers"], self.window)
                draw_map(self.tmx_data, self.window, 2, self.camera)
                self.draw_hud()

                self.all_sprites.update()
                self.draw_sprites()

                for enemy in self.enemy_group:
                    enemy.ai(self.player)
                    enemy.update()

                self.grenade_group.update()
                self.item_box_group.update()
                self.explosion_group.update()
                self.sign_group.update()

                if self.player.alive:
                    self.handle_grenades()
                    self.update_player_animation()
                    self.player.move(self.moving_left, self.moving_right, self.sprinting)

                    if self.enemy2.health <= 0 and self.enemy1.health <= 0:
                        draw_text(
                            "VITTORIA", self.fonts["big"], WHITE,
                            SCREEN_WIDTH // 2 - 135, SCREEN_HEIGHT // 2 - 100, self.window,
                        )
                        if self.reload_button.draw(self.window):
                            self.sounds["action"].play()
                            self.restart_level()
                        elif self.exit_button.draw(self.window):
                            self.sounds["action"].play()
                            self.running = False
                else:
                    draw_text(
                        "GAME OVER", self.fonts["big"], WHITE,
                        SCREEN_WIDTH // 2 - 135, SCREEN_HEIGHT // 2 - 100, self.window,
                    )
                    if self.reload_button.draw(self.window):
                        self.sounds["action"].play()
                        self.restart_level()
                    elif self.exit_button.draw(self.window):
                        self.sounds["action"].play()
                        self.running = False

            self.handle_events()
            pygame.display.update()

        pygame.quit()
