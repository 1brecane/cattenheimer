import pygame


def build_terrain_hitboxes(tmx_data, terrain_layer_index, scale=2):
    """Hitbox per gid basate sui pixel non trasparenti del tile.

    I tile parziali (es. mezzo blocco di terra) collidono così solo con
    la parte visibile invece che con l'intero quadrato del tile.
    """
    hitboxes = {}
    layer = list(tmx_data.visible_layers)[terrain_layer_index]
    for _, _, gid in layer:
        if not gid or gid in hitboxes:
            continue
        img = tmx_data.get_tile_image_by_gid(gid)
        if img is None:
            continue
        bounds = img.get_bounding_rect()
        if bounds.width and bounds.height:
            hitboxes[gid] = pygame.Rect(
                bounds.x * scale, bounds.y * scale,
                bounds.width * scale, bounds.height * scale,
            )
    return hitboxes


def check_terrain_collision(rect, tmx_data, terrain_layer_index, hitboxes):
    """Shared terrain collision check used by Character and Grenade."""
    tile_w2 = tmx_data.tilewidth * 2
    tile_h2 = tmx_data.tileheight * 2

    # pytmx lancia ValueError fuori dai limiti della mappa
    left = max(rect.left // tile_w2, 0)
    right = min(rect.right // tile_w2, tmx_data.width - 1)
    top = max(rect.top // tile_h2, 0)
    bottom = min(rect.bottom // tile_h2, tmx_data.height - 1)

    for x in range(left, right + 1):
        for y in range(top, bottom + 1):
            gid = tmx_data.get_tile_gid(x, y, terrain_layer_index)
            hitbox = hitboxes.get(gid)
            if hitbox:
                terrain_rect = hitbox.move(x * tile_w2, y * tile_h2)
                if rect.colliderect(terrain_rect):
                    return terrain_rect
    return None
