# AGENTS.md

## Run

```sh
python -m src.main          # run game
```

Activate `.venv/` first. Only dependency: `pygame>=2.5.0`.

## Architecture

- `src/main.py` — entrypoint
- `src/game.py` — `FreeThrowGame` class (init, event loop, physics, rendering)
- `src/settings.py` — all constants (screen, physics, colors, hoop/backboard coords)

Assets under `assets/images/player/` (throw frames `process_*.png`, walk frames `running*.png`). No tests, no CI, no formatter/linter config.

## Field calibration

Hoop/backboard pixel coords in `src/settings.py:97-105`. Adjust `RIM_Y`, `RIM_LEFT_X`, `RIM_RIGHT_X` to match background image. Player anchor positions at lines 25-28 (`PLAYER_BASE_X/Y_FREETHROW` / `THREE_POINT`).

## Known quirks

- `settings.py:129,131`: `COLOR_SUCCESS` defined twice — second override wins.
- `USE_BACKGROUND_IMAGE` auto-detects file existence; `SHOW_HOOP_OVERLAY_ON_PHOTO` / `SHOW_PLAYER_SILHOUETTE_ON_PHOTO` gate overlay rendering.
- `sounds/` and `fonts/` dirs are empty (`.gitkeep`).
- No type checking, no linting configured.
