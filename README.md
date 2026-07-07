# 🏀 BilóHooper — Jogo de Arremessos de Basquete

Projeto da disciplina de Tópicos 1.  
Um joguinho onde você alterna entre lance livre e linha de 3 pontos, com física simples, animações e efeitos sonoros.

---

## Como jogar

O passo a passo completo (com instalação do Python, ambiente virtual, etc.) está aqui:

📄 **[docs/tutorial_para_rodar_o_jogo.md](docs/tutorial_para_rodar_o_jogo.md)**

Mas se você já manja, o resumo é:

```bash
python -m venv .venv               # cria o ambiente virtual
.venv\Scripts\activate             # ativa (Windows)
# ou: source .venv/bin/activate    # ativa (Linux)
pip install -r requirements.txt    # instala o pygame
python -m src.main                 # roda o jogo
```

---

## Controles

| Ação | Como faz |
|---|---|
| Mirar e arremessar | Clica na bola, arrasta (define direção e força) e solta |
| Resetar a bola | `R` |
| Nova partida | `N` |
| Tela cheia / janela | `F11` |

---

## Estrutura do projeto

```
jogo-basquete-topicos1/
├── src/
│   ├── main.py         # ponto de entrada
│   ├── game.py         # o jogo inteiro (loop, física, desenho)
│   └── settings.py     # constantes (tamanho da tela, posições, cores)
├── assets/
│   ├── images/
│   │   ├── player/     # sprites do jogador (arremesso e caminhada)
│   │   ├── court/      # fundo da quadra e bola
│   │   └── ui/         # tela inicial
│   └── sounds/         # efeitos sonoros (.wav)
├── docs/               # tutoriais
├── requirements.txt
└── README.md
```

---

## Tecnologias

- **Python 3.10+**
- **Pygame 2.5+** (a única biblioteca usada)

---

## Funcionalidades

- Física de arremesso com gravidade e trajetória parabólica
- Colisão com os dois lados do aro e com a tabela
- Pontuação alternada: lance livre (1pt) → linha de 3 (3pts)
- 10 tentativas por rodada com tela de resultado
- Animações do jogador (5 poses de arremesso, 4 de caminhada)
- Efeitos sonoros (preparação, acerto, erro, batida no aro)
- Feedback visual de acerto e erro
