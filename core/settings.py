SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

GRAVITY = 0.45
TILE_SIZE = 40

# sposta la visuale verso l'alto: il player sta sotto il centro dello
# schermo, così si vede più cielo e meno terreno
CAMERA_OFFSET_Y = 100

RED = (229, 101, 46)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (102, 146, 61)

DIFFICULTY_ORDER = ["FACILE", "NORMALE", "DIFFICILE"]
DIFFICULTIES = {
    "FACILE": {"health_mult": 0.6, "contact_damage": 5, "speed_mult": 1.0},
    "NORMALE": {"health_mult": 1.0, "contact_damage": 10, "speed_mult": 1.0},
    "DIFFICILE": {"health_mult": 1.5, "contact_damage": 20, "speed_mult": 1.25},
}
