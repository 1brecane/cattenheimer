
import pygame, random, os, pytmx, button

pygame.init()

#Finestra di gioco
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
window.fill((255, 255, 255))
pygame.display.flip()

#frame rate 
clock = pygame.time.Clock()
FPS = 60

#definizione variabili di gioco
GRAVITY = 0.45
TILE_SIZE = 40
start_game = False

#variabili di azione giocatore
moving_left = False
moving_right = False
grenade = False
grenade_thrown = False
classic_grenade_trow = True
atom_grenade_trow = False
impact_grenade_trow = False
sprinting = False

#carica suoni
pygame.mixer.music.load("Assets/music/time_for_adventure.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound("Assets/sounds/jump.wav")
jump_fx.set_volume(0.5)
explosion_fx = pygame.mixer.Sound("Assets/sounds/explosion.wav")
explosion_fx.set_volume(0.5)
action_fx = pygame.mixer.Sound("Assets/sounds/tap.wav")
action_fx.set_volume(0.5)
hurt_fx = pygame.mixer.Sound("Assets/sounds/hurt.wav")
hurt_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound("Assets/sounds/power_up.wav")
heal_fx.set_volume(0.5)

#carica immagini
#immagini di sfondo
bg_layer1 = pygame.image.load("Assets/Clouds/Clouds 2/1.png").convert_alpha()
bg_layer1 = pygame.transform.scale(bg_layer1, (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_layer2 = pygame.image.load("Assets/Clouds/Clouds 2/2.png").convert_alpha()
bg_layer2 = pygame.transform.scale(bg_layer2, (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_layer3 = pygame.image.load("Assets/Clouds/Clouds 2/3.png").convert_alpha()
bg_layer3 = pygame.transform.scale(bg_layer3, (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_layer4 = pygame.image.load("Assets/Clouds/Clouds 2/4.png").convert_alpha()
bg_layer4 = pygame.transform.scale(bg_layer4, (SCREEN_WIDTH, SCREEN_HEIGHT))

#immagini bottone
start_img = pygame.image.load("Assets/Buttons/start.png").convert_alpha()
reload_img = pygame.image.load("Assets/Buttons/reload.png").convert_alpha()
exit_img = pygame.image.load("Assets/Buttons/exit.png").convert_alpha()

#granate (che si possono raccogliere)
classic_grenade = pygame.image.load("Assets/Items/classic_grenade.png").convert_alpha()
atom_grenade = pygame.image.load("Assets/Items/atom_grenade.png").convert_alpha()
impact_grenade = pygame.image.load("Assets/Items/impact_grenade.png").convert_alpha()

#pick up boxes , metto qui dentro le immagini (item) che si possono raccogliere
onigiri_img =  pygame.image.load("Assets/Items/onigiri_1.png").convert_alpha()
item_boxes = {
    "Health"    :onigiri_img,
    "Classic grenade"   :classic_grenade,
    "Atom grenade"  :atom_grenade,
    "Impact grenade"    :impact_grenade
}

#definizioni colori
RED = (229, 101, 46)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (102, 146, 61)

#definisci font
font = pygame.font.SysFont("Pixel Operator 8", 12)
font_big = pygame.font.SysFont("Pixel Operator 8", 36, True, True)

#funzioni utili per il gioco in generale
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    window.blit(img, (x, y))

def draw_parallax_bg(camera):
    # Calcola la posizione di ogni livello in base alla posizione della camera
    layer1_x = -camera.camera.x * 0.02
    layer2_x = -camera.camera.x * 0.05
    layer3_x = -camera.camera.x * 0.07
    layer4_x = -camera.camera.x * 0.1

    # Centra le immagini sul giocatore
    layer1_x = (layer1_x % SCREEN_WIDTH) - SCREEN_WIDTH
    layer2_x = (layer2_x % SCREEN_WIDTH) - SCREEN_WIDTH
    layer3_x = (layer3_x % SCREEN_WIDTH) - SCREEN_WIDTH
    layer4_x = (layer4_x % SCREEN_WIDTH) - SCREEN_WIDTH

    # Disegna ogni livello
    window.blit(bg_layer1, (layer1_x, 0))
    window.blit(bg_layer1, (layer1_x + SCREEN_WIDTH, 0))
    window.blit(bg_layer2, (layer2_x, 0))
    window.blit(bg_layer2, (layer2_x + SCREEN_WIDTH, 0))
    window.blit(bg_layer3, (layer3_x, 0))
    window.blit(bg_layer3, (layer3_x + SCREEN_WIDTH, 0))
    window.blit(bg_layer4, (layer4_x, 0))
    window.blit(bg_layer4, (layer4_x + SCREEN_WIDTH, 0))

def load_map(filename):
    tmx_data = pytmx.util_pygame.load_pygame(filename)
    return tmx_data

def draw_map(tmx_data, surface, scale, camera):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    # Calcola la posizione del tile
                    tile_x = x * tmx_data.tilewidth * scale + camera.camera.x 
                    tile_y = y * tmx_data.tileheight * scale + camera.camera.y 
                    # Disegna solo se il tile è visibile nella finestra di gioco
                    if -50 <= tile_x < SCREEN_WIDTH and -50 <= tile_y < SCREEN_HEIGHT:
                        scaled_tile = pygame.transform.scale(tile, (int(tile.get_width() * scale), int(tile.get_height() * scale)))
                        surface.blit(scaled_tile, (tile_x, tile_y))                

def restart_level():
    global player, health_bar, enemy1, enemy2, all_sprites, enemy_group, grenade_group, explosion_group, item_box_group

    # Reset gruppi sprite
    all_sprites.empty()
    enemy_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()

    # Area temporanea per creare item box
    item_box = ItemBox("Health", 1850, 345)
    item_box_group.add(item_box)
    all_sprites.add(item_box)
    item_box = ItemBox("Atom grenade", 1750, 310)
    item_box_group.add(item_box)
    all_sprites.add(item_box)
    item_box = ItemBox("Classic grenade", 2800, 470)
    item_box_group.add(item_box)
    all_sprites.add(item_box)
    item_box = ItemBox("Impact grenade", 2325, 1175)
    item_box_group.add(item_box)
    all_sprites.add(item_box)

    # Genera le varie entità
    player = Character("Player", 500, 500, 3, 3, 100, True, tmx_data)
    all_sprites.add(player)
    health_bar = HealthBar(10, 10, player.health, player.health)

    enemy1 = Character("Enemy1", 2000, 850, 3, 2, 100, False, tmx_data)
    enemy2 = Character("Enemy2", 1300, 200, 3, 2, 200, False, tmx_data)
    enemy_group.add(enemy1)
    all_sprites.add(enemy1)
    enemy_group.add(enemy2)
    all_sprites.add(enemy2)

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - SCREEN_WIDTH), x)  # right
        y = max(-(self.height - SCREEN_HEIGHT), y)  # bottom
    
        self.camera = pygame.Rect(x, y, self.width, self.height)


#Classi Character, Itembox, Healthbar, Grenade, Explosion
class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, health, sprinting_possibility, tmx_data):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.tmx_data = tmx_data
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
        self.update_time = 60
        self.still_cooldown = 400
        self.jump_count = 0
        #specifiche variabili di ia
        self.move_count = 0
        self.vision = pygame.Rect(0, 0, 200, 20)
        self.idling = False
        self.idling_count = 0

        animation_types = ["Idle", "Walking", "Jumping", "Action", "Running", "Death", "Cleaning"]

        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f"Assets/Sprites/{self.char_type}/{animation}"))
            for i in range(num_of_frames):
                img = pygame.image.load(f"Assets/Sprites/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale ), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list) 

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    #funzione generale per aggiornare funzione animazioni e controlla se vivo


    def update (self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def check_collision(self):
        terrain_layer = self.tmx_data.get_layer_by_name("terrain")
        visible_layers = list(self.tmx_data.visible_layers)
        terrain_layer_index = visible_layers.index(terrain_layer)
        # Calcola i limiti dell'entità
        left = self.rect.left // (self.tmx_data.tilewidth * 2)
        right = self.rect.right // (self.tmx_data.tilewidth * 2)
        top = self.rect.top // (self.tmx_data.tileheight * 2)
        bottom = self.rect.bottom // (self.tmx_data.tileheight * 2)
        
        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                tile = self.tmx_data.get_tile_image(x, y, terrain_layer_index)
                if tile:
                    terrain_rect = pygame.Rect(x * self.tmx_data.tilewidth * 2, y * self.tmx_data.tileheight * 2, self.tmx_data.tilewidth * 2, self.tmx_data.tileheight * 2)
                    if self.rect.colliderect(terrain_rect):
                        return terrain_rect
        return None

    
    def move(self, moving_left, moving_right):
        #reset variabili di movimento 
        dx = 0
        dy = 0

        #movimento: camminaare e sprint
        if moving_left == True:
            if sprinting == True and self.sprinting_possibility:
                dx = -self.speed * 2
            else:
                dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right == True:
            if sprinting == True and self.sprinting_possibility:
                dx = self.speed * 2
            else:
                dx = self.speed
            self.flip = False
            self.direction = 1

        #salto
        if self.jump == True and self.in_air == False:
            jump_fx.play()
            if self.jump_count <= 3 :
                self.vel_y = -10
            else:
                self.vel_y = -10 + self.jump_count * 0.9
            self.jump = False
            self.in_air = True
        #applico gravità al salto
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # controlla collisioni verticali
        self.rect.y += dy
        collision_rect = self.check_collision()
        if collision_rect:
            if dy > 0:  # Moving down
                self.rect.bottom = collision_rect.top
                self.vel_y = 0
                self.in_air = False
            elif dy < 0:  # Moving up
                self.rect.top = collision_rect.bottom
                self.vel_y = 0

         # controlla collisioni orizzontali
        self.rect.x += dx
        collision_rect = self.check_collision()
        if collision_rect:
            if dx > 0:  # Moving right
                self.rect.right = collision_rect.left
                if not self.in_air and self.can_step_up(collision_rect):
                    self.rect.y -= TILE_SIZE
            elif dx < 0:  # Moving left
                self.rect.left = collision_rect.right
                if not self.in_air and self.can_step_up(collision_rect):
                    self.rect.y -= TILE_SIZE

    def can_step_up(self, collision_rect):
        # Controlla se c'è un tile sopra il tile di collisione
        terrain_layer = self.tmx_data.get_layer_by_name("terrain")
        visible_layers = list(self.tmx_data.visible_layers)
        terrain_layer_index = visible_layers.index(terrain_layer)
        x = collision_rect.left // (self.tmx_data.tilewidth * 2)
        y = (collision_rect.top // (self.tmx_data.tileheight * 2)) - 1
        tile_above = self.tmx_data.get_tile_image(x, y, terrain_layer_index)
        return tile_above is None
        

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # idle
                self.idling = True
                self.idling_count = 150

            # se tocca il player li fa danno
            if self.rect.colliderect(player.rect):
                player.health -= 1
                hurt_fx.play()
                self.update_action(3)  # attacco
                self.idling = True
                self.idling_count = 100

            # controlla se l'ia è vicina al player
            if self.vision.colliderect(player.rect):
                # inseguire il giocatore
                self.idling = False
                if self.rect.centerx < player.rect.centerx:
                    ai_moving_right = True
                    ai_moving_left = False
                else:
                    ai_moving_right = False
                    ai_moving_left = True
                self.move(ai_moving_left, ai_moving_right)
                self.update_action(1)  # camminare
                self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
            else:
                self.idling = True
                self.idling_count -= 1
                if self.idling_count <= 0:
                    self.idling = False
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # camminare
                    self.move_count += 1
                    # aggiorna la posizione del rettangolo "vision" quando si muove
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_count > TILE_SIZE:
                        self.direction *= -1
                        self.move_count *= -1
                else:
                    self.idling_count -= 1
                    if self.idling_count == 0:
                        self.idling = False
      
    def update_animation(self):
        #aggiorna animazione
        ANIMATION_COOLDOWN = 100
        #aggiorna animazione dipendendo dal frame in cui è 
        self.image = self.animation_list[self.action][self.frame_index]
        #controlla se il tempo è passato prima della nuova animazione
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #se l'indice di frame raggiunge il limite di animazioni caricate torna a 0 
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1   
            #elif self.action_done == True:
                #self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
    
    def update_action(self, new_action):
        #controlla se la nuova azione è differente dalla precedente
        if new_action != self.action:
            self.action = new_action
            #update le setting dell'animazione
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(5) #5 è animazione di morte
                
    def draw(self):
        #disegna l'immagine caricata
        window.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Sign(pygame.sprite.Sprite):
    def __init__(self, x, y, text):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Assets/Sprites/Enemy2/Death/14.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        self.text = text

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            # Applica la trasformazione della telecamera alla posizione del testo
            text_pos = camera.apply(self).topleft
            lines = self.text.split(", ")
            x_offset = 50  # Sposta il testo 10 pixel a destra
            y_offset = -100  # Sposta il testo 30 pixel sopra
            for i, line in enumerate(lines):
                draw_text(line, font, WHITE, text_pos[0] + x_offset, text_pos[1] + y_offset + (i * 20))
        else:
            window.blit(self.image, camera.apply(self))

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        #controlla se il player è andato nelle boxes
        if pygame.sprite.collide_rect(self, player):
            #controlla che drop era
            if self.item_type == "Health": 
                player.health += 25
                heal_fx.play()
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Classic grenade":
                player.classic_grenades += 5
            elif self.item_type == "Atom grenade":
                player.atom_grenades += 2
            elif self.item_type == "Impact grenade":
                player.impact_grenades += 10

            #elimina l'item box
            self.kill()

class HealthBar():
    def __init__ (self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #aggiorna con nuova vita raccolta
        self.health = health

        #calcola la vita rimanente
        ratio = self.health / self.max_health
        pygame.draw.rect(window, BLACK, (self.x -2, self.y -2, 204, 19))
        pygame.draw.rect(window, RED, (self.x, self.y, 200, 15))
        pygame.draw.rect(window, GREEN, (self.x, self.y, 200 * ratio, 15))

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, timer, grenade_type, expl_type, speed, bounce, impact, damage, tmx_data):
        pygame.sprite.Sprite.__init__(self)
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
        self.tmx_data = tmx_data

    def check_collision(self):
        terrain_layer = self.tmx_data.get_layer_by_name("terrain")
        visible_layers = list(self.tmx_data.visible_layers)
        terrain_layer_index = visible_layers.index(terrain_layer)
        # Calcola i limiti dell'entità
        left = self.rect.left // (self.tmx_data.tilewidth * 2)
        right = self.rect.right // (self.tmx_data.tilewidth * 2)
        top = self.rect.top // (self.tmx_data.tileheight * 2)
        bottom = self.rect.bottom // (self.tmx_data.tileheight * 2)
        
        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                tile = self.tmx_data.get_tile_image(x, y, terrain_layer_index)
                if tile:
                    terrain_rect = pygame.Rect(x * self.tmx_data.tilewidth * 2, y * self.tmx_data.tileheight * 2, self.tmx_data.tilewidth * 2, self.tmx_data.tileheight * 2)
                    if self.rect.colliderect(terrain_rect):
                        return terrain_rect
        return None
        
    #applico gravità
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

       # controlla collisione con il terreno
        self.rect.y += dy
        collision_rect = self.check_collision()
        if collision_rect:
            if dy > 0:  # Moving down
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

            elif dy < 0:  # Moving up
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
                   
       # controlla collisioni orizzontali
        self.rect.x += dx
        collision_rect = self.check_collision()
        if collision_rect:
            if dx > 0:  # Moving right
                self.rect.right = collision_rect.left
                if self.impact:
                    self.explosion_function()
                if self.bounce:
                    self.direction *= -1
                else:
                    self.speed = 0
            elif dx < 0:  # Moving left
                self.rect.left = collision_rect.right
                if self.impact:
                    self.explosion_function()
                if self.bounce:
                    self.direction *= -1    
                else:
                    self.speed = 0


        #controlla se le granate sono ad impatto oppure no e falle esplodere in collisione con i nemici
        if self.impact:
            for enemy in enemy_group:
                if enemy.alive:
                    if pygame.sprite.spritecollide(enemy, grenade_group, False):
                        self.explosion_function()
                    else:
                        self.timer -= 1
                        if self.timer <= 0:
                            self.explosion_function()
        else:
        #timer countdown
            self.timer -= 1
            if self.timer <= 0:
                self.explosion_function()

    def explosion_function(self):
        explosion_fx.play()
        explosion = Explosion(self.rect.centerx, self.rect.bottom, 1.5, self.expl_type, self.damage)
        self.kill() 
        explosion_group.add(explosion)
        all_sprites.add(explosion)
        #fai danno a chi è vicino
        if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
            abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                    player.health -= self.damage
                    hurt_fx.play()

        for enemy in enemy_group:
            if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
            abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                enemy.health -= self.damage
                hurt_fx.play()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, expl_type, damage):
         pygame.sprite.Sprite.__init__(self)
         self.images = []
         self.num_of_frames = len(os.listdir(f"Assets/Sprites/Explosions/Pack/explosion-1-{expl_type}"))
         for num in range (self.num_of_frames):
            img = pygame.image.load(f"Assets/Sprites/Explosions/Pack/explosion-1-{expl_type}/{num}.png").convert_alpha()
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
        #aggiorna animazione
        EXPLOSION_SPEED = 10
        self.counter += 1
        self.image = self.images[self.frame_index]
        #controlla se il tempo è passato prima della nuova animazione
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
        if self.frame_index >= self.num_of_frames:
                self.kill()
        else:
                self.image = self.images[self.frame_index]

# Caricamento mappa di gioco
tmx_data = load_map("Data/tmx/tutorial.tmx")
map_width = tmx_data.width * tmx_data.tilewidth * 2
map_height = tmx_data.height * tmx_data.tileheight * 2

#crea telecamera 
camera = Camera(map_width, map_height)
                
#crea bottoni
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2, start_img, 3)
exit_button = button.Button(SCREEN_WIDTH // 2 + 130, SCREEN_HEIGHT // 2, exit_img, 3)
reload_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2, reload_img, 3)

#Crea gruppi sprite
all_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
sign_group = pygame.sprite.Group()
#Area temporanea per creare item box
item_box = ItemBox("Health", 1850, 345)
item_box_group.add(item_box)
all_sprites.add(item_box)
item_box = ItemBox("Atom grenade", 1750, 310)
item_box_group.add(item_box)
all_sprites.add(item_box)
item_box = ItemBox("Classic grenade", 2800, 470) 
item_box_group.add(item_box)
all_sprites.add(item_box)
item_box = ItemBox("Classic grenade", 600, 200) 
item_box_group.add(item_box)
all_sprites.add(item_box)
item_box = ItemBox("Impact grenade", 2325, 1175)
item_box_group.add(item_box)
all_sprites.add(item_box)
item_box = ItemBox("Impact grenade", 50, 725)
item_box_group.add(item_box)
all_sprites.add(item_box)

#Genera le varie entità
player = Character("Player", 500, 500, 3, 3, 100, True, tmx_data)
all_sprites.add(player)
health_bar = HealthBar(10, 10, player.health, player.health)

enemy1 = Character("Enemy1", 2000, 850, 3, 2, 100, False, tmx_data)
enemy2 = Character("Enemy2", 1300, 200, 3, 2, 200, False, tmx_data)

sign1 = Sign(505, 880, "Benvenuto!, premi 'a' per andare a sinistra, 'd' per andare a destra e 'space bar' per saltare, puoi usare 'shift' mentre cammini per correre, procedi verso destra ed entra nella grotta!")
sign2 = Sign(2000, 1050, "Fai attenzione al nemico!, se ti avvicini ti farà danno, prendi le GRANATE AD IMPATTO quì sotto, premi il tato '3' per selezionarle e poi 'f' per usarle, (è macchinoso lo so ci sto lavorando)")
sign3 = Sign(2080, 450, "Molto bene!, esplora la mappa e cerca altre granate se vuoi, (Per selezionare le GRANATE CLASSICHE premi '1', per le GRANATE AD ATOMI premi '2', per le GRANATE AD IMPATTO premi '3'), quando sei pronto affronta il boss salendo nell'isola!")

sign_group.add(sign1, sign2, sign3)
all_sprites.add(sign1, sign2, sign3)
enemy_group.add(enemy1)
all_sprites.add(enemy1)
enemy_group.add(enemy2)
all_sprites.add(enemy2)

running = True

while running: #ciclo che permette al programma di continuare finchè non si decide di uscire dal gioco 

    clock.tick(FPS)

    if start_game == False:
        #disegna menu principale
        draw_parallax_bg(camera)
        #disegna testo
        draw_text("CATTENHEIMER", font_big, WHITE, SCREEN_WIDTH // 2 -170, SCREEN_HEIGHT // 2 - 100)
        #aggiungi bottoni
        if start_button.draw(window):
            action_fx.play()
            start_game = True
        if exit_button.draw(window):
            action_fx.play()
            running = False

    else:
        camera.update(player)
        #disegna lo sfondo
        draw_parallax_bg(camera)
        draw_map(tmx_data, window, 2, camera)
        #mostra barra della vita
        health_bar.draw(player.health)

        #mostra quante granate ha il player
        if player.classic_grenades > 0:
            draw_text("GRANATE CLASSICHE: ", font, WHITE, 10, 35)
            for x in range(player.classic_grenades):
                window.blit(classic_grenade, (190 + (x * 10), 32))

        if player.atom_grenades > 0:
            draw_text("GRANATE AD ATOMI: ", font, WHITE, 10, 55)
            for x in range(player.atom_grenades):
                window.blit(atom_grenade, (185 + (x * 10), 53))

        if player.impact_grenades > 0:
            draw_text("GRANATE AD IMPATTO: ", font, WHITE, 10, 75)
            for x in range(player.impact_grenades):
                window.blit(impact_grenade, (195 + (x * 10), 73))

        all_sprites.update()
        for entity in all_sprites:
            if hasattr(entity, "flip"):
                window.blit(pygame.transform.flip(entity.image, entity.flip, False), camera.apply(entity))
            else:
                window.blit(entity.image, camera.apply(entity))

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            
        #disegna e aggiorna sprite groups
        grenade_group.update()
        item_box_group.update()
        explosion_group.update()
        sign_group.update()

        #aggiorna azioni del player
        if player.alive:
            #controllo il lancio delle granate
            if classic_grenade_trow:
                if grenade and grenade_thrown == False and player.classic_grenades > 0:
                    grenade = Grenade(player.rect.centerx + (0.3 * player.rect.size[0] * player.direction), player.rect.centery + (0.3 * player.rect.size[1]), player.direction, 150, classic_grenade, "d", 5, True, False, 50, tmx_data)
                    grenade_group.add(grenade)
                    all_sprites.add(grenade)
                    #riduci granate
                    player.classic_grenades -= 1 
                    grenade_thrown = True

            if atom_grenade_trow:
                if grenade and grenade_thrown == False and player.atom_grenades > 0:
                    grenade = Grenade(player.rect.centerx + (0.3 * player.rect.size[0] * player.direction), player.rect.centery + (0.3 * player.rect.size[1]), player.direction, 150, atom_grenade, "c", 4, True, False, 100, tmx_data)
                    grenade_group.add(grenade)
                    all_sprites.add(grenade)
                    #riduci granate
                    player.atom_grenades -= 1 
                    grenade_thrown = True
                
            if impact_grenade_trow:
                if grenade and grenade_thrown == False and player.impact_grenades > 0:
                    grenade = Grenade(player.rect.centerx + (0.3 * player.rect.size[0] * player.direction), player.rect.centery + (0.3 * player.rect.size[1]), player.direction, 150, impact_grenade, "a", 7, False, True, 25, tmx_data)
                    grenade_group.add(grenade)
                    all_sprites.add(grenade)
                    #riduci granate
                    player.impact_grenades -= 1 
                    grenade_thrown = True

            #aggiorna animazioni del player in base a cosa sta facendo
            if player.in_air:
                player.update_action(2) #2 significa che sta saltando
                player.still_cooldown = 400
            elif sprinting:
                player.update_action(4) #4 corsa
                player.still_cooldown = 400
            elif moving_left or moving_right:
                player.update_action(1) #1 camminare | perchè é la seconda nella lista self_action
                player.still_cooldown = 400
                player.jump_count -= 0.1
                if player.jump_count <= 0:
                    player.jump_count = 0
            elif grenade:
                player.update_action(3) #3 azione
                player.still_cooldown = 400      
            else:
                #ritorna a 0 (Idle) se non si muove a destra o sinistro
                player.still_cooldown -= 1
                if player.still_cooldown >= 0:
                    player.update_action(0)
                    if player.still_cooldown == 380:
                        player.jump_count = 0
                #leccati le ferite se stai fermo per un tot di tempo, aggiorna a 6
                else:
                    player.update_action(6)
                    player.health += 0.01
                    if player.health >= player.max_health:
                        player.health = player.max_health

            player.move(moving_left, moving_right)

            if enemy2.health <= 0 and enemy1.health <= 0:
                draw_text("VITTORIA", font_big, WHITE, SCREEN_WIDTH // 2 - 135, SCREEN_HEIGHT // 2 - 100)
                if reload_button.draw(window):
                    action_fx.play()
                    restart_level()
                elif exit_button.draw(window):
                    action_fx.play()
                    running = False

        else:
            draw_text("GAME OVER", font_big, WHITE, SCREEN_WIDTH // 2 -135, SCREEN_HEIGHT // 2 - 100)
            if reload_button.draw(window):
                action_fx.play()
                restart_level()
            elif exit_button.draw(window):
                action_fx.play()
                running = False

    for event in pygame.event.get(): 

        #esci dal gioco
        if event.type == pygame.QUIT:
                running = False  

        #input tasti premuti 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right =  True
            if event.key == pygame.K_LSHIFT:
                if player.action == 0:
                    sprinting = False
                else:
                    sprinting = True
            if event.key == pygame.K_SPACE:
                player.rect.y -= 1
                player.jump =  True
                if player.jump and player.in_air == False: #aggiungi un count alle volte che fai il salto, per aggiungere un fattore fatica
                    player.jump_count += 1
            if event.key == pygame.K_f:
                grenade = True
                player.action_done = True
            if event.key == pygame.K_1:
                atom_grenade_trow = False
                impact_grenade_trow = False 
                classic_grenade_trow = True  
            if event.key == pygame.K_2:
                classic_grenade_trow = False
                impact_grenade_trow = False
                atom_grenade_trow = True
            if event.key == pygame.K_3:
                classic_grenade_trow = False
                impact_grenade_trow = True
                atom_grenade_trow = False
            if event.key == pygame.K_ESCAPE:
                running = False
            
        #input tasti che però vengono rilasciati
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
                sprinting = False
            if event.key == pygame.K_d:
                moving_right =  False
                sprinting = False
            if event.key == pygame.K_LSHIFT:
                sprinting = False
            if event.key == pygame.K_SPACE:
                player.jump =  False
            if event.key == pygame.K_f:
                grenade = False
                grenade_thrown = False
                player.action_done = False
            if event.key == pygame.K_ESCAPE:
                running = False

    pygame.display.update()

pygame.quit()