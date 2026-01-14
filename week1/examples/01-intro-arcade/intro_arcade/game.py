from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

import pygame


@dataclass
class Colors:
    bg: tuple[int, int, int] = (22, 24, 28)
    panel: tuple[int, int, int] = (34, 38, 46)
    text: tuple[int, int, int] = (236, 239, 244)

    player: tuple[int, int, int] = (136, 192, 208)
    enemy: tuple[int, int, int] = (191, 97, 106)
    coin: tuple[int, int, int] = (235, 203, 139)


COLORS = Colors()


class Game:
    def __init__(self) -> None:
        self.fps = 60
        self.w = 960
        self.h = 540
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 48)

        self.save_path = Path(__file__).resolve().parent.parent / "save.json"
        self.high_score = self._load_high_score()

        self.state: str = "title"  # title | playing | gameover
        self._reset_run()

    def _load_high_score(self) -> int:
        if not self.save_path.exists():
            return 0
        try:
            raw = json.loads(self.save_path.read_text(encoding="utf-8"))
            return int(raw.get("high_score", 0))
        except Exception:
            return 0

    def _save_high_score(self) -> None:
        self.save_path.write_text(
            json.dumps({"high_score": int(self.high_score)}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _reset_run(self) -> None:
        self.player = pygame.Rect(self.w // 2 - 16, self.h // 2 - 16, 32, 32)
        self.player_v = pygame.Vector2(0, 0)

        self.score = 0
        self.alive_time = 0.0

        self.enemy_rects: list[pygame.Rect] = []
        self.enemy_vs: list[pygame.Vector2] = []
        for _ in range(3):
            r = pygame.Rect(random.randrange(40, self.w - 40), random.randrange(80, self.h - 40), 36, 36)
            v = pygame.Vector2(random.choice([-1, 1]) * 220, random.choice([-1, 1]) * 180)
            self.enemy_rects.append(r)
            self.enemy_vs.append(v)

        self.coin = self._spawn_coin()

    def _spawn_coin(self) -> pygame.Rect:
        # Keep coin away from top HUD area.
        return pygame.Rect(random.randrange(20, self.w - 20), random.randrange(90, self.h - 20), 18, 18)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

            if event.key == pygame.K_RETURN:
                if self.state in ("title", "gameover"):
                    self._reset_run()
                    self.state = "playing"

    def update(self, dt: float) -> None:
        if self.state != "playing":
            return

        self.alive_time += dt

        # Input: map keys -> direction.
        keys = pygame.key.get_pressed()
        input_x = 0.0
        input_y = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            input_x -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            input_x += 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            input_y -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            input_y += 1.0

        # Movement: velocity integrates into position; dt makes it frame-rate independent.
        speed = 360.0
        self.player_v.x = input_x * speed
        self.player_v.y = input_y * speed

        self.player.x += int(self.player_v.x * dt)
        self.player.y += int(self.player_v.y * dt)
        self.player.clamp_ip(pygame.Rect(0, 60, self.w, self.h - 60))

        # Enemies: bounce around the playfield.
        bounds = pygame.Rect(0, 60, self.w, self.h - 60)
        for i, r in enumerate(self.enemy_rects):
            v = self.enemy_vs[i]
            r.x += int(v.x * dt)
            r.y += int(v.y * dt)
            if r.left < bounds.left:
                r.left = bounds.left
                v.x *= -1
            if r.right > bounds.right:
                r.right = bounds.right
                v.x *= -1
            if r.top < bounds.top:
                r.top = bounds.top
                v.y *= -1
            if r.bottom > bounds.bottom:
                r.bottom = bounds.bottom
                v.y *= -1

        # Collision: player with coin.
        if self.player.colliderect(self.coin):
            self.score += 1
            self.coin = self._spawn_coin()

        # Collision: player with enemies.
        if self.player.collidelist(self.enemy_rects) != -1:
            self.state = "gameover"
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()

    def draw(self) -> None:
        self.screen.fill(COLORS.bg)

        if self.state == "title":
            self._draw_title()
        elif self.state == "playing":
            self._draw_playing()
        else:
            self._draw_gameover()

    def _draw_hud(self) -> None:
        panel = pygame.Rect(12, 12, 420, 40)
        pygame.draw.rect(self.screen, COLORS.panel, panel, border_radius=10)

        text = f"Score: {self.score}    High: {self.high_score}"
        surf = self.font.render(text, True, COLORS.text)
        self.screen.blit(surf, (panel.x + 12, panel.y + 12))

    def _draw_playing(self) -> None:
        self._draw_hud()

        pygame.draw.rect(self.screen, COLORS.coin, self.coin, border_radius=7)
        for r in self.enemy_rects:
            pygame.draw.rect(self.screen, COLORS.enemy, r, border_radius=8)
        pygame.draw.rect(self.screen, COLORS.player, self.player, border_radius=8)

    def _draw_title(self) -> None:
        title = self.big_font.render("Intro Arcade", True, COLORS.text)
        hint = self.font.render("Move with arrows/WASD.  Avoid red.  Collect gold.", True, COLORS.text)
        hint2 = self.font.render("Press Enter to start.  Esc to quit.", True, COLORS.text)

        self.screen.blit(title, (self.w / 2 - title.get_width() / 2, 190))
        self.screen.blit(hint, (self.w / 2 - hint.get_width() / 2, 250))
        self.screen.blit(hint2, (self.w / 2 - hint2.get_width() / 2, 280))

    def _draw_gameover(self) -> None:
        title = self.big_font.render("Game Over", True, COLORS.text)
        msg = self.font.render(f"Score: {self.score}   High: {self.high_score}", True, COLORS.text)
        hint = self.font.render("Press Enter to play again.  Esc to quit.", True, COLORS.text)

        self.screen.blit(title, (self.w / 2 - title.get_width() / 2, 190))
        self.screen.blit(msg, (self.w / 2 - msg.get_width() / 2, 250))
        self.screen.blit(hint, (self.w / 2 - hint.get_width() / 2, 280))
