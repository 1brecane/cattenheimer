"""Re-extracts the Player frames from the original sprite sheet.

The frames in Assets/Sprites/Player/* are 16x16 crops, but the sheet
uses 32x32 logical cells: poses that overflow the crop (e.g. the jump)
end up clipped. This script locates each frame in the sheet, takes the
full 32x32 cell and saves the tight crop of its content.

Usage: python tools/extract_frames.py
"""

import os

import pygame

SHEET_PATH = "Assets/Sprites/Player/player_ss1.png"
SPRITE_DIR = "Assets/Sprites/Player"
FRAME = 16
CELL = 32


def normalized_bytes(surface):
    """RGBA with transparent pixels zeroed out (the RGB channels of
    invisible pixels differ between the sheet and the extracted frames)."""
    px = bytearray(pygame.image.tobytes(surface.convert_alpha(), "RGBA"))
    for i in range(0, len(px), 4):
        if px[i + 3] == 0:
            px[i] = px[i + 1] = px[i + 2] = 0
        else:
            px[i + 3] = 255
    return bytes(px)


def find_in_sheet(sheet_px, sheet_size, target):
    """Searches for the 16x16 frame in the sheet, on an 8px grid then 1px."""
    w, h = sheet_size
    row_len = FRAME * 4
    for step in (FRAME // 2, 1):
        for y in range(0, h - FRAME + 1, step):
            for x in range(0, w - FRAME + 1, step):
                for r in range(FRAME):
                    start = ((y + r) * w + x) * 4
                    if sheet_px[start:start + row_len] != target[r * row_len:(r + 1) * row_len]:
                        break
                else:
                    return x, y
    return None


def main():
    pygame.init()
    pygame.display.set_mode((32, 32))
    sheet = pygame.image.load(SHEET_PATH).convert_alpha()
    sheet_px = normalized_bytes(sheet)

    for anim in sorted(os.listdir(SPRITE_DIR)):
        anim_dir = os.path.join(SPRITE_DIR, anim)
        if not os.path.isdir(anim_dir):
            continue
        for name in sorted(os.listdir(anim_dir)):
            path = os.path.join(anim_dir, name)
            frame = pygame.image.load(path).convert_alpha()
            if frame.get_size() != (FRAME, FRAME):
                print(f"skip {path}: size {frame.get_size()}")
                continue
            found = find_in_sheet(sheet_px, sheet.get_size(), normalized_bytes(frame))
            if found is None:
                print(f"NOT FOUND {path}: left unchanged")
                continue
            fx, fy = found
            cx, cy = (fx // CELL) * CELL, (fy // CELL) * CELL
            cell = sheet.subsurface((cx, cy, CELL, CELL))
            bounds = cell.get_bounding_rect()
            tight = cell.subsurface(bounds).copy()
            pygame.image.save(tight, path)
            cut = frame.get_bounding_rect()
            was_cut = (
                cut.top == 0 or cut.left == 0
                or cut.right == FRAME or cut.bottom == FRAME
            )
            marker = "  <- was clipped" if tight.get_size() != cut.size and was_cut else ""
            print(f"{path}: {tight.get_width()}x{tight.get_height()}{marker}")

    pygame.quit()


if __name__ == "__main__":
    main()
