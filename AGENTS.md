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

### Assets

| Path | Contents |
|------|----------|
| `assets/images/player/` | Throw frames `process_*.png`, walk frames `running*.png` |
| `assets/images/court/` | Background `quadradebasquete.png`, ball sprite `bola_basquete.png` |
| `assets/images/ui/` | Start screen image `start_screen.png` |
| `assets/sounds/` | `.wav`, 44.1kHz 16-bit stereo |

No tests, no CI, no formatter/linter config.

## Ball rendering

- Ball sprite loaded from `BALL_IMAGE_PATH` (`settings.py:54`), scaled to `BALL_RADIUS * 2` px.
- `_load_ball_image()` at `game.py:845` — falls back to `None` if file missing.
- `_draw_ball()` at `game.py:1311` — uses `blit()` with rotation if image available; draws orange circle fallback if not.
- Rotation: `ball_rotation += BALL_ROTATION_SPEED * dt` during flight (`game.py:324-326`), reset in `_launch_ball()` and `_reset_ball()`.

## Walk transition (3pt → free-throw)

- `_start_walk_transition()` at `game.py:878` — called from `_finalize_shot()` when missing a 3pt shot.
- `_update_walk_transition()` at `game.py:904` — interpolates `walk_player_pos` with cosine ease-in-out over `WALK_TOTAL_DURATION`.
- Ball follows player: `ball_pos.update(_get_ball_rest_position())` at each step (`game.py:918-919`).
- After transition ends: `_reset_ball()` called, `at_three_point_line` set back to `False`.

## Field calibration

Hoop/backboard pixel coords in `src/settings.py:99-107`. Adjust `RIM_Y`, `RIM_LEFT_X`, `RIM_RIGHT_X` to match background image. Player anchor positions at lines 25-28 (`PLAYER_BASE_X/Y_FREETHROW` / `THREE_POINT`).

## Sound system

- `pygame.mixer.init(frequency=44100)` at `game.py:20` — must match WAV sample rate (44.1 kHz). Default (22050 Hz) causes slow/distorted playback.
- Sounds loaded at `game.py:71-73` via `_load_sound()` (returns `None` if file missing).
- Play via `_play_sound()` (no-op if `None`).
- Sound files:
  - `preparation.wav` — plays on drag start (`game.py:388`); stopped before score/miss sounds, on drag cancel, and before replaying.
  - `acertou.wav` — Faustão "acertou!", plays on made basket (`game.py:754`).
  - `errou.wav` — Faustão "errou!", plays on early miss detection (ball passes below rim, `game.py:352-354`) with fallback in `_finalize_shot()` (`game.py:776-779`).
  - `som_aro.wav` — rim hit sound, plays on hoop collision (`game.py:660`); 0.15s cooldown to avoid retrigger spam.
- Early failure buzzer: fires when `ball_was_above_rim` and ball descends past `RIM_Y` without scoring — no need to wait for floor bounces.
- Trimming silence from WAV: `ffmpeg -i file.wav -ss 00:00.X -t 00:00.Y file_trimmed.wav` (use `python3` with `wave` module to detect silence).
- `errou.wav` cut at 0.44s (not 0.495s — that clipped the "e" making it sound like "rou").
- Windows users: use `python -m yt_dlp` instead of `yt-dlp` if not on PATH.

## Known quirks

- `settings.py:131,133`: `COLOR_SUCCESS` defined twice — second override wins.
- `USE_BACKGROUND_IMAGE` auto-detects file existence; `SHOW_HOOP_OVERLAY_ON_PHOTO` / `SHOW_PLAYER_SILHOUETTE_ON_PHOTO` gate overlay rendering.
- No type checking, no linting configured.
