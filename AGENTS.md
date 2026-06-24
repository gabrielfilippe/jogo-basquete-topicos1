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

Assets under `assets/images/player/` (throw frames `process_*.png`, walk frames `running*.png`).
Sound assets under `assets/sounds/`  (`.wav`, 44.1kHz 16-bit stereo). No tests, no CI, no formatter/linter config.

## Field calibration

Hoop/backboard pixel coords in `src/settings.py:97-105`. Adjust `RIM_Y`, `RIM_LEFT_X`, `RIM_RIGHT_X` to match background image. Player anchor positions at lines 25-28 (`PLAYER_BASE_X/Y_FREETHROW` / `THREE_POINT`).

## Known quirks

- `settings.py:129,131`: `COLOR_SUCCESS` defined twice — second override wins.
- `USE_BACKGROUND_IMAGE` auto-detects file existence; `SHOW_HOOP_OVERLAY_ON_PHOTO` / `SHOW_PLAYER_SILHOUETTE_ON_PHOTO` gate overlay rendering.
- Sound system in `src/game.py`: mixer init on line 20, sounds loaded at lines 67-69. Methods `_load_sound()` / `_play_sound()` at lines 817-827.
  - `preparation.wav` — plays when player clicks ball to aim (line 367), stops on score/miss.
  - `success.wav` — plays on made basket (line 707), stops preparation sound first.
  - `failure.wav` — plays on miss (line 730), stops preparation sound first.
- Trimming silence from WAV: `ffmpeg -i file.wav -ss 00:00.X -t 00:00.Y file_trimmed.wav` (use `python3` with `wave` module to detect silence).
- `sounds/` and `fonts/` dirs used to be empty — `NBASound.wav` extracted via `yt-dlp`.
- No type checking, no linting configured.
