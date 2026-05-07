"""Loop e cena principal do jogo de lances livres."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

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
        self.using_photo_background = False
        self.static_background = self._build_static_background()
        self.start_screen_background = self._load_start_screen_background()
        ball_rest_pos = self._get_ball_rest_position()

        self.ball_pos = pygame.Vector2(ball_rest_pos)
        self.ball_vel = pygame.Vector2(0, 0)
        self.ball_in_flight = False
        self.shot_scored = False
        self.shot_time = 0.0
        self.floor_bounces = 0

        self.angle_deg = settings.ANGLE_DEFAULT
        self.dragging_shot = False
        self.drag_current_pos = pygame.Vector2(self.ball_pos)
        self.current_throw_force = settings.THROW_FORCE_MIN

        self.score = 0
        self.attempts_used = 0

        self.status_text = ""
        self.status_color = settings.COLOR_TEXT
        self.status_timer = 0.0

        self.feedback_flash_timer = 0.0
        self.feedback_flash_color = settings.COLOR_SUCCESS
        self.throw_frames = self._load_throw_frames()
        self.throw_anim_active = False
        self.throw_anim_time = 0.0
        self.throw_anim_frame_index = 0
        self.throw_anim_start_index = 0
        self.throw_anim_end_index = 0
        self.throw_ball_released = False
        self.pending_throw_velocity = pygame.Vector2(0, 0)

        # Botao "Como Jogar" no canto inferior direito da tela inicial.
        btn_w, btn_h = 160, 38
        padding = 20
        self._how_to_play_btn = pygame.Rect(
            settings.SCREEN_WIDTH - btn_w - padding,
            settings.SCREEN_HEIGHT - btn_h - padding,
            btn_w,
            btn_h,
        )

    def run(self) -> None:
        """Executa o loop principal."""
        self._show_start_screen()

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
                if event.key == pygame.K_r:
                    self._reset_ball()
                if event.key == pygame.K_n:
                    self._new_session()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._start_drag_shot(event.pos)
            if event.type == pygame.MOUSEMOTION:
                self._update_drag_shot(event.pos)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._release_drag_shot(event.pos)

    def _show_start_screen(self) -> None:
        """Exibe a tela inicial. Clicar em 'Como Jogar' abre as instrucoes;
        qualquer outra tecla ou clique inicia o jogo.
        """
        waiting_for_player = True

        while waiting_for_player and self.running:
            self.clock.tick(settings.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting_for_player = False
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self._how_to_play_btn.collidepoint(event.pos):
                        # Abre tela de instrucoes sem sair da tela inicial.
                        self._show_instructions_screen()
                    else:
                        waiting_for_player = False
                elif event.type == pygame.KEYUP:
                    waiting_for_player = False

            if not self.running:
                break

            self._draw_start_screen()
            pygame.display.flip()

    def _draw_start_screen(self) -> None:
        """Renderiza a tela inicial com titulo, prompt e botao 'Como Jogar'."""
        if self.start_screen_background is not None:
            self.screen.blit(self.start_screen_background, (0, 0))
        else:
            self.screen.blit(self.static_background, (0, 0))

        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 14, 24, 160))
        self.screen.blit(overlay, (0, 0))

        cx = settings.SCREEN_WIDTH // 2
        cy = settings.SCREEN_HEIGHT // 2

        # Titulo principal.
        # title_surface = self.font.render("BilóHooper", True, settings.COLOR_ACCENT)
        # self.screen.blit(title_surface, (cx - title_surface.get_width() // 2, cy - 100))

        # # Subtitulo.
        # sub_surface = self.small_font.render("Lances Livres", True, settings.COLOR_TEXT)
        # self.screen.blit(sub_surface, (cx - sub_surface.get_width() // 2, cy - 64))

        # Prompt de inicio.
        prompt_surface = self.small_font.render(
            "Pressione qualquer tecla ou clique para jogar!",
            True,
            settings.COLOR_TEXT,
        )
        self.screen.blit(prompt_surface, (cx - prompt_surface.get_width() // 2, cy - 16))

        # Botao "Como Jogar" no canto inferior direito.
        mouse_pos = pygame.mouse.get_pos()
        btn_hovered = self._how_to_play_btn.collidepoint(mouse_pos)
        btn_color = settings.COLOR_ACCENT if btn_hovered else (30, 38, 56)
        btn_text_color = (10, 14, 24) if btn_hovered else settings.COLOR_TEXT
        pygame.draw.rect(self.screen, btn_color, self._how_to_play_btn, border_radius=8)
        pygame.draw.rect(self.screen, settings.COLOR_ACCENT, self._how_to_play_btn, width=2, border_radius=8)
        btn_label = self.small_font.render("Como jogar", True, btn_text_color)
        self.screen.blit(
            btn_label,
            (
                self._how_to_play_btn.centerx - btn_label.get_width() // 2,
                self._how_to_play_btn.centery - btn_label.get_height() // 2,
            ),
        )

    def _show_instructions_screen(self) -> None:
        """Exibe a tela de instrucoes completa. Fecha com qualquer tecla ou clique."""
        waiting = True
        while waiting and self.running:
            self.clock.tick(settings.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type in (pygame.KEYUP, pygame.MOUSEBUTTONUP):
                    waiting = False

            if not self.running:
                break

            self._draw_instructions_screen()
            pygame.display.flip()

    def _draw_instructions_screen(self) -> None:
        """Renderiza o overlay de instrucoes centralizado verticalmente na tela."""
        # Fundo.
        if self.start_screen_background is not None:
            self.screen.blit(self.start_screen_background, (0, 0))
        else:
            self.screen.blit(self.static_background, (0, 0))

        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 10, 20, 210))
        self.screen.blit(overlay, (0, 0))

        cx = settings.SCREEN_WIDTH // 2
        title_gap = 48   # espaco apos o titulo
        section_h = 28   # altura de cada cabecalho de secao
        body_h = 24      # altura de cada linha de conteudo
        gap = 10         # espaco entre secoes

        # Calcula a altura total do bloco para centralizar verticalmente.
        total_h = (
            title_gap
            + section_h + 2 * body_h + gap   # OBJETIVO
            + section_h + 4 * body_h + gap   # CONTROLES
            + section_h + 2 * body_h          # TECLAS
        )
        y = (settings.SCREEN_HEIGHT - total_h) // 2

        # # Titulo da tela.
        # title = self.font.render("Como Jogar", True, settings.COLOR_ACCENT)
        # self.screen.blit(title, (cx - title.get_width() // 2, y))
        # y += title_gap

        # Secao: Objetivo.
        sec1 = self.small_font.render("OBJETIVO", True, settings.COLOR_ACCENT)
        self.screen.blit(sec1, (cx - sec1.get_width() // 2, y))
        y += section_h
        for line in [
            "Acerte o máximo de cestas em 10 tentativas.",
            "Quanto maior o aproveitamento, melhor!",
        ]:
            s = self.small_font.render(line, True, settings.COLOR_TEXT)
            self.screen.blit(s, (cx - s.get_width() // 2, y))
            y += body_h
        y += gap

        # Secao: Controles.
        sec2 = self.small_font.render("CONTROLES", True, settings.COLOR_ACCENT)
        self.screen.blit(sec2, (cx - sec2.get_width() // 2, y))
        y += section_h
        for line in [
            "1° - Clique na bola para mirar.",
            "2° - Arraste o mouse para mirar e definir a força.",
            "3° - Solte o botão para arremessar.",
            "   Dica: Arraste mais longe para mais força!",
        ]:
            s = self.small_font.render(line, True, settings.COLOR_TEXT)
            self.screen.blit(s, (cx - s.get_width() // 2, y))
            y += body_h
        y += gap

        # Secao: Teclas.
        sec3 = self.small_font.render("TECLAS DE ATALHO", True, settings.COLOR_ACCENT)
        self.screen.blit(sec3, (cx - sec3.get_width() // 2, y))
        y += section_h
        for line in [
            "R — Resetar a posição da bola",
            "N — Iniciar nova partida",
        ]:
            s = self.small_font.render(line, True, settings.COLOR_TEXT)
            self.screen.blit(s, (cx - s.get_width() // 2, y))
            y += body_h

        # Rodape fixo na parte inferior da tela.
        footer = self.small_font.render(
            "Pressione qualquer tecla ou clique para voltar",
            True,
            (160, 160, 180),
        )
        self.screen.blit(footer, (cx - footer.get_width() // 2, settings.SCREEN_HEIGHT - 36))

    def _load_start_screen_background(self) -> pygame.Surface | None:
        image_path = Path(__file__).resolve().parents[1] / settings.START_SCREEN_IMAGE_PATH
        if not image_path.exists():
            return None

        try:
            loaded = pygame.image.load(str(image_path)).convert()
        except pygame.error:
            return None

        return pygame.transform.smoothscale(
            loaded,
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
        )

    def _update(self, dt: float) -> None:
        self._update_status_timer(dt)
        self._update_feedback_flash_timer(dt)
        self._update_throw_animation(dt)

        if self.dragging_shot and not self.ball_in_flight:
            self._sync_ball_to_pose(1)

        if not self.ball_in_flight:
            return

        self.shot_time += dt
        prev_pos = pygame.Vector2(self.ball_pos)
        self.ball_vel.y += settings.GRAVITY * dt
        self.ball_pos += self.ball_vel * dt

        # Valida cesta antes das colisoes para evitar rejeicao indevida no aro.
        self._check_made_basket(prev_pos)
        self._resolve_hoop_collisions()
        self._resolve_floor_collision()

        if self._should_end_shot():
            self._finalize_shot(auto_miss=not self.shot_scored)
            return

        if self._is_ball_out_of_bounds():
            self._finalize_shot(auto_miss=not self.shot_scored)

    def _start_drag_shot(self, mouse_pos: tuple[int, int]) -> None:
        if self.ball_in_flight:
            return
        if self.throw_anim_active:
            return
        if self.attempts_used >= settings.MAX_ATTEMPTS:
            self._set_status("Sem tentativas. Pressione N para novo jogo.", settings.COLOR_ACCENT, 2.0)
            return
        if self.dragging_shot:
            return

        click_pos = pygame.Vector2(mouse_pos)
        if click_pos.distance_to(self.ball_pos) > settings.BALL_RADIUS + settings.DRAG_START_TOLERANCE_PX:
            return

        self.dragging_shot = True
        self.drag_current_pos.update(click_pos)
        self.current_throw_force = settings.THROW_FORCE_MIN
        self._update_drag_aim_and_force()
        self._sync_ball_to_pose(1)

    def _update_drag_shot(self, mouse_pos: tuple[int, int]) -> None:
        if not self.dragging_shot:
            return
        if self.ball_in_flight:
            self._cancel_drag_shot()
            return
        self.drag_current_pos.update(mouse_pos)
        self._update_drag_aim_and_force()

    def _update_drag_aim_and_force(self) -> None:
        drag_vec = self.drag_current_pos - self.ball_pos
        drag_distance = drag_vec.length()
        if drag_distance <= 0.0001:
            return

        # Usa o vetor de arrasto para definir direcao de arremesso.
        dy_up = -drag_vec.y
        angle_deg = math.degrees(math.atan2(dy_up, drag_vec.x))
        self.angle_deg = max(settings.ANGLE_MIN, min(settings.ANGLE_MAX, angle_deg))

        t = drag_distance / settings.DRAG_MAX_DISTANCE_PX
        t = max(0.0, min(1.0, t))
        self.current_throw_force = (
            settings.THROW_FORCE_MIN
            + t * (settings.THROW_FORCE_MAX - settings.THROW_FORCE_MIN)
        )

        if self.dragging_shot and not self.ball_in_flight:
            self._sync_ball_to_pose(1)

    def _release_drag_shot(self, mouse_pos: tuple[int, int]) -> None:
        if not self.dragging_shot:
            return
        self.drag_current_pos.update(mouse_pos)
        self._update_drag_aim_and_force()

        drag_vec = self.drag_current_pos - self.ball_pos
        if drag_vec.length() < settings.DRAG_MIN_DISTANCE_PX:
            self._cancel_drag_shot()
            return
        if self.ball_in_flight:
            self._cancel_drag_shot()
            return
        if self.attempts_used >= settings.MAX_ATTEMPTS:
            self._cancel_drag_shot()
            self._set_status("Sem tentativas. Pressione N para novo jogo.", settings.COLOR_ACCENT, 2.0)
            return

        angle_rad = math.radians(self.angle_deg)
        self.pending_throw_velocity = pygame.Vector2(
            math.cos(angle_rad) * self.current_throw_force,
            -math.sin(angle_rad) * self.current_throw_force,
        )
        self._sync_ball_to_pose(2)
        self.attempts_used += 1
        self.dragging_shot = False
        self._launch_ball()
        self._start_throw_animation()

    def _cancel_drag_shot(self) -> None:
        self.dragging_shot = False
        self.drag_current_pos.update(self.ball_pos)
        self.current_throw_force = settings.THROW_FORCE_MIN
        self._sync_ball_to_pose(0)

    def _reset_ball(self) -> None:
        self._cancel_drag_shot()
        self.ball_pos.update(self._get_ball_rest_position())
        self.ball_vel.update(0, 0)
        self.ball_in_flight = False
        self.shot_scored = False
        self.shot_time = 0.0
        self.floor_bounces = 0
        self.throw_anim_active = False
        self.throw_anim_time = 0.0
        self.throw_anim_frame_index = 0
        self.throw_anim_start_index = 0
        self.throw_anim_end_index = 0
        self.throw_ball_released = False
        self.pending_throw_velocity.update(0, 0)

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

    def _start_throw_animation(self) -> None:
        if not self.throw_frames:
            self.throw_anim_active = False
            return

        frame_count = len(self.throw_frames)
        if frame_count >= 5:
            self.throw_anim_start_index = 2
            self.throw_anim_end_index = 4
        elif frame_count >= 3:
            self.throw_anim_start_index = 1
            self.throw_anim_end_index = frame_count - 1
        else:
            self.throw_anim_start_index = 0
            self.throw_anim_end_index = frame_count - 1

        self.throw_anim_active = True
        self.throw_anim_time = 0.0
        self.throw_anim_frame_index = self.throw_anim_start_index

    def _update_throw_animation(self, dt: float) -> None:
        if not self.throw_anim_active:
            return

        self.throw_anim_time += dt
        frame_count = self.throw_anim_end_index - self.throw_anim_start_index + 1
        total_duration = frame_count * settings.THROW_FRAME_DURATION

        if self.throw_anim_time >= total_duration:
            self.throw_anim_active = False
            self.throw_anim_frame_index = self.throw_anim_end_index
            return

        local_index = min(frame_count - 1, int(self.throw_anim_time / settings.THROW_FRAME_DURATION))
        self.throw_anim_frame_index = self.throw_anim_start_index + local_index

    def _launch_ball(self) -> None:
        if self.throw_ball_released:
            return

        self.ball_vel.update(self.pending_throw_velocity)
        self.ball_in_flight = True
        self.shot_scored = False
        self.shot_time = 0.0
        self.floor_bounces = 0
        self.throw_ball_released = True

    def _sync_ball_to_pose(self, pose_index: int) -> None:
        self.ball_pos.update(self._get_ball_pose_position(pose_index))

    def _get_ball_pose_position(self, pose_index: int) -> tuple[float, float]:
        pose_offsets = [
            (settings.BALL_HAND_OFFSET_X,                          settings.BALL_HAND_OFFSET_Y),
            (settings.BALL_HAND_OFFSET_X + settings.BALL_AIM_OFFSET_X, settings.BALL_HAND_OFFSET_Y + settings.BALL_AIM_OFFSET_Y),
            (settings.BALL_HAND_OFFSET_X + 22, settings.BALL_HAND_OFFSET_Y - 105),
            (settings.BALL_HAND_OFFSET_X + 27, settings.BALL_HAND_OFFSET_Y - 129),
            (settings.BALL_HAND_OFFSET_X + 32, settings.BALL_HAND_OFFSET_Y - 149),
        ]
        safe_index = max(0, min(pose_index, len(pose_offsets) - 1))
        base_x, base_y = self._get_player_base_position()
        offset_x, offset_y = pose_offsets[safe_index]
        return (base_x + offset_x, base_y + offset_y)

    def _resolve_hoop_collisions(self) -> None:
        """Trata colisoes da bola com o aro (nos esquerdo/direito) e com a tabela.

        Nao aplica colisao se a bola ja esta descendo pelo canal do aro (cesta
        em progresso) ou se ja pontuou e ainda esta passando pelo aro.
        Os nos do aro sao tratados como circulos — veja RIM_LEFT_X / RIM_RIGHT_X
        e RIM_NODE_RADIUS em settings.py para calibrar a posicao e tamanho.
        """
        # Se a bola esta descendo pelo meio do aro, deixa passar (contagem de cesta).
        if self._is_descending_through_rim_channel():
            return
        # Apos pontuar, ignora colisao enquanto a bola ainda sai pelo fundo.
        if self.shot_scored and self.ball_vel.y > 0 and self.ball_pos.y >= settings.RIM_Y - settings.BALL_RADIUS:
            return

        # Cria pontos de colisao para o no esquerdo e direito do aro.
        left_rim = pygame.Vector2(settings.RIM_LEFT_X, settings.RIM_Y)
        right_rim = pygame.Vector2(settings.RIM_RIGHT_X, settings.RIM_Y)

        self._resolve_circle_collision(left_rim, settings.RIM_NODE_RADIUS, settings.RIM_BOUNCE)
        self._resolve_circle_collision(right_rim, settings.RIM_NODE_RADIUS, settings.RIM_BOUNCE)
        self._resolve_backboard_collision()

    def _is_descending_through_rim_channel(self) -> bool:
        """Verifica se a bola esta descendo pelo interior do aro (canal de cesta).

        Retorna True quando a bola desce dentro da abertura horizontal do aro
        e esta na faixa vertical proxima ao RIM_Y. Nesse caso, colisoes com os
        nos do aro sao suprimidas para a bola passar livremente.
        """
        # Bola subindo nao pode estar 'passando' pelo aro.
        if self.ball_vel.y <= 0:
            return False

        # Verifica se o centro da bola esta dentro da abertura horizontal do aro.
        inner_left = settings.RIM_LEFT_X + settings.BALL_RADIUS * 0.2
        inner_right = settings.RIM_RIGHT_X - settings.BALL_RADIUS * 0.2
        in_channel_x = inner_left <= self.ball_pos.x <= inner_right

        # Verifica se a bola esta na faixa vertical proxima ao aro.
        rim_top = settings.RIM_Y - settings.BALL_RADIUS * 0.9
        rim_bottom = settings.RIM_Y + settings.BALL_RADIUS * 2.4
        near_rim_y = rim_top <= self.ball_pos.y <= rim_bottom
        return in_channel_x and near_rim_y

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
        """Detecta se a bola cruzou o plano do aro de cima para baixo (cesta valida).

        Usa interpolacao linear entre a posicao anterior e atual para encontrar
        o ponto exato de cruzamento em RIM_Y. Se o cruzamento ocorreu dentro da
        abertura interna do aro (RIM_LEFT_X .. RIM_RIGHT_X), a cesta e contada.

        Para calibrar o aro com a imagem de fundo, ajuste em settings.py:
          RIM_Y       — altura do aro em pixels (diminua para subir)
          RIM_LEFT_X  — borda esquerda interna do aro
          RIM_RIGHT_X — borda direita interna do aro
        """
        # Ignora se ja pontuou ou se a bola esta subindo.
        if self.shot_scored:
            return
        if self.ball_vel.y <= 0:
            return
        # A bola deve ter cruzado RIM_Y neste frame (estava acima, agora abaixo).
        if prev_pos.y >= settings.RIM_Y or self.ball_pos.y < settings.RIM_Y:
            return

        # Interpola para achar a posicao X exata no plano do aro.
        dy = self.ball_pos.y - prev_pos.y
        if abs(dy) <= 0.0001:
            return

        t = (settings.RIM_Y - prev_pos.y) / dy
        t = max(0.0, min(1.0, t))
        cross_x = prev_pos.x + (self.ball_pos.x - prev_pos.x) * t

        # Verifica se o cruzamento foi dentro da abertura interna do aro.
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
        if self.using_photo_background:
            if settings.SHOW_HOOP_OVERLAY_ON_PHOTO:
                self._draw_hoop()
            # Mantem o frame idle do jogador visivel para orientar o clique inicial.
            if settings.SHOW_PLAYER_SILHOUETTE_ON_PHOTO or self.throw_anim_active or self.throw_frames:
                self._draw_player()
        else:
            self._draw_court()
            self._draw_player()
        self._draw_aim_preview()
        self._draw_ball()
        self._draw_feedback_flash()
        self._draw_ui()
        self._draw_round_end_overlay()

    def _load_throw_frames(self) -> list[pygame.Surface]:
        assets_dir = Path(__file__).resolve().parents[1] / "assets" / "images" / "player"
        frame_paths = sorted(assets_dir.glob("process_*.png"), key=self._frame_sort_key)
        if not frame_paths:
            frame_paths = sorted(assets_dir.glob("precess_*.png"), key=self._frame_sort_key)
        if not frame_paths:
            frame_paths = sorted(assets_dir.glob("processo*.png"), key=self._frame_sort_key)
        if not frame_paths:
            frame_paths = sorted(assets_dir.glob("arremesso*.png"), key=self._frame_sort_key)

        frames: list[pygame.Surface] = []
        for image_path in frame_paths:
            try:
                loaded = pygame.image.load(str(image_path)).convert_alpha()
            except pygame.error:
                continue

            source_height = max(1, loaded.get_height())
            scale = settings.THROW_IMAGE_HEIGHT / source_height
            target_width = max(1, int(loaded.get_width() * scale))
            frame = pygame.transform.smoothscale(loaded, (target_width, settings.THROW_IMAGE_HEIGHT))
            frames.append(frame)

        return frames

    def _frame_sort_key(self, path: Path) -> tuple[int, str]:
        stem = path.stem
        number_chunks = re.findall(r"\d+", stem)
        if number_chunks:
            return (int(number_chunks[-1]), stem)
        return (10**9, stem)

    def _draw_player(self) -> None:
        if self.throw_anim_active and self.throw_frames:
            self._draw_throw_animation_frame()
            return
        if self.dragging_shot and len(self.throw_frames) >= 2:
            self._draw_throw_frame(1)
            return
        if self.throw_frames:
            self._draw_throw_frame(0)
            return
        self._draw_player_silhouette()

    def _draw_throw_animation_frame(self) -> None:
        self._draw_throw_frame(self.throw_anim_frame_index)

    def _draw_throw_frame(self, frame_index: int) -> None:
        if not self.throw_frames:
            return

        safe_index = max(0, min(frame_index, len(self.throw_frames) - 1))
        frame = self.throw_frames[safe_index]
        base_x, base_y = self._get_player_base_position()
        image_rect = frame.get_rect()
        image_rect.midbottom = (
            int(base_x + settings.THROW_IMAGE_OFFSET_X),
            int(base_y + settings.THROW_IMAGE_OFFSET_Y),
        )
        self.screen.blit(frame, image_rect)

    def _build_static_background(self) -> pygame.Surface:
        if settings.USE_BACKGROUND_IMAGE:
            image_path = Path(__file__).resolve().parents[1] / settings.BACKGROUND_IMAGE_PATH
            if image_path.exists():
                try:
                    loaded = pygame.image.load(str(image_path)).convert()
                    scaled = pygame.transform.smoothscale(
                        loaded,
                        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
                    )
                    self.using_photo_background = True
                    return scaled
                except pygame.error:
                    self.using_photo_background = False

        self.using_photo_background = False
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
        base_x, base_y = self._get_player_base_position()

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

        # Marca visual da mao para reforcar a origem do arremesso.
        hand_x, hand_y = self._get_ball_rest_position()
        pygame.draw.circle(self.screen, (58, 64, 80), (int(hand_x), int(hand_y)), 6)

    def _get_player_base_position(self) -> tuple[float, float]:
        return (settings.PLAYER_BASE_X, settings.PLAYER_BASE_Y)

    def _get_ball_rest_position(self) -> tuple[float, float]:
        base_x, base_y = self._get_player_base_position()
        return (
            base_x + settings.BALL_HAND_OFFSET_X,
            base_y + settings.BALL_HAND_OFFSET_Y,
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

        if not self.dragging_shot:
            return

        angle_rad = math.radians(self.angle_deg)
        direction = pygame.Vector2(math.cos(angle_rad), -math.sin(angle_rad))

        start = self.ball_pos
        end = start + direction * 80
        pygame.draw.line(self.screen, settings.COLOR_ACCENT, start, end, 3)
        pygame.draw.line(self.screen, (210, 210, 210), self.ball_pos, self.drag_current_pos, 2)

        self._draw_preview_dots(direction, self.current_throw_force, settings.COLOR_LINES)

    def _draw_preview_dots(
        self,
        direction: pygame.Vector2,
        throw_force: float,
        color: tuple[int, int, int],
    ) -> None:
        # Pontos da trajetoria aproximada para facilitar calibracao do arremesso.
        sim_pos = pygame.Vector2(self.ball_pos)
        sim_vel = direction * throw_force
        step_dt = 0.08
        for _ in range(14):
            sim_vel.y += settings.GRAVITY * step_dt
            sim_pos += sim_vel * step_dt
            pygame.draw.circle(self.screen, color, sim_pos, 3)

    def _draw_ui(self) -> None:
        """Renderiza a UI minimalista em jogo: placar, barra de forca e feedback."""
        attempts_left = settings.MAX_ATTEMPTS - self.attempts_used
        pad = 16

        # --- Placar e tentativas no canto inferior direito ---
        score_text = f"Placar: {self.score}  |  Tentativas: {self.attempts_used}/{settings.MAX_ATTEMPTS}"
        score_surface = self.small_font.render(score_text, True, settings.COLOR_TEXT)
        score_x = settings.SCREEN_WIDTH - score_surface.get_width() - pad
        score_y = settings.SCREEN_HEIGHT - score_surface.get_height() - pad
        self.screen.blit(score_surface, (score_x, score_y))

        # Aviso de fim de tentativas centralizado no topo.
        if not self.ball_in_flight and attempts_left == 0:
            hint = "Fim das tentativas  —  Pressione N para recomecar"
            hint_surface = self.small_font.render(hint, True, settings.COLOR_ACCENT)
            hint_x = settings.SCREEN_WIDTH // 2 - hint_surface.get_width() // 2
            self.screen.blit(hint_surface, (hint_x, 16))

        # --- Barra de forca no canto inferior direito (acima do placar) ---
        self._draw_force_bar()

        # --- Mensagem de feedback centralizada na tela ---
        if self.status_timer > 0.0:
            status_surface = self.font.render(self.status_text, True, self.status_color)
            status_x = settings.SCREEN_WIDTH // 2 - status_surface.get_width() // 2
            self.screen.blit(status_surface, (status_x, settings.SCREEN_HEIGHT // 2 - 60))

    def _draw_force_bar(self) -> None:
        """Barra de forca horizontal ancorada no canto inferior direito.
        Aparece apenas enquanto o jogador esta arrastando para arremessar.
        """
        if not self.dragging_shot:
            return

        pad = 16
        bar_w = 200
        bar_h = 12
        # Posicionada acima do texto de placar (que tem ~20px de altura + pad).
        bar_x = settings.SCREEN_WIDTH - bar_w - pad
        bar_y = settings.SCREEN_HEIGHT - bar_h - 44

        pct = (self.current_throw_force - settings.THROW_FORCE_MIN) / (
            settings.THROW_FORCE_MAX - settings.THROW_FORCE_MIN
        )
        pct = max(0.0, min(1.0, pct))

        # Fundo e borda.
        pygame.draw.rect(self.screen, (20, 26, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, settings.COLOR_LINES, (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=4)

        # Preenchimento colorido conforme forca.
        fill_w = int((bar_w - 2) * pct)
        if fill_w > 0:
            # Cor vai de azul (fraco) para laranja/acento (maximo).
            r = int(settings.COLOR_ACCENT[0] * pct + 80 * (1 - pct))
            g = int(settings.COLOR_ACCENT[1] * pct + 120 * (1 - pct))
            b = int(settings.COLOR_ACCENT[2] * pct + 200 * (1 - pct))
            pygame.draw.rect(
                self.screen,
                (r, g, b),
                (bar_x + 1, bar_y + 1, fill_w, bar_h - 2),
                border_radius=3,
            )

        # Label "Forca" a esquerda da barra.
        label = self.small_font.render("Força:", True, settings.COLOR_TEXT)
        self.screen.blit(label, (bar_x - label.get_width() - 8, bar_y - 1))

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
