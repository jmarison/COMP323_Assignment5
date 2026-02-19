# Week 5 Example — Animation + Feedback

This example supports the Week 5 slides (animation states, dt-driven frame timers, and feedback bundles).

## Learning goals

- Implement a basic animation timer (dt-driven)
- Choose animation by state (idle/run/hurt)
- Keep motion smooth with float positions + `Rect`
- Add a small feedback bundle (flash/shake/hitstop/particles)
- Handle rotation without drift (`get_rect(center=...)`)

## Run
From this folder:

- `python3 -m pip install pygame`
- `python3 main.py`

## Controls
- Arrow keys / WASD: move
- `Space`: start / restart
- `F1`: toggle debug overlay (hitboxes)
- `R`: reset level
- `1`: toggle flash cue
- `2`: toggle screen shake cue
- `3`: toggle hitstop cue
- `4`: toggle particles cue
- `Esc`: quit

## What to change first
- Change animation speed (fps) in `anim_feedback/game.py`
- Add one more state (e.g., `hurt` animation)
- Add a new event and choose a feedback bundle for it
