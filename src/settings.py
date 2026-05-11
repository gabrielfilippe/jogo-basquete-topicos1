"""Configuracoes globais do projeto."""

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 576
FPS = 60
WINDOW_TITLE = "BilóHooper"

# Tela inicial
START_SCREEN_IMAGE_PATH = "assets/images/ui/start_screen.png"

# Background opcional por imagem (baseado na referencia da quadra).
USE_BACKGROUND_IMAGE = True
BACKGROUND_IMAGE_PATH = "assets/images/court/quadradebasquete.png"
SHOW_HOOP_OVERLAY_ON_PHOTO = False
SHOW_PLAYER_SILHOUETTE_ON_PHOTO = False

# Ancora do jogador e da bola na posicao inicial.
PLAYER_BASE_X = 142
PLAYER_BASE_Y = 446

# Posicoes de arremesso — ajuste X (horizontal) e Y (vertical) para cada linha.
# X: menor valor = mais a esquerda na tela.
# Y: menor valor = mais para cima na tela. A perspectiva da quadra faz a linha de
#    3 pontos ficar um pouco mais baixa (Y maior) que o lance livre.
PLAYER_BASE_X_FREETHROW   = 260   # lance livre — proximo ao topo do garrafao - quanto maior o numero, mais a direita o jogador fica
PLAYER_BASE_Y_FREETHROW   = 390   # lance livre — altura na quadra - quanto maior o numero, mais para baixo o jogador fica
PLAYER_BASE_X_THREE_POINT = 60   # linha de 3 pontos — mais a esquerda - quanto maior o numero, mais a direita o jogador fica
PLAYER_BASE_Y_THREE_POINT = 390   # linha de 3 pontos —  quanto maior o numero, mais para baixo o jogador fica

# Pontuacao por posicao
FREETHROW_SCORE = 1
THREE_POINT_SCORE = 3
BALL_HAND_OFFSET_X = 100
BALL_HAND_OFFSET_Y = -35

# Offsets extras da bola em cada pose (somados a BALL_HAND_OFFSET_X/Y).
# Pose 0 = repouso, Pose 1 = mirando, Poses 2-4 = frames do arremesso.
# Para mover a bola na mira: ajuste BALL_AIM_OFFSET_X (esq/dir) e BALL_AIM_OFFSET_Y (cima/baixo).
# Valores negativos em Y = mais para cima.
BALL_AIM_OFFSET_X = -5    # deslocamento X extra na pose de mira
BALL_AIM_OFFSET_Y = -86  # deslocamento Y extra na pose de mira (negativo = sobe)

THROW_IMAGE_HEIGHT = 220
THROW_IMAGE_OFFSET_X = 80
THROW_IMAGE_OFFSET_Y = 70
THROW_FRAME_DURATION = 0.11

# Parametros de gameplay (parte 1)
BALL_RADIUS = 12
BALL_START_X = 190
BALL_START_Y = 430
GRAVITY = 900.0

ANGLE_MIN = 20.0
ANGLE_MAX = 80.0
ANGLE_DEFAULT = 52.0
ANGLE_STEP = 1.5

POWER_MIN = 350.0
POWER_MAX = 950.0
POWER_DEFAULT = 680.0
POWER_STEP = 18.0

# Forca variavel por tempo segurando espaco
THROW_FORCE_MIN = 350.0
THROW_FORCE_MAX = 950.0
THROW_CHARGE_MAX_MS = 1200

# Ajuste de forca por arrasto do mouse
DRAG_MIN_DISTANCE_PX = 14.0
DRAG_MAX_DISTANCE_PX = 260.0
DRAG_START_TOLERANCE_PX = 24.0

MAX_ATTEMPTS = 10

# ---------------------------------------------------------------------------
# Aro e tabela — coordenadas em pixels na tela (1024 x 576)
#
# Como calibrar:
#   RIM_Y        → altura Y do centro do aro. Diminua para mover para CIMA,
#                  aumente para mover para BAIXO. Ajuste até coincidir com o
#                  topo visual da cesta na imagem de fundo.
#   RIM_LEFT_X   → borda esquerda interna do aro (pixel X).
#   RIM_RIGHT_X  → borda direita interna do aro (pixel X).
#   RIM_NODE_RADIUS → raio dos "nós" do aro para cálculo de colisão.
#
#   BACKBOARD_X  → borda esquerda da tabela (pixel X).
#   BACKBOARD_Y  → topo da tabela (pixel Y). Diminua para mover para CIMA.
#   BACKBOARD_WIDTH  → espessura da tabela em pixels.
#   BACKBOARD_HEIGHT → altura total da tabela em pixels.
# ---------------------------------------------------------------------------
RIM_Y = 163          # era 191 — movido ~28 px para cima para coincidir com a cesta visual
RIM_LEFT_X = 828
RIM_RIGHT_X = 862
RIM_NODE_RADIUS = 7

BACKBOARD_X = 875
BACKBOARD_Y = 45     
BACKBOARD_WIDTH = 10
BACKBOARD_HEIGHT = 150

# Colisao/restituicao
RIM_BOUNCE = 0.7
BACKBOARD_BOUNCE = 0.72
FLOOR_Y = 520
FLOOR_BOUNCE = 0.5
FLOOR_FRICTION = 0.86

MAX_FLOOR_BOUNCES = 3
SHOT_MAX_TIME = 7.0
SHOT_STOP_SPEED = 110.0

FEEDBACK_FLASH_TIME = 0.35

# Cores (RGB)
COLOR_BG = (20, 28, 44)
COLOR_COURT = (123, 146, 104)
COLOR_PAINT = (198, 121, 77)
COLOR_LINES = (241, 238, 230)
COLOR_TEXT = (245, 245, 245)
COLOR_ACCENT = (244, 172, 72)
COLOR_BALL = (235, 137, 55)
COLOR_BOARD = (202, 216, 228)
COLOR_SUCCESS = (255, 198, 88)
COLOR_FAILURE = (210, 230, 242)
COLOR_SUCCESS = (0, 255, 0)



COLOR_SKY_TOP = (57, 66, 116)
COLOR_SKY_MID = (152, 92, 102)
COLOR_SKY_HORIZON = (244, 166, 98)
COLOR_CITY = (82, 70, 96)
COLOR_FENCE = (64, 58, 72)
COLOR_TREE_DARK = (35, 56, 42)
COLOR_TREE_LIGHT = (50, 78, 58)
COLOR_SHADOW = (31, 38, 52)
