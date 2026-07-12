import pygame
import pytmx

from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT


def draw_text(text, font, text_col, x, y, surface):
    img = font.render(text, True, text_col)
    surface.blit(img, (x, y))


def draw_parallax_bg(camera, bg_layers, surface):
    speeds = [0.02, 0.05, 0.07, 0.1]
    for layer, speed in zip(bg_layers, speeds):
        layer_x = -camera.camera.x * speed
        layer_x = (layer_x % SCREEN_WIDTH) - SCREEN_WIDTH
        surface.blit(layer, (layer_x, 0))
        surface.blit(layer, (layer_x + SCREEN_WIDTH, 0))


def load_map(filename):
    return pytmx.util_pygame.load_pygame(filename)


def build_map_surface(tmx_data, scale):
    """Pre-renderizza tutti i layer visibili della mappa su un'unica surface."""
    width = tmx_data.width * tmx_data.tilewidth * scale
    height = tmx_data.height * tmx_data.tileheight * scale
    map_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    scaled_tiles = {}
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if not gid:
                    continue
                tile = scaled_tiles.get(gid)
                if tile is None:
                    img = tmx_data.get_tile_image_by_gid(gid)
                    if img is None:
                        continue
                    tile = pygame.transform.scale(
                        img,
                        (int(img.get_width() * scale), int(img.get_height() * scale)),
                    )
                    scaled_tiles[gid] = tile
                map_surface.blit(
                    tile,
                    (x * tmx_data.tilewidth * scale, y * tmx_data.tileheight * scale),
                )
    return map_surface


def draw_map(map_surface, surface, camera):
    surface.blit(map_surface, (camera.camera.x, camera.camera.y))
