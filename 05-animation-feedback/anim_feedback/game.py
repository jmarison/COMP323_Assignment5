from __future__ import annotations

from dataclasses import dataclass, field
import random
#used for audio sfx
from pathlib import Path

import pygame


@dataclass(frozen=True)
class Palette:
    bg: pygame.Color = field(default_factory=lambda: pygame.Color("#1e222a"))
    panel: pygame.Color = field(default_factory=lambda: pygame.Color("#2a303c"))
    text: pygame.Color = field(default_factory=lambda: pygame.Color("#e5e9f0"))
    subtle: pygame.Color = field(default_factory=lambda: pygame.Color("#a3adbf"))

    player: pygame.Color = field(default_factory=lambda: pygame.Color("#88c0d0"))
    coin: pygame.Color = field(default_factory=lambda: pygame.Color("#ebcb8b"))
    hazard: pygame.Color = field(default_factory=lambda: pygame.Color("#bf616a"))
    particle: pygame.Color = field(default_factory=lambda: pygame.Color("#a3be8c"))
    wall: pygame.Color = field(default_factory=lambda: pygame.Color("#4c566a"))
    enemy: pygame.Color = field(default_factory=lambda: pygame.Color("#b48ead"))


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


class Animation:
    def __init__(self, frames: list[pygame.Surface], *, fps: float) -> None:
        if not frames:
            raise ValueError("Animation needs at least 1 frame")
        self.frames = frames
        self.frame_dt = 1.0 / fps
        self.t = 0.0
        self.i = 0

    def reset(self) -> None:
        self.t = 0.0
        self.i = 0

    def update(self, dt: float) -> None:
        self.t += dt
        while self.t >= self.frame_dt:
            self.t -= self.frame_dt
            self.i = (self.i + 1) % len(self.frames)

    @property
    def image(self) -> pygame.Surface:
        return self.frames[self.i]


@dataclass
class Particle:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: float
    color: pygame.Color
    life: float
    ttl: float

    def update(self, dt: float) -> None:
        self.life = max(0.0, self.life - dt)
        self.pos += self.vel * dt

    @property
    def alive(self) -> bool:
        return self.life > 0


class Wall(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.Rect, color: pygame.Color) -> None:
        super().__init__()
        self.rect = rect.copy()
        self.color = color


class Coin(pygame.sprite.Sprite):
    def __init__(
        self,
        center: tuple[int, int],
        *,
        color: pygame.Color,
    ) -> None:
        super().__init__()
        self.anim = Animation(_make_coin_frames(color), fps=10.0)
        self.image = self.anim.image
        self.rect = self.image.get_rect(center=center)

    def update(self, dt: float) -> None:
        self.anim.update(dt)
        center = self.rect.center
        self.image = self.anim.image
        self.rect = self.image.get_rect(center=center)


class Hazard(pygame.sprite.Sprite):
    def __init__(
        self,
        center: tuple[int, int],
        *,
        color: pygame.Color,
        size: int = 34,
        spin_speed_dps: float = 210.0,
    ) -> None:
        super().__init__()
        self.base = _make_hazard_surface(size, color)
        self.angle = 0.0
        self.spin_speed_dps = spin_speed_dps

        self.image = self.base
        self.rect = self.image.get_rect(center=center)

    def update(self, dt: float) -> None:
        self.angle = (self.angle + self.spin_speed_dps * dt) % 360.0
        center = self.rect.center
        self.image = pygame.transform.rotate(self.base, self.angle)
        self.rect = self.image.get_rect(center=center)

# enemy - normal speed, alerted speed (when player enters detect dist.) and detect distance
# which is the "alert" range for the enemy
ENEMY_PATROL_SPEED = 90.0
ENEMY_CHASE_SPEED  = 160.0
ENEMY_DETECT_DIST  = 180.0   # pixels — switches to chase state


class Enemy(pygame.sprite.Sprite):

    def __init__(
        self,
        waypoint_a: tuple[int, int],
        waypoint_b: tuple[int, int],
        *,
        color: pygame.Color,
    ) -> None:
        super().__init__()

        self.waypoints = [pygame.Vector2(waypoint_a), pygame.Vector2(waypoint_b)]
        self.wp_index  = 1     
        self.pos       = pygame.Vector2(waypoint_a)
        self.facing    = 1       
        self.anims = _make_enemy_anims(color)
        self.state = "walk" # walk | chase  

        self.image = self.anims[self.state].image
        self.rect  = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def _set_state(self, new_state: str) -> None:
        if new_state == self.state:
            return
        self.state = new_state
        self.anims[self.state].reset()


    def update(self, dt: float, player_pos: pygame.Vector2) -> None:  
        to_player = player_pos - self.pos
        dist      = to_player.length()

        if dist < ENEMY_DETECT_DIST:
            # Chase state 
            self._set_state("chase")
            speed     = ENEMY_CHASE_SPEED
            direction = to_player.normalize() if dist > 0 else pygame.Vector2(1, 0)
        else:
            # Walk state - serves as a patrol 
            self._set_state("walk")
            speed     = ENEMY_PATROL_SPEED
            to_wp     = self.waypoints[self.wp_index] - self.pos
            if to_wp.length() < 4:
                self.wp_index = 1 - self.wp_index
                to_wp = self.waypoints[self.wp_index] - self.pos
            direction = to_wp.normalize() if to_wp.length() > 0 else pygame.Vector2(1, 0)

        if direction.x != 0:
            self.facing = 1 if direction.x > 0 else -1

        self.pos += direction * speed * dt

        self.anims[self.state].update(dt)
        center = self.rect.center
        base_image = self.anims[self.state].image
        # Flip horizontally based on direciton facing
        self.image = pygame.transform.flip(base_image, self.facing < 0, False)
        self.rect  = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        center: tuple[int, int],
        *,
        color: pygame.Color,
    ) -> None:
        super().__init__()

        self.anims = _make_player_anims(color)
        self.state = "idle"
        self.prev_state = "idle"

        self.image = self.anims[self.state].image
        self.rect = self.image.get_rect(center=center)

        self.pos = pygame.Vector2(self.rect.center)
        self.vel = pygame.Vector2(0, 0)
        self.speed = 320.0

        self.hp = 3
        self.invincible_for = 0.0

        self.score = 0

        self.flash_for = 0.0

    @property
    def is_invincible(self) -> bool:
        return self.invincible_for > 0

    def set_state(self, new_state: str) -> None:
        if new_state == self.state:
            return
        self.prev_state = self.state
        self.state = new_state
        self.anims[self.state].reset()

    def update(self, dt: float) -> None:
        self.anims[self.state].update(dt)
        center = self.rect.center
        self.image = self.anims[self.state].image
        self.rect = self.image.get_rect(center=center)

        if self.invincible_for > 0:
            self.invincible_for = max(0.0, self.invincible_for - dt)

        if self.flash_for > 0:
            self.flash_for = max(0.0, self.flash_for - dt)


class Game:
    fps = 60

    SCREEN_W, SCREEN_H = 960, 540
    HUD_H = 56
    PADDING = 12

    def __init__(self) -> None:
        self.palette = Palette()

        # Audio setup
        base_path = Path(__file__).parent
        self.coin_sfx = pygame.mixer.Sound(str(base_path / "media" / "coin_sfx.mp3"))
        self.coin_sfx.set_volume(0.5)
        self.hurt_sfx = pygame.mixer.Sound(str(base_path / "media" / "hurt_sfx.mp3"))
        self.hurt_sfx.set_volume(0.5)
        self.alert_sfx = pygame.mixer.Sound(str(base_path / "media" / "alert.mp3"))
        self.alert_sfx.set_volume(0.5)
        self.muted = False


        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self.font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 40)

        self.screen_rect = pygame.Rect(0, 0, self.SCREEN_W, self.SCREEN_H)
        self.playfield = pygame.Rect(
            self.PADDING,
            self.HUD_H + self.PADDING,
            self.SCREEN_W - 2 * self.PADDING,
            self.SCREEN_H - self.HUD_H - 2 * self.PADDING,
        )

        self.debug = False
        self.state = "title"  # title | play | gameover

        self.cue_flash = True
        self.cue_shake = True
        self.cue_hitstop = True
        self.cue_particles = True

        self.rng = random.Random(5)

        self.all_sprites: pygame.sprite.Group[pygame.sprite.Sprite] = pygame.sprite.Group()
        self.walls: pygame.sprite.Group[Wall] = pygame.sprite.Group()
        self.coins: pygame.sprite.Group[Coin] = pygame.sprite.Group()
        self.hazards: pygame.sprite.Group[Hazard] = pygame.sprite.Group()
        self.enemies: pygame.sprite.Group[Enemy] = pygame.sprite.Group()

        self.player = Player(self.playfield.center, color=self.palette.player)
        self.all_sprites.add(self.player)

        self.particles: list[Particle] = []

        self._shake_for = 0.0
        self._hitstop_for = 0.0

        self._reset_level(keep_state=True)

    def _reset_level(self, *, keep_state: bool = False) -> None:
        self.all_sprites.empty()
        self.walls.empty()
        self.coins.empty()
        self.hazards.empty()
        self.enemies.empty()
        self.particles.clear()

        self.player = Player(self.playfield.center, color=self.palette.player)
        self.all_sprites.add(self.player)

        def add_wall(r: pygame.Rect) -> None:
            wall = Wall(r, self.palette.wall)
            self.walls.add(wall)
            self.all_sprites.add(wall)

        t = 16
        add_wall(pygame.Rect(self.playfield.left, self.playfield.top, self.playfield.width, t))
        add_wall(pygame.Rect(self.playfield.left, self.playfield.bottom - t, self.playfield.width, t))
        add_wall(pygame.Rect(self.playfield.left, self.playfield.top, t, self.playfield.height))
        add_wall(pygame.Rect(self.playfield.right - t, self.playfield.top, t, self.playfield.height))

        add_wall(pygame.Rect(self.playfield.left + 180, self.playfield.top + 110, 18, 240))
        add_wall(pygame.Rect(self.playfield.left + 420, self.playfield.top + 140, 18, 240))
        add_wall(pygame.Rect(self.playfield.left + 560, self.playfield.top + 240, 260, 18))

        hz1 = Hazard((self.playfield.centerx + 190, self.playfield.centery - 80), color=self.palette.hazard)
        hz2 = Hazard((self.playfield.centerx - 150, self.playfield.centery + 140), color=self.palette.hazard, spin_speed_dps=260)
        self.hazards.add(hz1, hz2)
        self.all_sprites.add(hz1, hz2)

        #  Enemies 
        e1 = Enemy(
            (self.playfield.left + 60,  self.playfield.top + 200),
            (self.playfield.left + 360, self.playfield.top + 200),
            color=self.palette.enemy,
        )
        e2 = Enemy(
            (self.playfield.right - 60,  self.playfield.bottom - 100),
            (self.playfield.right - 300, self.playfield.bottom - 100),
            color=self.palette.enemy,
        )
        self.enemies.add(e1, e2)
        self.all_sprites.add(e1, e2)

        for _ in range(10):
            for __ in range(120):
                x = self.rng.randint(self.playfield.left + 50, self.playfield.right - 50)
                y = self.rng.randint(self.playfield.top + 50, self.playfield.bottom - 50)
                candidate = Coin((x, y), color=self.palette.coin)

                if pygame.sprite.spritecollideany(candidate, self.walls):
                    continue
                if pygame.sprite.spritecollideany(candidate, self.coins):
                    continue
                if candidate.rect.colliderect(self.player.rect):
                    continue

                self.coins.add(candidate)
                self.all_sprites.add(candidate)
                break

        if not keep_state:
            self.state = "play"

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.key == pygame.K_F1:
            self.debug = not self.debug
            return

        if event.key == pygame.K_r:
            self._reset_level(keep_state=(self.state == "title"))
            return

        if event.key == pygame.K_1:
            self.cue_flash = not self.cue_flash
            return

        if event.key == pygame.K_2:
            self.cue_shake = not self.cue_shake
            return

        if event.key == pygame.K_3:
            self.cue_hitstop = not self.cue_hitstop
            return

        if event.key == pygame.K_4:
            self.cue_particles = not self.cue_particles
            return
        
        if event.key == pygame.K_m:
            self.muted = not self.muted
            return

        if self.state in {"title", "gameover"} and event.key == pygame.K_SPACE:
            self._reset_level(keep_state=True)
            self.state = "play"

    def _read_move(self) -> pygame.Vector2:
        keys = pygame.key.get_pressed()

        x = 0
        y = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            y += 1

        v = pygame.Vector2(x, y)
        if v.length_squared() > 0:
            v = v.normalize()
        return v

    def _move_player_axis(self, axis: str, amount: float) -> None:
        if axis == "x":
            self.player.pos.x += amount
            self.player.rect.centerx = int(round(self.player.pos.x))
        else:
            self.player.pos.y += amount
            self.player.rect.centery = int(round(self.player.pos.y))

        hits = pygame.sprite.spritecollide(self.player, self.walls, dokill=False)
        if not hits:
            return

        for wall in hits:
            if axis == "x":
                if amount > 0:
                    self.player.rect.right = wall.rect.left
                elif amount < 0:
                    self.player.rect.left = wall.rect.right
                self.player.pos.x = self.player.rect.centerx
            else:
                if amount > 0:
                    self.player.rect.bottom = wall.rect.top
                elif amount < 0:
                    self.player.rect.top = wall.rect.bottom
                self.player.pos.y = self.player.rect.centery

    def _spawn_particles(self, center: tuple[int, int], *, color: pygame.Color, count: int) -> None:
        for _ in range(count):
            angle = self.rng.random() * 6.2831853
            speed = self.rng.uniform(80.0, 240.0)
            vel = pygame.Vector2(speed, 0).rotate_rad(angle)
            p = Particle(
                pos=pygame.Vector2(center),
                vel=vel,
                radius=self.rng.uniform(2.0, 5.0),
                color=color,
                life=0.35,
                ttl=0.35,
            )
            self.particles.append(p)

    def _cue_coin(self, coin_rect: pygame.Rect) -> None:
        if self.cue_shake:
            self._shake_for = max(self._shake_for, 0.10)

        if self.cue_particles:
            self._spawn_particles(coin_rect.center, color=self.palette.particle, count=18)

        if not self.muted:
            self.coin_sfx.play()

    def _cue_hit(self, source_rect: pygame.Rect) -> None:
        if self.cue_flash:
            self.player.flash_for = 0.18

        if self.cue_hitstop:
            self._hitstop_for = max(self._hitstop_for, 0.06)

        if self.cue_shake:
            self._shake_for = max(self._shake_for, 0.18)

        if self.cue_particles:
            self._spawn_particles(self.player.rect.center, color=self.palette.hazard, count=26)
        
        if not self.muted:
            self.hurt_sfx.play()

    def _apply_damage(self, source_rect: pygame.Rect) -> None:
        if self.player.is_invincible:
            return

        self.player.hp -= 1
        self.player.invincible_for = 0.85

        push = pygame.Vector2(self.player.rect.center) - pygame.Vector2(source_rect.center)
        if push.length_squared() == 0:
            push = pygame.Vector2(1, 0)
        push = push.normalize() * 540.0
        self.player.vel.update(push)

        self._cue_hit(source_rect)

        if self.player.hp <= 0:
            self.state = "gameover"

    def update(self, dt: float) -> None:
        if self._shake_for > 0:
            self._shake_for = max(0.0, self._shake_for - dt)

        if self._hitstop_for > 0:
            self._hitstop_for = max(0.0, self._hitstop_for - dt)
            return

        for p in list(self.particles):
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        if self.state != "play":
            return

        move = self._read_move()
        self.player.vel.update(move * self.player.speed)

        speed2 = self.player.vel.length_squared()
        if self.player.is_invincible:
            self.player.set_state("hurt")
        elif speed2 < 1.0:
            self.player.set_state("idle")
        else:
            self.player.set_state("run")

        self._move_player_axis("x", self.player.vel.x * dt)
        self._move_player_axis("y", self.player.vel.y * dt)

        picked = pygame.sprite.spritecollide(self.player, self.coins, dokill=True)
        if picked:
            self.player.score += len(picked)
            self._cue_coin(picked[0].rect)

        for hz in pygame.sprite.spritecollide(self.player, self.hazards, dokill=False):
            self._apply_damage(hz.rect)

        # update and check collisions
        player_pos = pygame.Vector2(self.player.rect.center)
        for enemy in self.enemies:
            was_chasing = enemy.state == "chase"
            enemy.update(dt, player_pos)
            if enemy.state == "chase" and not was_chasing and not self.muted:
                self.alert_sfx.play()
        for enemy in pygame.sprite.spritecollide(self.player, self.enemies, dokill=False):
            self._apply_damage(enemy.rect)

        self.coins.update(dt)
        self.hazards.update(dt)
        self.player.update(dt)

        if len(self.coins) == 0:
            self._reset_level(keep_state=True)
            self.state = "play"

    def _camera_offset(self) -> tuple[int, int]:
        if not self.cue_shake or self._shake_for <= 0:
            return (0, 0)
        strength = _clamp(self._shake_for / 0.18, 0.0, 1.0)
        max_px = 10 * strength
        ox = int(self.rng.uniform(-max_px, max_px))
        oy = int(self.rng.uniform(-max_px, max_px))
        return (ox, oy)

    def draw(self) -> None:
        self.screen.fill(self.palette.bg)

        hud_rect = pygame.Rect(0, 0, self.SCREEN_W, self.HUD_H)
        pygame.draw.rect(self.screen, self.palette.panel, hud_rect)

        cues = f"Cues: [1]flash={'on' if self.cue_flash else 'off'}  [2]shake={'on' if self.cue_shake else 'off'}  [3]hitstop={'on' if self.cue_hitstop else 'off'}  [4]particles={'on' if self.cue_particles else 'off'}"
        self._draw_text(f"HP {self.player.hp}   Score {self.player.score}", (12, 10), self.palette.text)
        self._draw_text(cues, (12, 32), self.palette.subtle)

        if self.muted:
            self._draw_text("MUTED - [M] to unmute", (self.SCREEN_W - 180, 10), self.palette.subtle)
        cam = self._camera_offset()

        pygame.draw.rect(self.screen, self.palette.panel, self.playfield)

        for wall in self.walls:
            pygame.draw.rect(self.screen, wall.color, wall.rect.move(cam))

        for coin in self.coins:
            self.screen.blit(coin.image, coin.rect.move(cam))

        for hz in self.hazards:
            self.screen.blit(hz.image, hz.rect.move(cam))

        for enemy in self.enemies:
            self.screen.blit(enemy.image, enemy.rect.move(cam))

        player_image = self.player.image
        if self.cue_flash and self.player.flash_for > 0:
            player_image = player_image.copy()
            player_image.fill((255, 255, 255, 120), special_flags=pygame.BLEND_RGBA_ADD)
        self.screen.blit(player_image, self.player.rect.move(cam))

        for p in self.particles:
            a = _clamp(p.life / p.ttl, 0.0, 1.0)
            radius = max(1, int(round(p.radius * (0.8 + 0.6 * a))))
            col = pygame.Color(p.color)
            col.a = int(255 * a)
            surf = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, col, (radius + 1, radius + 1), radius)
            self.screen.blit(surf, (p.pos.x - radius + cam[0], p.pos.y - radius + cam[1]))

        if self.debug:
            pygame.draw.rect(self.screen, pygame.Color("#d08770"), self.player.rect.move(cam), 2)
            for coin in self.coins:
                pygame.draw.rect(self.screen, pygame.Color("#ebcb8b"), coin.rect.move(cam), 2)
            for hz in self.hazards:
                pygame.draw.rect(self.screen, pygame.Color("#bf616a"), hz.rect.move(cam), 2)
            for enemy in self.enemies:
                pygame.draw.rect(self.screen, pygame.Color("#b48ead"), enemy.rect.move(cam), 2)
                #detection radius
                pygame.draw.circle(self.screen, pygame.Color("#b48ead"), (int(enemy.pos.x) + cam[0], int(enemy.pos.y) + cam[1]), int(ENEMY_DETECT_DIST), 1)

        if self.state == "title":
            self._draw_centered("Press Space to Start", y=self.playfield.centery, color=self.palette.text)
        elif self.state == "gameover":
            self._draw_centered("Game Over — Press Space", y=self.playfield.centery, color=self.palette.text)

    def _draw_text(self, text: str, pos: tuple[int, int], color: pygame.Color) -> None:
        s = self.font.render(text, True, color)
        self.screen.blit(s, pos)

    def _draw_centered(self, text: str, *, y: int, color: pygame.Color) -> None:
        s = self.big_font.render(text, True, color)
        r = s.get_rect(center=(self.playfield.centerx, y))
        self.screen.blit(s, r)



def _make_coin_frames(color: pygame.Color) -> list[pygame.Surface]:
    frames: list[pygame.Surface] = []

    for i in range(6):
        pulse = 1.0 + 0.08 * (1.0 if i % 2 == 0 else -1.0)
        w = int(round(26 * pulse))
        h = int(round(26 * pulse))

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2
        r = min(cx, cy) - 2

        pygame.draw.circle(surf, color, (cx, cy), r)
        pygame.draw.circle(surf, pygame.Color("#000000"), (cx, cy), r, 2)

        sparkle = pygame.Color("#ffffff")
        sparkle.a = 180
        pygame.draw.circle(surf, sparkle, (cx - r // 3, cy - r // 3), max(1, r // 5))

        frames.append(surf)

    return frames


def _make_hazard_surface(size: int, color: pygame.Color) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    pts = [
        (cx, 2),
        (size - 2, cy),
        (cx, size - 2),
        (2, cy),
    ]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, pygame.Color("#000000"), pts, 2)
    return surf


def _make_player_anims(color: pygame.Color) -> dict[str, Animation]:
    idle = [_draw_player_frame(color, leg_phase=0, eye_open=True)]

    run_frames = [
        _draw_player_frame(color, leg_phase=0, eye_open=True),
        _draw_player_frame(color, leg_phase=1, eye_open=True),
        _draw_player_frame(color, leg_phase=2, eye_open=True),
        _draw_player_frame(color, leg_phase=3, eye_open=True),
    ]

    hurt_frames = [
        _draw_player_frame(pygame.Color("#d08770"), leg_phase=0, eye_open=False),
        _draw_player_frame(pygame.Color("#bf616a"), leg_phase=2, eye_open=False),
    ]

    return {
        "idle": Animation(idle, fps=1.0),
        "run": Animation(run_frames, fps=10.0),
        "hurt": Animation(hurt_frames, fps=8.0),
    }


def _draw_player_frame(color: pygame.Color, *, leg_phase: int, eye_open: bool) -> pygame.Surface:
    w, h = 44, 44
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # Body
    body = pygame.Rect(0, 0, 24, 26)
    body.center = (w // 2, h // 2 + 4)
    pygame.draw.rect(surf, color, body, border_radius=8)
    pygame.draw.rect(surf, pygame.Color("#000000"), body, 2, border_radius=8)

    # Head
    head_center = (w // 2, h // 2 - 10)
    pygame.draw.circle(surf, color, head_center, 10)
    pygame.draw.circle(surf, pygame.Color("#000000"), head_center, 10, 2)

    # Eyes
    eye = pygame.Color("#2e3440")
    if eye_open:
        pygame.draw.circle(surf, eye, (head_center[0] - 3, head_center[1] - 1), 2)
        pygame.draw.circle(surf, eye, (head_center[0] + 3, head_center[1] - 1), 2)
    else:
        pygame.draw.line(surf, eye, (head_center[0] - 5, head_center[1] - 1), (head_center[0] - 1, head_center[1] - 1), 2)
        pygame.draw.line(surf, eye, (head_center[0] + 1, head_center[1] - 1), (head_center[0] + 5, head_center[1] - 1), 2)

    # Legs (simple alternating phase)
    leg_y = body.bottom + 2
    dx = 6
    phase = leg_phase % 4
    left_off = (-dx, 4) if phase in {0, 3} else (-dx, 1)
    right_off = (dx, 4) if phase in {1, 2} else (dx,  1)

    pygame.draw.line(surf, pygame.Color("#2e3440"), (w // 2 - 6, leg_y), (w // 2 - 6 + left_off[0]  // 3, leg_y + left_off[1]),  4)
    pygame.draw.line(surf, pygame.Color("#2e3440"), (w // 2 + 6, leg_y), (w // 2 + 6 + right_off[0] // 3, leg_y + right_off[1]), 4)

    # Arms
    arm_y = body.top + 10
    pygame.draw.line(surf, pygame.Color("#2e3440"), (body.left + 3, arm_y), (body.left  - 6, arm_y + 3), 4)
    pygame.draw.line(surf, pygame.Color("#2e3440"), (body.right - 3, arm_y), (body.right + 6, arm_y + 3), 4)

    return surf



def _make_enemy_anims(color: pygame.Color) -> dict[str, Animation]:
    # walk (slow leg cycle) and chase (fast leg cycle, angry eyebrows)
    walk_frames = [
        _draw_enemy_frame(color, leg_phase=p, angry=False) for p in range(4)
    ]
    chase_frames = [
        _draw_enemy_frame(color, leg_phase=p, angry=True) for p in range(4)
    ]
    return {
        "walk":  Animation(walk_frames,  fps=6.0),
        "chase": Animation(chase_frames, fps=12.0),
    }


def _draw_enemy_frame(color: pygame.Color, *, leg_phase: int, angry: bool) -> pygame.Surface:
    w, h = 40, 42
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    outline = pygame.Color("#1a1a2e")

    # Body 
    body = pygame.Rect(0, 0, 28, 22)
    body.center = (w // 2, h // 2 + 6)
    pygame.draw.rect(surf, color, body, border_radius=6)
    pygame.draw.rect(surf, outline, body, 2, border_radius=6)

    # Head
    hc = (w // 2, h // 2 - 8)
    pygame.draw.circle(surf, color, hc, 11)
    pygame.draw.circle(surf, outline, hc, 11, 2)

    # Eyes
    eye_col = pygame.Color("#2e3440")
    pygame.draw.circle(surf, eye_col, (hc[0] - 4, hc[1]), 2)
    pygame.draw.circle(surf, eye_col, (hc[0] + 4, hc[1]), 2)

    # Angry brows (angled) when chasing
    brow_col = outline
    if angry:
        pygame.draw.line(surf, brow_col, (hc[0] - 7, hc[1] - 6), (hc[0] - 1, hc[1] - 4), 2)
        pygame.draw.line(surf, brow_col, (hc[0] + 7, hc[1] - 6), (hc[0] + 1, hc[1] - 4), 2)
    else:
        # flat brows for non-chasing state
        pygame.draw.line(surf, brow_col, (hc[0] - 7, hc[1] - 5), (hc[0] - 1, hc[1] - 5), 2)
        pygame.draw.line(surf, brow_col, (hc[0] + 1, hc[1] - 5), (hc[0] + 7, hc[1] - 5), 2)

    # Legs
    leg_y = body.bottom + 1
    phase     = leg_phase % 4
    left_off  = (-4, 4) if phase in {0, 3} else (-4, 1)
    right_off = ( 4, 4) if phase in {1, 2} else ( 4, 1)
    pygame.draw.line(surf, outline, (w // 2 - 6, leg_y), (w // 2 - 6 + left_off[0]  // 2, leg_y + left_off[1]),  4)
    pygame.draw.line(surf, outline, (w // 2 + 6, leg_y), (w // 2 + 6 + right_off[0] // 2, leg_y + right_off[1]), 4)

    return surf
