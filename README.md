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
- `M` : Mute Sound

## What to change first
- Change animation speed (fps) in `anim_feedback/game.py`
- Add one more state (e.g., `hurt` animation)
- Add a new event and choose a feedback bundle for it

## What I added
- Enemy which patrols an area until the player enters its detection range which it then persues the player as long as its in range and then returns to patrol area once player leaves range
- Enemy cycles through state of "chase" and "walk" 
- Animation to show when player enters and leaves the enemy's detection range 
- Sound effects for coin, player hit, and enemy alerted of player


## Iteration Log
- Tuned enemy detection radius to 180 px. Initially was too large and felt as if the enemy were never patrolling only permanently chasing player. Felt unescapble. 
- Enemy tracking. I intially had the enemies collide and go around walls, but often got stuck.
- Slowed enemy speed to compensate for lack of wall collision. 

## Rationale
 Feedback is attached to two key game events: coin collection and hazard/enemy collision. For coin pickups, a sound effect confirms the pickup, giving the player a reward signal. For hits, flash, hitstop, shake, particles, and the hurt sound all play. The enemy's chase animation (faster leg cycle, angry brows) gives the player an advance read on incoming danger before contact, supporting avoidance decisions. The goal of the enemy is to encourage a more disciplined play style where players have to work to get the enemy out of the way by grabbing the enemy's attention before leading them away from coins so the player can loop around and grab them while enemy is chasing. 
