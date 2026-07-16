# Cattenheimer

A 2D pixel-art platformer where an explorer cat fights enemies with
grenades. Written in Python with [pygame-ce](https://pyga.me/), with maps
made in [Tiled](https://www.mapeditor.org/).

## Getting started

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
|---|---|
| `A` / `D` | Move left / right |
| `Space` | Jump (costs stamina) |
| `Shift` | Sprint (drains stamina) |
| `F` (hold) | Aim the grenade: the longer you aim, the farther it flies. Release to throw |
| `1` / `2` / `3` or mouse wheel | Switch grenade type |
| `F11` | Toggle fullscreen |
| `Esc` | Pause / back to menu |

The main menu has a **settings** screen: music and SFX volume, fullscreen
and enemy difficulty (persisted to `settings.json`).

## Project layout

```
main.py        game entry point
core/          game loop, settings, asset loading
world/         camera, map rendering, collisions (per-pixel hitboxes and slopes)
entities/      characters (player/enemies), grenades, items, signs
ui/            menu buttons
Assets/        sprites, sounds, music, fonts
Data/tmx/      Tiled maps: player spawn, enemies, items and signs are
               objects in the map's "entities" layer
tools/         utility scripts (frame re-extraction from the sprite sheet)
```

## Editing the level

Open `Data/tmx/tutorial.tmx` in Tiled: the `entities` object layer holds
the player spawn, enemies (with `char_type`, `health`, `chase_mult`
properties), items (`item_type`) and signs (`text`). The game reads them
at load time — no coordinates in the code.

## Adding a level

Any `.tmx` map with a `terrain` layer (tile layer, `collision=true`
property) and at least one `player` spawn object works. Register it in
`LEVELS`/`LEVEL_ORDER` in `core/settings.py`; it then shows up in the
settings menu's `LEVEL` selector.
