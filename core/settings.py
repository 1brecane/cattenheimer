SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

GRAVITY = 0.45
TILE_SIZE = 40

# shifts the view upward: the player sits below the screen center,
# showing more sky and less ground
CAMERA_OFFSET_Y = 100

RED = (229, 101, 46)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (102, 146, 61)
YELLOW = (230, 195, 60)

DIFFICULTY_ORDER = ["EASY", "NORMAL", "HARD"]
DIFFICULTIES = {
    "EASY": {"health_mult": 0.6, "contact_damage": 5, "speed_mult": 1.0},
    "NORMAL": {"health_mult": 1.0, "contact_damage": 10, "speed_mult": 1.0},
    "HARD": {"health_mult": 1.5, "contact_damage": 20, "speed_mult": 1.25},
}
