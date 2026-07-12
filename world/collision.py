import pygame


def build_terrain_geometry(tmx_data, terrain_layer_index, scale=2):
    """Collision geometry for every gid of the terrain layer.

    Returns (solid_hitboxes, slope_heightmaps, full_hitboxes):
    - solid_hitboxes: gid -> Rect of the visible pixels (flat-surface
      tiles, including half blocks)
    - slope_heightmaps: gid -> surface height for every pixel column
      (slanted tiles: characters follow the profile)
    - full_hitboxes: every gid as a Rect (for grenades)
    """
    solid = {}
    slopes = {}
    full = {}
    layer = list(tmx_data.visible_layers)[terrain_layer_index]
    for _, _, gid in layer:
        if not gid or gid in full:
            continue
        img = tmx_data.get_tile_image_by_gid(gid)
        if img is None:
            continue
        bounds = img.get_bounding_rect()
        if not (bounds.width and bounds.height):
            continue
        rect = pygame.Rect(
            bounds.x * scale, bounds.y * scale,
            bounds.width * scale, bounds.height * scale,
        )
        full[gid] = rect

        # top profile: first opaque pixel of each column
        w, h = img.get_size()
        tops = []
        for x in range(w):
            top = None
            for y in range(h):
                if img.get_at((x, y)).a > 0:
                    top = y
                    break
            tops.append(top)
        opaque_tops = [t for t in tops if t is not None]
        if max(opaque_tops) - min(opaque_tops) <= 4:
            solid[gid] = rect
        else:
            heightmap = []
            for t in tops:
                v = t * scale if t is not None else None
                heightmap.extend([v] * scale)
            slopes[gid] = heightmap
    return solid, slopes, full


def slope_surface_y(rect, tmx_data, terrain_layer_index, heightmaps, probe=8):
    """Y of a slope surface under the rect center, or None."""
    if not heightmaps:
        return None
    tile_w2 = tmx_data.tilewidth * 2
    tile_h2 = tmx_data.tileheight * 2
    tx = rect.centerx // tile_w2
    if not 0 <= tx < tmx_data.width:
        return None
    col = rect.centerx % tile_w2
    top_row = max((rect.bottom - tile_h2) // tile_h2, 0)
    bottom_row = min((rect.bottom + probe) // tile_h2, tmx_data.height - 1)
    for ty in range(top_row, bottom_row + 1):
        gid = tmx_data.get_tile_gid(tx, ty, terrain_layer_index)
        heightmap = heightmaps.get(gid)
        if heightmap:
            offset = heightmap[col]
            if offset is not None:
                return ty * tile_h2 + offset
    return None


def check_terrain_collision(rect, tmx_data, terrain_layer_index, hitboxes):
    """Shared terrain collision check used by Character and Grenade."""
    tile_w2 = tmx_data.tilewidth * 2
    tile_h2 = tmx_data.tileheight * 2

    # pytmx raises ValueError outside the map bounds
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
