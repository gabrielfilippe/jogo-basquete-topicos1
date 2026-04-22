# Jogo de Basquete - Lances Livres (Pygame)

Projeto inicial para a disciplina de Topicos 1.
A proposta e desenvolver um jogo de lances livres com fisica simples, pontuacao e feedback visual.

## Escopo inicial (MVP)
- Janela e loop principal com `pygame`
- Cenario de quadra simplificado
- Bola com gravidade e lancamento parametrico
- Regras de cesta, pontuacao e tentativas

## Como executar
1. Crie e ative um ambiente virtual (opcional, recomendado).
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Rode o jogo:

```bash
python -m src.main
```

## Estrutura

```
jogo-basquete-topicos1/
├── src/
│   ├── main.py          # ponto de entrada
│   ├── game.py          # classe principal e loop do jogo
│   └── settings.py      # configuracoes e constantes globais
├── assets/
│   ├── images/
│   │   ├── player/      # frames de animacao do jogador (process_*.png)
│   │   ├── court/       # fundo da quadra (quadrabasquete.png)
│   │   └── ui/          # tela inicial e elementos de interface
│   ├── sounds/          # sons (futuro)
│   └── fonts/           # fontes customizadas (futuro)
├── docs/                # documentacao e acompanhamento do projeto
├── requirements.txt
└── README.md
```

## Controles (parte 1)
- `Qualquer tecla` ou `clique`: inicia o jogo na tela inicial
- `Clique e arraste` na bola: mira e define forca do arremesso
- `Solte o botao esquerdo`: lanca a bola
- `R`: reseta a bola para nova tentativa
- `N`: reinicia placar e tentativas

## O que ja esta implementado
- Colisao da bola com os dois pontos do aro
- Colisao da bola com a tabela
- Deteccao de cesta valida (bola descendo por dentro do aro)
- Placar e limite de 10 tentativas
- Quique no chao com atrito e encerramento automatico da jogada
- Feedback visual de acerto/erro no aro
- Tela final da rodada com aproveitamento

## Proximos passos
- Adicionar sons para acerto, aro e tabela
- Criar nivel de dificuldade com variacao de distancia
- Refinar animacoes (rede e celebracao de cesta)
