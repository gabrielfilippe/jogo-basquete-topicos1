"""Loop e cena principal do jogo de lances livres."""

from __future__ import annotations

import math
import sys

import pygame

from . import settings


class FreeThrowGame:
    """Classe principal que controla inicializacao, update e render."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(settings.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 24)
        self.small_font = pygame.font.SysFont("consolas", 18)
        self.running = True
        self.static_background = self._build_static_background()

        self.ball_pos = pygame.Vector2(settings.BALL_START_X, settings.BALL_START_Y)
        self.ball_vel = pygame.Vector2(0, 0)
        self.ball_in_flight = False
        self.shot_scored = False
        self.shot_time = 0.0
        self.floor_bounces = 0

        self.angle_deg = settings.ANGLE_DEFAULT
        self.power = settings.POWER_DEFAULT

        self.score = 0
        self.attempts_used = 0

        self.status_text = ""
        self.status_color = settings.COLOR_TEXT
        self.status_timer = 0.0

        self.feedback_flash_timer = 0.0
        self.feedback_flash_color = settings.COLOR_SUCCESS

    def run(self) -> None:
        """Executa o loop principal."""
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._try_launch_ball()
                if event.key == pygame.K_r:
                    self._reset_ball()
                if event.key == pygame.K_n:
                    self._new_session()

    def _update(self, dt: float) -> None:
        self._update_status_timer(dt)
        self._update_feedback_flash_timer(dt)
        self._update_aim_controls()

        if not self.ball_in_flight:
            return

        self.shot_time += dt
        prev_pos = pygame.Vector2(self.ball_pos)
        self.ball_vel.y += settings.GRAVITY * dt
        self.ball_pos += self.ball_vel * dt

        self._resolve_hoop_collisions()
        self._resolve_floor_collision()
        self._check_made_basket(prev_pos)

        if self._should_end_shot():
            self._finalize_shot(auto_miss=not self.shot_scored)
            return

        if self._is_ball_out_of_bounds():
            self._finalize_shot(auto_miss=not self.shot_scored)

    def _update_aim_controls(self) -> None:
        if self.ball_in_flight:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.angle_deg = min(settings.ANGLE_MAX, self.angle_deg + settings.ANGLE_STEP)
        if keys[pygame.K_DOWN]:
            self.angle_deg = max(settings.ANGLE_MIN, self.angle_deg - settings.ANGLE_STEP)
        if keys[pygame.K_RIGHT]:
            self.power = min(settings.POWER_MAX, self.power + settings.POWER_STEP)
        if keys[pygame.K_LEFT]:
            self.power = max(settings.POWER_MIN, self.power - settings.POWER_STEP)

    def _try_launch_ball(self) -> None:
        if self.ball_in_flight:
            return
        if self.attempts_used >= settings.MAX_ATTEMPTS:
            self._set_status("Sem tentativas. Pressione N para novo jogo.", settings.COLOR_ACCENT, 2.0)
            return

        angle_rad = math.radians(self.angle_deg)
        self.ball_vel.x = math.cos(angle_rad) * self.power
        self.ball_vel.y = -math.sin(angle_rad) * self.power
        self.ball_in_flight = True
        self.shot_scored = False
        self.shot_time = 0.0
        self.floor_bounces = 0
        self.attempts_used += 1

    def _reset_ball(self) -> None:
        self.ball_pos.update(settings.BALL_START_X, settings.BALL_START_Y)
        self.ball_vel.update(0, 0)
        self.ball_in_flight = False
        self.shot_scored = False
        self.shot_time = 0.0
        self.floor_bounces = 0

    def _new_session(self) -> None:
        self.score = 0
        self.attempts_used = 0
        self._reset_ball()
        self._set_status("Novo jogo iniciado.", settings.COLOR_ACCENT, 1.2)

    def _update_status_timer(self, dt: float) -> None:
        if self.status_timer <= 0.0:
            return
        self.status_timer = max(0.0, self.status_timer - dt)

    def _update_feedback_flash_timer(self, dt: float) -> None:
        if self.feedback_flash_timer <= 0.0:
            return
        self.feedback_flash_timer = max(0.0, self.feedback_flash_timer - dt)

    def _trigger_feedback_flash(self, color: tuple[int, int, int]) -> None:
        self.feedback_flash_color = color
        self.feedback_flash_timer = settings.FEEDBACK_FLASH_TIME

    def _set_status(self, text: str, color: tuple[int, int, int], duration: float) -> None:
        self.status_text = text
        self.status_color = color
        self.status_timer = duration

    def _resolve_hoop_collisions(self) -> None:
        left_rim = pygame.Vector2(settings.RIM_LEFT_X, settings.RIM_Y)
        right_rim = pygame.Vector2(settings.RIM_RIGHT_X, settings.RIM_Y)

        self._resolve_circle_collision(left_rim, settings.RIM_NODE_RADIUS, settings.RIM_BOUNCE)
        self._resolve_circle_collision(right_rim, settings.RIM_NODE_RADIUS, settings.RIM_BOUNCE)
        self._resolve_backboard_collision()

    def _resolve_floor_collision(self) -> None:
        floor_level = settings.FLOOR_Y - settings.BALL_RADIUS
        if self.ball_pos.y < floor_level:
            return

        if self.ball_vel.y <= 0:
            return

        self.ball_pos.y = floor_level
        self.ball_vel.y = -abs(self.ball_vel.y) * settings.FLOOR_BOUNCE
        self.ball_vel.x *= settings.FLOOR_FRICTION
        self.floor_bounces += 1

    def _resolve_circle_collision(
        self,
        center: pygame.Vector2,
        radius: float,
        bounce: float,
    ) -> None:
        offset = self.ball_pos - center
        distance = offset.length()
        min_distance = settings.BALL_RADIUS + radius

        if distance <= 0.0001 or distance >= min_distance:
            return

        normal = offset / distance
        self.ball_pos = center + normal * min_distance

        speed_on_normal = self.ball_vel.dot(normal)
        if speed_on_normal < 0:
            self.ball_vel -= (1.0 + bounce) * speed_on_normal * normal

    def _resolve_backboard_collision(self) -> None:
        board = pygame.Rect(
            settings.BACKBOARD_X,
            settings.BACKBOARD_Y,
            settings.BACKBOARD_WIDTH,
            settings.BACKBOARD_HEIGHT,
        )

        expanded = board.inflate(settings.BALL_RADIUS * 2, settings.BALL_RADIUS * 2)
        if not expanded.collidepoint(self.ball_pos.x, self.ball_pos.y):
            return

        dist_left = abs(self.ball_pos.x - expanded.left)
        dist_right = abs(expanded.right - self.ball_pos.x)
        dist_top = abs(self.ball_pos.y - expanded.top)
        dist_bottom = abs(expanded.bottom - self.ball_pos.y)

        min_dist = min(dist_left, dist_right, dist_top, dist_bottom)

        if min_dist == dist_left:
            self.ball_pos.x = expanded.left
            self.ball_vel.x = -abs(self.ball_vel.x) * settings.BACKBOARD_BOUNCE
        elif min_dist == dist_right:
            self.ball_pos.x = expanded.right
            self.ball_vel.x = abs(self.ball_vel.x) * settings.BACKBOARD_BOUNCE
        elif min_dist == dist_top:
            self.ball_pos.y = expanded.top
            self.ball_vel.y = -abs(self.ball_vel.y) * settings.BACKBOARD_BOUNCE
        else:
            self.ball_pos.y = expanded.bottom
            self.ball_vel.y = abs(self.ball_vel.y) * settings.BACKBOARD_BOUNCE

    def _check_made_basket(self, prev_pos: pygame.Vector2) -> None:
        if self.shot_scored:
            return
        if self.ball_vel.y <= 0:
            return
        if prev_pos.y >= settings.RIM_Y or self.ball_pos.y < settings.RIM_Y:
            return

        dy = self.ball_pos.y - prev_pos.y
        if abs(dy) <= 0.0001:
            return

        t = (settings.RIM_Y - prev_pos.y) / dy
        t = max(0.0, min(1.0, t))
        cross_x = prev_pos.x + (self.ball_pos.x - prev_pos.x) * t

        inner_left = settings.RIM_LEFT_X + settings.BALL_RADIUS * 0.35
        inner_right = settings.RIM_RIGHT_X - settings.BALL_RADIUS * 0.35
        if inner_left <= cross_x <= inner_right:
            self.shot_scored = True
            self.score += 1
            self._set_status("Cesta!", settings.COLOR_ACCENT, 1.5)
            self._trigger_feedback_flash(settings.COLOR_SUCCESS)

    def _should_end_shot(self) -> bool:
        if not self.ball_in_flight:
            return False
        if self.shot_time >= settings.SHOT_MAX_TIME:
            return True
        if self.floor_bounces >= settings.MAX_FLOOR_BOUNCES:
            return True

        speed = self.ball_vel.length()
        floor_contact = self.ball_pos.y >= settings.FLOOR_Y - settings.BALL_RADIUS - 1
        if floor_contact and speed <= settings.SHOT_STOP_SPEED:
            return True
        return False

    def _finalize_shot(self, auto_miss: bool) -> None:
        if auto_miss:
            self._set_status("Errou o lance.", settings.COLOR_FAILURE, 1.6)
            self._trigger_feedback_flash(settings.COLOR_FAILURE)
        self._reset_ball()

    def _is_ball_out_of_bounds(self) -> bool:
        radius = settings.BALL_RADIUS
        if self.ball_pos.x < -radius:
            return True
        if self.ball_pos.x > settings.SCREEN_WIDTH + radius:
            return True
        if self.ball_pos.y > settings.SCREEN_HEIGHT + radius:
            return True
        return False

    def _draw(self) -> None:
        self.screen.blit(self.static_background, (0, 0))
        self._draw_court()
        self._draw_aim_preview()
        self._draw_ball()
        self._draw_feedback_flash()
        self._draw_player_silhouette()
        self._draw_ui()
        self._draw_round_end_overlay()

    def _build_static_background(self) -> pygame.Surface:
        surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self._draw_sky_gradient(surface)
        self._draw_sun_glow(surface)
        self._draw_city_silhouette(surface)
        self._draw_trees(surface)
        self._draw_fence(surface)
        return surface

    def _draw_sky_gradient(self, surface: pygame.Surface) -> None:
        horizon = 250
        for y in range(settings.SCREEN_HEIGHT):
            if y <= horizon:
                ratio = y / max(1, horizon)
                if ratio < 0.65:
                    local = ratio / 0.65
                    color = self._lerp_color(settings.COLOR_SKY_TOP, settings.COLOR_SKY_MID, local)
                else:
                    local = (ratio - 0.65) / 0.35
                    color = self._lerp_color(settings.COLOR_SKY_MID, settings.COLOR_SKY_HORIZON, local)
            else:
                ground_ratio = (y - horizon) / max(1, settings.SCREEN_HEIGHT - horizon)
                color = self._lerp_color((64, 79, 86), settings.COLOR_BG, ground_ratio)
            pygame.draw.line(surface, color, (0, y), (settings.SCREEN_WIDTH, y))

    def _draw_sun_glow(self, surface: pygame.Surface) -> None:
        glow = pygame.Surface((360, 220), pygame.SRCALPHA)
        center = (100, 120)
        for radius, alpha in ((120, 80), (85, 110), (55, 145), (30, 185)):
            pygame.draw.circle(glow, (255, 210, 130, alpha), center, radius)
        surface.blit(glow, (0, 105))

    def _draw_city_silhouette(self, surface: pygame.Surface) -> None:
        buildings = [
            pygame.Rect(355, 183, 56, 84),
            pygame.Rect(426, 169, 46, 98),
            pygame.Rect(482, 176, 58, 91),
            pygame.Rect(552, 195, 38, 72),
            pygame.Rect(602, 188, 52, 79),
        ]
        for rect in buildings:
            pygame.draw.rect(surface, settings.COLOR_CITY, rect)

        hill_points = [
            (310, 267),
            (420, 240),
            (530, 246),
            (620, 228),
            (760, 241),
            (900, 267),
            (310, 267),
        ]
        pygame.draw.polygon(surface, (66, 72, 82), hill_points)

    def _draw_trees(self, surface: pygame.Surface) -> None:
        trees = [
            ((72, 213), 52),
            ((160, 204), 62),
            ((780, 212), 48),
            ((862, 206), 58),
        ]
        for center, radius in trees:
            pygame.draw.circle(surface, settings.COLOR_TREE_DARK, center, radius)
            pygame.draw.circle(
                surface,
                settings.COLOR_TREE_LIGHT,
                (center[0] - 10, center[1] - 6),
                int(radius * 0.62),
            )
            trunk = pygame.Rect(center[0] - 6, center[1] + radius - 8, 12, 28)
            pygame.draw.rect(surface, (62, 48, 36), trunk)

    def _draw_fence(self, surface: pygame.Surface) -> None:
        fence_rect = pygame.Rect(48, 150, 836, 175)
        pygame.draw.rect(surface, settings.COLOR_FENCE, fence_rect, width=3)

        for x in range(fence_rect.left + 18, fence_rect.right, 18):
            pygame.draw.line(
                surface,
                (88, 84, 97),
                (x, fence_rect.top),
                (x - 22, fence_rect.bottom),
                1,
            )
            pygame.draw.line(
                surface,
                (88, 84, 97),
                (x, fence_rect.top),
                (x + 22, fence_rect.bottom),
                1,
            )

        for x in (265, 490, 700):
            pygame.draw.line(surface, settings.COLOR_FENCE, (x, 150), (x, 325), 4)

    def _lerp_color(
        self,
        start: tuple[int, int, int],
        end: tuple[int, int, int],
        ratio: float,
    ) -> tuple[int, int, int]:
        ratio = max(0.0, min(1.0, ratio))
        return (
            int(start[0] + (end[0] - start[0]) * ratio),
            int(start[1] + (end[1] - start[1]) * ratio),
            int(start[2] + (end[2] - start[2]) * ratio),
        )

    def _court_point(
        self,
        u: float,
        d: float,
        far_left: tuple[float, float],
        far_right: tuple[float, float],
        near_left: tuple[float, float],
        near_right: tuple[float, float],
    ) -> tuple[int, int]:
        """Converte coordenadas de quadra (u,d) para tela com perspectiva."""
        d = max(0.0, min(1.0, d))
        u = max(0.0, min(1.0, u))

        left_x = far_left[0] + (near_left[0] - far_left[0]) * d
        left_y = far_left[1] + (near_left[1] - far_left[1]) * d
        right_x = far_right[0] + (near_right[0] - far_right[0]) * d
        right_y = far_right[1] + (near_right[1] - far_right[1]) * d

        px = left_x + (right_x - left_x) * u
        py = left_y + (right_y - left_y) * u
        return (int(px), int(py))

    def _draw_court(self) -> None:
        far_left = (118.0, 334.0)
        far_right = (892.0, 322.0)
        near_left = (34.0, 548.0)
        near_right = (978.0, 529.0)

        court_polygon = [
            self._court_point(0.0, 0.0, far_left, far_right, near_left, near_right),
            self._court_point(1.0, 0.0, far_left, far_right, near_left, near_right),
            self._court_point(1.0, 1.0, far_left, far_right, near_left, near_right),
            self._court_point(0.0, 1.0, far_left, far_right, near_left, near_right),
        ]

        pygame.draw.polygon(self.screen, settings.COLOR_COURT, court_polygon)
        pygame.draw.polygon(self.screen, (101, 119, 87), court_polygon, width=4)

        # Linha central sutil para reforcar leitura de perspectiva da quadra.
        mid_top = self._court_point(0.50, 0.06, far_left, far_right, near_left, near_right)
        mid_bottom = self._court_point(0.50, 0.94, far_left, far_right, near_left, near_right)
        pygame.draw.line(self.screen, settings.COLOR_LINES, mid_top, mid_bottom, 2)

        # Garrafao em perspectiva, alinhado com o aro do lado direito.
        key_left_u = 0.63
        key_right_u = 0.90
        key_top_d = 0.26
        key_bottom_d = 0.74

        paint_polygon = [
            self._court_point(key_left_u, key_top_d, far_left, far_right, near_left, near_right),
            self._court_point(key_right_u, key_top_d, far_left, far_right, near_left, near_right),
            self._court_point(key_right_u, key_bottom_d, far_left, far_right, near_left, near_right),
            self._court_point(key_left_u, key_bottom_d, far_left, far_right, near_left, near_right),
        ]
        pygame.draw.polygon(self.screen, settings.COLOR_PAINT, paint_polygon)
        pygame.draw.polygon(self.screen, settings.COLOR_LINES, paint_polygon, width=3)

        # Linha de lance livre (borda esquerda do garrafao).
        free_throw_top = self._court_point(key_left_u, key_top_d, far_left, far_right, near_left, near_right)
        free_throw_bottom = self._court_point(key_left_u, key_bottom_d, far_left, far_right, near_left, near_right)
        pygame.draw.line(self.screen, settings.COLOR_LINES, free_throw_top, free_throw_bottom, 3)

        # Arco do lance livre (externo ao garrafao).
        free_throw_arc: list[tuple[int, int]] = []
        for i in range(30):
            t = i / 29
            angle = -math.pi / 2 + t * math.pi
            local_u = key_left_u - 0.09 * math.cos(angle)
            local_d = 0.50 + 0.19 * math.sin(angle)
            free_throw_arc.append(
                self._court_point(local_u, local_d, far_left, far_right, near_left, near_right)
            )
        pygame.draw.lines(self.screen, settings.COLOR_LINES, False, free_throw_arc, 3)

        # Arco restrito perto da cesta.
        restricted_arc: list[tuple[int, int]] = []
        for i in range(24):
            t = i / 23
            angle = -math.pi / 2 + t * math.pi
            local_u = key_right_u - 0.045 * math.cos(angle)
            local_d = 0.50 + 0.12 * math.sin(angle)
            restricted_arc.append(
                self._court_point(local_u, local_d, far_left, far_right, near_left, near_right)
            )
        pygame.draw.lines(self.screen, settings.COLOR_LINES, False, restricted_arc, 2)

        # Linha curva grande no lado esquerdo (perimetro), seguindo a referencia.
        left_perimeter_arc: list[tuple[int, int]] = []
        for i in range(32):
            t = i / 31
            angle = math.pi * (0.18 + 0.64 * t)
            local_u = 0.12 + 0.23 * math.cos(angle)
            local_d = 0.90 + 0.30 * math.sin(angle)
            left_perimeter_arc.append(
                self._court_point(local_u, local_d, far_left, far_right, near_left, near_right)
            )
        pygame.draw.lines(self.screen, settings.COLOR_LINES, False, left_perimeter_arc, 4)

        # Sombra alongada no piso para reforcar perspectiva.
        shadow = pygame.Surface((settings.SCREEN_WIDTH, 130), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (*settings.COLOR_SHADOW, 88), (120, 30, 760, 72))
        self.screen.blit(shadow, (0, 430))

        # Linha do piso usada na fisica, integrada ao desenho.
        pygame.draw.line(
            self.screen,
            settings.COLOR_LINES,
            (int(near_left[0]), settings.FLOOR_Y),
            (int(near_right[0]), settings.FLOOR_Y - 14),
            2,
        )

        self._draw_hoop()

    def _draw_hoop(self) -> None:
        board_rect = pygame.Rect(
            settings.BACKBOARD_X,
            settings.BACKBOARD_Y,
            settings.BACKBOARD_WIDTH,
            settings.BACKBOARD_HEIGHT,
        )
        pygame.draw.rect(self.screen, settings.COLOR_BOARD, board_rect, border_radius=2)
        pygame.draw.rect(self.screen, (132, 148, 166), board_rect, width=2, border_radius=2)

        left_rim = (settings.RIM_LEFT_X, settings.RIM_Y)
        right_rim = (settings.RIM_RIGHT_X, settings.RIM_Y)
        pygame.draw.circle(self.screen, settings.COLOR_ACCENT, left_rim, settings.RIM_NODE_RADIUS)
        pygame.draw.circle(self.screen, settings.COLOR_ACCENT, right_rim, settings.RIM_NODE_RADIUS)
        pygame.draw.line(self.screen, settings.COLOR_ACCENT, left_rim, right_rim, 3)

        # Rede simplificada apenas para referencia visual da zona de cesta.
        net_bottom_y = settings.RIM_Y + 26
        pygame.draw.line(
            self.screen,
            settings.COLOR_LINES,
            (settings.RIM_LEFT_X + 2, settings.RIM_Y + 2),
            (settings.RIM_LEFT_X + 6, net_bottom_y),
            2,
        )
        pygame.draw.line(
            self.screen,
            settings.COLOR_LINES,
            (settings.RIM_RIGHT_X - 2, settings.RIM_Y + 2),
            (settings.RIM_RIGHT_X - 6, net_bottom_y),
            2,
        )
        pygame.draw.line(
            self.screen,
            settings.COLOR_LINES,
            (settings.RIM_LEFT_X + 6, net_bottom_y),
            (settings.RIM_RIGHT_X - 6, net_bottom_y),
            2,
        )

    def _draw_player_silhouette(self) -> None:
        # Silhueta simples para aproximar a composicao da cena de referencia.
        base_x = settings.BALL_START_X - 56
        base_y = 454

        pygame.draw.ellipse(self.screen, (26, 34, 45), (base_x - 10, base_y + 30, 115, 25))
        pygame.draw.circle(self.screen, (38, 44, 59), (base_x + 54, base_y - 78), 14)

        body_points = [
            (base_x + 38, base_y - 66),
            (base_x + 66, base_y - 53),
            (base_x + 74, base_y - 2),
            (base_x + 30, base_y + 8),
        ]
        pygame.draw.polygon(self.screen, (44, 49, 65), body_points)

        arm_points = [
            (base_x + 36, base_y - 49),
            (base_x + 22, base_y - 35),
            (base_x + 18, base_y - 6),
            (base_x + 33, base_y - 2),
            (base_x + 41, base_y - 29),
        ]
        pygame.draw.polygon(self.screen, (44, 49, 65), arm_points)

        pygame.draw.polygon(
            self.screen,
            (37, 43, 58),
            [(base_x + 42, base_y + 5), (base_x + 31, base_y + 59), (base_x + 50, base_y + 60), (base_x + 61, base_y + 9)],
        )
        pygame.draw.polygon(
            self.screen,
            (33, 39, 52),
            [(base_x + 60, base_y + 6), (base_x + 74, base_y + 62), (base_x + 94, base_y + 60), (base_x + 72, base_y + 4)],
        )

    def _draw_ball(self) -> None:
        pygame.draw.circle(
            self.screen,
            settings.COLOR_BALL,
            (int(self.ball_pos.x), int(self.ball_pos.y)),
            settings.BALL_RADIUS,
        )
        pygame.draw.circle(
            self.screen,
            settings.COLOR_LINES,
            (int(self.ball_pos.x), int(self.ball_pos.y)),
            settings.BALL_RADIUS,
            width=2,
        )

    def _draw_feedback_flash(self) -> None:
        if self.feedback_flash_timer <= 0.0:
            return

        ratio = self.feedback_flash_timer / settings.FEEDBACK_FLASH_TIME
        alpha = int(170 * ratio)
        radius = int(44 + 20 * (1.0 - ratio))

        flash_surface = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        color = (*self.feedback_flash_color, alpha)
        center = ((settings.RIM_LEFT_X + settings.RIM_RIGHT_X) // 2, settings.RIM_Y + 2)
        pygame.draw.circle(flash_surface, color, center, radius, width=7)
        self.screen.blit(flash_surface, (0, 0))

    def _draw_aim_preview(self) -> None:
        if self.ball_in_flight:
            return

        angle_rad = math.radians(self.angle_deg)
        direction = pygame.Vector2(math.cos(angle_rad), -math.sin(angle_rad))

        start = self.ball_pos
        end = start + direction * 80
        pygame.draw.line(self.screen, settings.COLOR_ACCENT, start, end, 3)

        # Pontos da trajetoria aproximada para facilitar calibracao do arremesso.
        sim_pos = pygame.Vector2(self.ball_pos)
        sim_vel = direction * self.power
        step_dt = 0.08
        for _ in range(14):
            sim_vel.y += settings.GRAVITY * step_dt
            sim_pos += sim_vel * step_dt
            pygame.draw.circle(self.screen, settings.COLOR_LINES, sim_pos, 3)

    def _draw_ui(self) -> None:
        message = "Setas: angulo/forca | ESPACO: arremessar | R: resetar bola | N: novo jogo"
        text_surface = self.font.render(message, True, settings.COLOR_TEXT)
        self.screen.blit(text_surface, (24, 24))

        stats = f"Angulo: {self.angle_deg:.1f} deg  |  Forca: {self.power:.0f}"
        stats_surface = self.small_font.render(stats, True, settings.COLOR_TEXT)
        self.screen.blit(stats_surface, (24, 58))

        attempts_left = settings.MAX_ATTEMPTS - self.attempts_used
        score_text = f"Placar: {self.score}  |  Tentativas: {self.attempts_used}/{settings.MAX_ATTEMPTS}"
        score_surface = self.small_font.render(score_text, True, settings.COLOR_TEXT)
        self.screen.blit(score_surface, (24, 86))

        if not self.ball_in_flight:
            if attempts_left > 0:
                hint = "Ajuste e pressione ESPACO para lancar"
            else:
                hint = "Fim das tentativas. Pressione N para recomecar"
            hint_surface = self.small_font.render(hint, True, settings.COLOR_ACCENT)
            self.screen.blit(hint_surface, (24, 114))

        if self.status_timer > 0.0:
            status_surface = self.font.render(self.status_text, True, self.status_color)
            status_x = settings.SCREEN_WIDTH // 2 - status_surface.get_width() // 2
            self.screen.blit(status_surface, (status_x, 150))

    def _draw_round_end_overlay(self) -> None:
        if self.attempts_used < settings.MAX_ATTEMPTS:
            return

        if self.ball_in_flight:
            return

        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 14, 22, 160))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("Fim da Rodada", True, settings.COLOR_TEXT)
        title_x = settings.SCREEN_WIDTH // 2 - title.get_width() // 2
        self.screen.blit(title, (title_x, 220))

        accuracy = (self.score / settings.MAX_ATTEMPTS) * 100.0
        result_text = f"Aproveitamento: {self.score}/{settings.MAX_ATTEMPTS} ({accuracy:.0f}%)"
        result_surface = self.small_font.render(result_text, True, settings.COLOR_ACCENT)
        result_x = settings.SCREEN_WIDTH // 2 - result_surface.get_width() // 2
        self.screen.blit(result_surface, (result_x, 258))

        hint = self.small_font.render("Pressione N para jogar novamente", True, settings.COLOR_TEXT)
        hint_x = settings.SCREEN_WIDTH // 2 - hint.get_width() // 2
        self.screen.blit(hint, (hint_x, 288))
