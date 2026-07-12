import pygame

from ui import button
from ui.button import TextButton
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, DIFFICULTIES, DIFFICULTY_ORDER
from core.assets import load_sounds, load_images, load_fonts
from world.camera import Camera
from world.collision import build_terrain_geometry
from world.renderer import draw_text, draw_parallax_bg, draw_map, load_map, build_map_surface
from entities.character import Character
from entities.items import ItemBox, HealthBar, StaminaBar
from entities.weapons import Grenade, GRENADE_TYPES, GRENADE_ORDER
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
        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth * 2
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight * 2

        # Pre-compute terrain layer index (avoids repeated lookup every frame)
        terrain_layer = self.tmx_data.get_layer_by_name("terrain")
        visible_layers = list(self.tmx_data.visible_layers)
        self.terrain_layer_index = visible_layers.index(terrain_layer)

        # geometria per-tile dai pixel visibili: i mezzi blocchi non
        # collidono come tile interi e i pendii hanno un profilo di altezze
        self.terrain_hitboxes, self.terrain_heightmaps, self.terrain_hitboxes_full = \
            build_terrain_geometry(self.tmx_data, self.terrain_layer_index)

        # Pre-render the whole map once: drawing becomes a single blit per frame
        self.map_surface = build_map_surface(self.tmx_data, 2)

        self.camera = Camera(self.map_width, self.map_height)

        self.start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2, self.images["start"], 3)
        self.exit_button = button.Button(SCREEN_WIDTH // 2 + 130, SCREEN_HEIGHT // 2, self.images["exit"], 3)
        self.reload_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2, self.images["reload"], 3)
        self.start_button.rect.center = (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30)
        self.exit_button.rect.center = (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 + 30)
        self.reload_button.rect.center = (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30)

        # impostazioni
        self.music_volume = 0.3
        self.sfx_volume = 0.5
        self.difficulty = "NORMALE"
        self.menu_state = "main"

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        menu_font = self.fonts["menu"]
        self.settings_button = TextButton((cx, cy + 120), "IMPOSTAZIONI", menu_font)
        self.music_minus = TextButton((cx - 170, cy - 50), "-", menu_font)
        self.music_plus = TextButton((cx + 170, cy - 50), "+", menu_font)
        self.sfx_minus = TextButton((cx - 170, cy + 10), "-", menu_font)
        self.sfx_plus = TextButton((cx + 170, cy + 10), "+", menu_font)
        self.difficulty_button = TextButton((cx, cy + 80), f"DIFFICOLTA': {self.difficulty}", menu_font)
        self.back_button = TextButton((cx, cy + 150), "INDIETRO", menu_font)

        # icone HUD ingrandite (le originali sono 13-16 px)
        self.hud_icons = {
            key: pygame.transform.scale2x(self.images[cfg["image"]])
            for key, cfg in GRENADE_TYPES.items()
        }

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
        self.selected_grenade = "classic"
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
        self.stamina_bar = StaminaBar(10, 31, self.player.max_stamina)

        diff = DIFFICULTIES[self.difficulty]
        enemy_data = [("Enemy1", 2000, 850, 100), ("Enemy2", 1300, 200, 200)]
        for char_type, x, y, base_health in enemy_data:
            enemy = Character(
                char_type, x, y, 3,
                2 * diff["speed_mult"],
                int(base_health * diff["health_mult"]),
                False, self,
            )
            enemy.contact_damage = diff["contact_damage"]
            self.enemy_group.add(enemy)
            self.all_sprites.add(enemy)

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
        self.sign_group.empty()
        self.setup_level()

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
                    self.sprinting = True
                if event.key == pygame.K_SPACE:
                    self.player.jump = True
                if event.key == pygame.K_f:
                    self.grenade = True
                    self.player.action_done = True
                if event.key == pygame.K_1:
                    self.selected_grenade = "classic"
                if event.key == pygame.K_2:
                    self.selected_grenade = "atom"
                if event.key == pygame.K_3:
                    self.selected_grenade = "impact"
                if event.key == pygame.K_ESCAPE:
                    if self.start_game:
                        # pausa: torna al menu principale
                        self.start_game = False
                        self.menu_state = "main"
                        self.moving_left = False
                        self.moving_right = False
                        self.sprinting = False
                    elif self.menu_state == "settings":
                        self.menu_state = "main"
                    else:
                        self.running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.moving_left = False
                if event.key == pygame.K_d:
                    self.moving_right = False
                if event.key == pygame.K_LSHIFT:
                    self.sprinting = False
                if event.key == pygame.K_SPACE:
                    self.player.jump = False
                if event.key == pygame.K_f:
                    self.grenade = False
                    self.grenade_thrown = False
                    self.player.action_done = False

            # rotella del mouse: scorre i tipi di granata
            if event.type == pygame.MOUSEWHEEL and self.start_game:
                idx = GRENADE_ORDER.index(self.selected_grenade)
                self.selected_grenade = GRENADE_ORDER[(idx - event.y) % len(GRENADE_ORDER)]

    # ------------------------------------------------------------------
    # Grenade logic
    # ------------------------------------------------------------------

    def handle_grenades(self):
        if not self.grenade or self.grenade_thrown:
            return
        cfg = GRENADE_TYPES[self.selected_grenade]
        ammo = getattr(self.player, cfg["ammo_attr"])
        if ammo <= 0:
            return
        g = Grenade(
            self.player.rect.centerx + (0.3 * self.player.rect.size[0] * self.player.direction),
            self.player.rect.centery + (0.3 * self.player.rect.size[1]),
            self.player.direction, cfg["timer"],
            self.images[cfg["image"]], cfg["expl_type"],
            cfg["speed"], cfg["bounce"], cfg["impact"], cfg["damage"], self,
        )
        self.grenade_group.add(g)
        self.all_sprites.add(g)
        setattr(self.player, cfg["ammo_attr"], ammo - 1)
        self.grenade_thrown = True

    # ------------------------------------------------------------------
    # Player animation state machine
    # ------------------------------------------------------------------

    def update_player_animation(self):
        player = self.player
        moving = self.moving_left or self.moving_right

        if player.in_air:
            # in aria il frame segue la velocità verticale:
            # slancio in salita, planata all'apice, caduta in discesa
            player.update_action(2)
            vel = player.vel_y
            if vel < -6:
                frame = 0 if moving else 1
            elif vel < -2:
                frame = 2
            elif vel < 2:
                frame = 3
            elif vel < 6:
                frame = 4
            else:
                frame = 5
            player.manual_frame = frame
            player.landing_timer = 12
            player.still_cooldown = 400
            return

        if player.landing_timer > 0 and not moving:
            # atterraggio: accucciata (6) e rialzata (7-9)
            player.update_action(2)
            player.landing_timer -= 1
            player.manual_frame = 6 + min((12 - player.landing_timer) // 3, 3)
            player.still_cooldown = 400
            return

        player.manual_frame = None
        player.landing_timer = 0
        if self.sprinting and moving and player.can_sprint():
            self.player.update_action(4)
            self.player.still_cooldown = 400
        elif moving:
            self.player.update_action(1)
            self.player.still_cooldown = 400
        elif self.grenade:
            self.player.update_action(3)
            self.player.still_cooldown = 400
        else:
            self.player.still_cooldown -= 1
            if self.player.still_cooldown >= 0:
                self.player.update_action(0)
            else:
                self.player.update_action(6)
                self.player.health += 0.01
                if self.player.health >= self.player.max_health:
                    self.player.health = self.player.max_health

    # ------------------------------------------------------------------
    # Menus
    # ------------------------------------------------------------------

    def apply_audio_settings(self):
        pygame.mixer.music.set_volume(self.music_volume)
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def _arm_menu_buttons(self):
        for b in (self.settings_button, self.music_minus, self.music_plus,
                  self.sfx_minus, self.sfx_plus, self.difficulty_button, self.back_button):
            b.arm()

    def draw_main_menu(self):
        draw_text(
            "CATTENHEIMER", self.fonts["big"], WHITE,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80, self.window, center=True,
        )
        if self.start_button.draw(self.window):
            self.sounds["action"].play()
            self.start_game = True
        if self.exit_button.draw(self.window):
            self.sounds["action"].play()
            self.running = False
        if self.settings_button.draw(self.window):
            self.sounds["action"].play()
            self.menu_state = "settings"
            self._arm_menu_buttons()

    def draw_settings_menu(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        draw_text("IMPOSTAZIONI", self.fonts["big"], WHITE, cx, cy - 160, self.window, center=True)

        draw_text(
            f"MUSICA: {round(self.music_volume * 100)}%",
            self.fonts["menu"], WHITE, cx, cy - 50, self.window, center=True,
        )
        draw_text(
            f"EFFETTI: {round(self.sfx_volume * 100)}%",
            self.fonts["menu"], WHITE, cx, cy + 10, self.window, center=True,
        )

        if self.music_minus.draw(self.window):
            self.music_volume = max(round(self.music_volume - 0.1, 1), 0.0)
            self.apply_audio_settings()
            self.sounds["action"].play()
        if self.music_plus.draw(self.window):
            self.music_volume = min(round(self.music_volume + 0.1, 1), 1.0)
            self.apply_audio_settings()
            self.sounds["action"].play()
        if self.sfx_minus.draw(self.window):
            self.sfx_volume = max(round(self.sfx_volume - 0.1, 1), 0.0)
            self.apply_audio_settings()
            self.sounds["action"].play()
        if self.sfx_plus.draw(self.window):
            self.sfx_volume = min(round(self.sfx_volume + 0.1, 1), 1.0)
            self.apply_audio_settings()
            self.sounds["action"].play()

        if self.difficulty_button.draw(self.window):
            idx = DIFFICULTY_ORDER.index(self.difficulty)
            self.difficulty = DIFFICULTY_ORDER[(idx + 1) % len(DIFFICULTY_ORDER)]
            self.difficulty_button.set_text(f"DIFFICOLTA': {self.difficulty}")
            self.restart_level()  # la nuova difficoltà riavvia il livello
            self.sounds["action"].play()

        if self.back_button.draw(self.window):
            self.sounds["action"].play()
            self.menu_state = "main"
            self._arm_menu_buttons()

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def draw_hud(self):
        self.health_bar.draw(self.player.health, self.window)
        self.stamina_bar.draw(self.player.stamina, self.player.exhausted, self.window)

        for i, key in enumerate(GRENADE_ORDER):
            cfg = GRENADE_TYPES[key]
            count = getattr(self.player, cfg["ammo_attr"])
            slot = pygame.Rect(10 + i * 48, 47, 44, 44)
            selected = key == self.selected_grenade

            bg = pygame.Surface(slot.size, pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150 if selected else 80))
            self.window.blit(bg, slot.topleft)
            if selected:
                pygame.draw.rect(self.window, WHITE, slot, 2)

            icon = self.hud_icons[key]
            if count == 0:
                icon.set_alpha(70)
            self.window.blit(icon, icon.get_rect(center=slot.center))
            icon.set_alpha(255)

            draw_text(str(i + 1), self.fonts["small"], WHITE, slot.x + 4, slot.y + 3, self.window)
            draw_text(str(count), self.fonts["small"], WHITE, slot.right - 12, slot.bottom - 15, self.window)

        cfg = GRENADE_TYPES[self.selected_grenade]
        draw_text(cfg["label"], self.fonts["small"], WHITE, 10, 96, self.window)

    def draw_sprites(self):
        for entity in self.all_sprites:
            # lampeggio durante i frame di invulnerabilità
            if getattr(entity, "hurt_cooldown", 0) > 0 and (entity.hurt_cooldown // 4) % 2:
                continue
            image = entity.image
            if hasattr(entity, "flip"):
                image = pygame.transform.flip(image, entity.flip, False)
            # ancora al centro-basso: i frame hanno dimensioni diverse tra loro
            draw_rect = image.get_rect(midbottom=entity.rect.midbottom)
            self.window.blit(image, draw_rect.move(self.camera.camera.topleft))

    # ------------------------------------------------------------------
    # Main game loop
    # ------------------------------------------------------------------

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            if not self.start_game:
                draw_parallax_bg(self.camera, self.images["bg_layers"], self.window)
                if self.menu_state == "settings":
                    self.draw_settings_menu()
                else:
                    self.draw_main_menu()
            else:
                self.camera.update(self.player)
                draw_parallax_bg(self.camera, self.images["bg_layers"], self.window)
                draw_map(self.map_surface, self.window, self.camera)
                self.draw_hud()

                for enemy in self.enemy_group:
                    enemy.ai(self.player)

                self.all_sprites.update()
                self.draw_sprites()

                for sign in self.sign_group:
                    sign.draw_text_overlay()

                if self.player.alive:
                    self.handle_grenades()
                    self.update_player_animation()
                    self.player.move(self.moving_left, self.moving_right, self.sprinting)

                    if not any(enemy.alive for enemy in self.enemy_group):
                        draw_text(
                            "VITTORIA", self.fonts["big"], WHITE,
                            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80, self.window, center=True,
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
                        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80, self.window, center=True,
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
