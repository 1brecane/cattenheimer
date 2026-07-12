import pygame

from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def load_sounds():
    pygame.mixer.music.load("Assets/music/time_for_adventure.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1, 0.0, 5000)

    sounds = {
        "jump": pygame.mixer.Sound("Assets/sounds/jump.wav"),
        "explosion": pygame.mixer.Sound("Assets/sounds/explosion.wav"),
        "action": pygame.mixer.Sound("Assets/sounds/tap.wav"),
        "hurt": pygame.mixer.Sound("Assets/sounds/hurt.wav"),
        "heal": pygame.mixer.Sound("Assets/sounds/power_up.wav"),
    }
    for sfx in sounds.values():
        sfx.set_volume(0.5)
    return sounds


def load_images():
    images = {
        "start": pygame.image.load("Assets/Buttons/start.png").convert_alpha(),
        "reload": pygame.image.load("Assets/Buttons/reload.png").convert_alpha(),
        "exit": pygame.image.load("Assets/Buttons/exit.png").convert_alpha(),
        "classic_grenade": pygame.image.load("Assets/Items/classic_grenade.png").convert_alpha(),
        "atom_grenade": pygame.image.load("Assets/Items/atom_grenade.png").convert_alpha(),
        "impact_grenade": pygame.image.load("Assets/Items/impact_grenade.png").convert_alpha(),
        "onigiri": pygame.image.load("Assets/Items/onigiri_1.png").convert_alpha(),
    }

    bg_layers = []
    for i in range(1, 5):
        layer = pygame.image.load(f"Assets/Clouds/Clouds 2/{i}.png").convert_alpha()
        layer = pygame.transform.scale(layer, (SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_layers.append(layer)
    images["bg_layers"] = bg_layers

    images["item_boxes"] = {
        "Health": images["onigiri"],
        "Classic grenade": images["classic_grenade"],
        "Atom grenade": images["atom_grenade"],
        "Impact grenade": images["impact_grenade"],
    }

    return images


def load_fonts():
    return {
        "small": pygame.font.SysFont("Pixel Operator 8", 12),
        "big": pygame.font.SysFont("Pixel Operator 8", 36, True, True),
    }
