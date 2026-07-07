# 🏀 Jogo de Basquete — Arremessos

Projeto desenvolvido para a disciplina de Tópicos 1.  
Um jogo de arremessos de basquete com física simples, animações e sistema de pontuação alternado entre lance livre e linha de 3 pontos.

---

## Tecnologias

- Python 3.10+
- [Pygame](https://www.pygame.org/) >= 2.5.0

---

## Como executar

Consulte o passo a passo detalhado em (docs/tutorial_para_rodar_o_jogo.md).


## Controles

| Ação | Controle |
|---|---|
| Iniciar o jogo | Qualquer tecla ou clique na tela inicial |
| Mirar e definir força | Clicar e arrastar o mouse na bola |
| Arremessar | Soltar o botão esquerdo do mouse |
| Resetar a bola | `R` |
| Nova partida | `N` |

---

## Estrutura do projeto

```
jogo-basquete-topicos1/
├── src/
│   ├── main.py        # ponto de entrada
│   ├── game.py        # loop principal e renderização
│   └── settings.py    # constantes e configurações globais
├── assets/
│   ├── images/
│   │   ├── player/    # frames de animação do jogador
│   │   ├── court/     # imagem de fundo da quadra
│   │   └── ui/        # tela inicial e interface
│   └── sounds/        # sons .wav 44.1kHz 16-bit stereo
├── docs/              # documentação do projeto
├── requirements.txt
└── README.md
```

---

## Funcionalidades implementadas

- Física de arremesso com gravidade e trajetória parabólica.
- Colisão com o aro (nós esquerdo e direito) e com a tabela.
- Detecção de cesta válida (bola descendo por dentro do aro) - Precisa ser refinado. Funciona na maioria das vezes, mas em alguns casos nao reconhece a cesta.
- Sistema de pontuação alternado: lance livre (1 pt) → linha de 3 (3 pts) - Acertou o lance livre vai para a linha de 3 pontos, errou volta para o lance livre.
- Limite de 10 tentativas por rodada com tela de resultado final
- Animação de arremesso por frames (5 poses)
- Animação de caminhada entre linha de 3 e lance livre
- Sistema de áudio com efeitos sonoros (preparação, acerto, erro)
- Feedback visual de acerto e erro
