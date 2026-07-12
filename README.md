# Cattenheimer

Platformer 2D in pixel art dove un gatto esploratore affronta nemici a colpi
di granate. Scritto in Python con [pygame-ce](https://pyga.me/) e mappe
realizzate in [Tiled](https://www.mapeditor.org/).

## Avvio

```bash
pip install -r requirements.txt
python main.py
```

## Comandi

| Tasto | Azione |
|---|---|
| `A` / `D` | Muoviti a sinistra / destra |
| `Spazio` | Salta (consuma stamina) |
| `Shift` | Corri (consuma stamina) |
| `F` (tieni premuto) | Mira la granata: più a lungo miri, più lontano arriva. Rilascia per lanciare |
| `1` / `2` / `3` o rotella | Cambia tipo di granata |
| `Esc` | Pausa / torna al menu |

Dal menu principale si accede alle **impostazioni**: volume di musica ed
effetti e difficoltà dei nemici (salvate in `settings.json`).

## Struttura del progetto

```
main.py        avvio del gioco
core/          loop di gioco, impostazioni, caricamento asset
world/         camera, rendering mappa, collisioni (hitbox per-pixel e pendii)
entities/      personaggi (player/nemici), granate, item, cartelli
ui/            bottoni del menu
Assets/        sprite, suoni, musica, font
Data/tmx/      mappe Tiled: gli spawn di player, nemici, item e cartelli
               sono oggetti nel layer "entities" della mappa
tools/         script di utilità (ri-estrazione frame dallo spritesheet)
```

## Modificare il livello

Apri `Data/tmx/tutorial.tmx` in Tiled: il layer oggetti `entities` contiene
spawn del player, nemici (con proprietà `char_type`, `health`, `chase_mult`),
item (`item_type`) e cartelli (`text`). Il gioco li legge al caricamento,
senza coordinate nel codice.
