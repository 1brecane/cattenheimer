import pygame


def check_terrain_collision(rect, tmx_data, terrain_layer_index):
    """Shared terrain collision check used by Character and Grenade."""
    tile_w2 = tmx_data.tilewidth * 2
    tile_h2 = tmx_data.tileheight * 2

    left = rect.left // tile_w2
    right = rect.right // tile_w2
    top = rect.top // tile_h2
    bottom = rect.bottom // tile_h2

    for x in range(left, right + 1):
        for y in range(top, bottom + 1):
            tile = tmx_data.get_tile_image(x, y, terrain_layer_index)
            if tile:
                terrain_rect = pygame.Rect(x * tile_w2, y * tile_h2, tile_w2, tile_h2)
                if rect.colliderect(terrain_rect):
                    return terrain_rect
    return None
