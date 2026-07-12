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


def draw_map(tmx_data, surface, scale, camera):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    tile_x = x * tmx_data.tilewidth * scale + camera.camera.x
                    tile_y = y * tmx_data.tileheight * scale + camera.camera.y
                    if -50 <= tile_x < SCREEN_WIDTH and -50 <= tile_y < SCREEN_HEIGHT:
                        scaled_tile = pygame.transform.scale(
                            tile,
                            (int(tile.get_width() * scale), int(tile.get_height() * scale)),
                        )
                        surface.blit(scaled_tile, (tile_x, tile_y))
