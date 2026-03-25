# Situacao atual do jogo (Marco/2026)

## 1. Resumo executivo
O projeto implementa um jogo de lances livres em Pygame com loop principal funcional, fisica basica da bola, deteccao de cesta, controle de tentativas, placar e tela de fim de rodada.

A base esta solida para um MVP jogavel de "acertar o aro", com elementos visuais de quadra e feedback de acerto/erro. Ainda nao ha modos de jogo, audio, sistema de dificuldade ou persistencia de dados.

## 2. Escopo implementado hoje
- Janela principal em `1024x576` com `60 FPS`.
- Controle de angulo e forca antes do arremesso.
- Arremesso com gravidade e movimento continuo.
- Colisoes com:
  - dois nos do aro,
  - tabela,
  - piso.
- Deteccao de cesta valida (bola cruzando o plano do aro de cima para baixo).
- Sistema de rodada com:
  - ate 10 tentativas,
  - placar acumulado,
  - aproveitamento ao final.
- Feedback visual:
  - mensagem temporaria de status,
  - flash no aro para acerto/erro,
  - preview de direcao/trajetoria.
- Cenario desenhado por codigo (sem sprites obrigatorios): ceu, cerca, arvores, cidade, quadra, aro e silhueta do jogador.

## 3. Estrutura tecnica
### 3.1 Arquivos principais
- `src/main.py`: ponto de entrada; instancia e executa o jogo.
- `src/game.py`: classe `FreeThrowGame` com estados, update, fisica e render.
- `src/settings.py`: constantes de gameplay, fisica, layout e cores.
- `requirements.txt`: dependencia principal (`pygame>=2.5.0`).

### 3.2 Responsabilidades da classe principal
A classe `FreeThrowGame` concentra:
- inicializacao do Pygame e fontes;
- controle de estado da bola (posicao, velocidade, voo);
- controle de rodada (placar, tentativas);
- tratamento de entrada de teclado;
- atualizacao de fisica por frame;
- renderizacao da cena e UI;
- regras de fim de jogada e fim de rodada.

## 4. Estado de gameplay e regras atuais
### 4.1 Controles disponiveis
- Seta para cima/baixo: ajusta angulo.
- Seta para direita/esquerda: ajusta forca.
- Espaco: arremessa.
- R: reseta bola (nao reinicia placar).
- N: inicia nova sessao (zera placar e tentativas).

### 4.2 Fluxo de uma jogada
1. Jogador ajusta angulo e forca com bola parada.
2. Ao arremessar, a tentativa e consumida imediatamente.
3. A bola recebe velocidade inicial e passa a ser atualizada por gravidade.
4. Durante o voo, sao processadas colisoes com aro/tabela/chao.
5. O sistema avalia se houve cesta valida.
6. A jogada termina por um destes criterios:
   - tempo maximo de jogada atingido,
   - numero maximo de quiques no chao,
   - bola quase parada no piso,
   - bola saiu da area da tela.
7. Ao finalizar, a bola volta para posicao inicial.

### 4.3 Regra de cesta (implementacao atual)
A cesta e contabilizada quando:
- a bola esta descendo (`velocidade Y > 0`),
- houve cruzamento da altura do aro entre o frame anterior e o atual,
- o ponto de cruzamento em X fica entre as bordas internas do aro (com margem baseada no raio da bola).

Esse criterio reduz falsos positivos (por exemplo, bola subindo por baixo do aro).

### 4.4 Placar e encerramento
- Total de tentativas por rodada: `10`.
- Cada cesta soma `+1` ao placar.
- Ao terminar as tentativas, aparece overlay de fim com aproveitamento percentual.
- O jogo so reinicia rodada com tecla `N`.

## 5. Parametros atuais (resumo)
### 5.1 Movimento
- Gravidade: `900.0`.
- Faixa de angulo: `20` a `80` graus.
- Faixa de forca: `350` a `950`.
- Valores iniciais: angulo `52`, forca `680`.

### 5.2 Colisoes e perda de energia
- Restituicao no aro: `0.7`.
- Restituicao na tabela: `0.72`.
- Restituicao no piso: `0.5`.
- Atrito horizontal no piso: `0.86`.

### 5.3 Encerramento automatico da jogada
- Maximo de `3` quiques no piso.
- Tempo maximo de `7.0s` por jogada.
- Finaliza se quase parar no piso (`velocidade <= 110`).

## 6. Estado visual e UX
### 6.1 Pontos fortes da versao atual
- Cenario com identidade visual coerente para MVP.
- UI informa controles, angulo, forca, placar e tentativas.
- Preview de trajetoria ajuda calibracao do usuario.
- Feedback imediato de acerto/erro melhora entendimento do resultado.

### 6.2 Limitacoes visuais atuais
- Rede e animacoes ainda simplificadas.
- Sem assets externos obrigatorios (visual e majoritariamente procedural).
- Sem transicoes de cena alem de overlay de fim de rodada.

## 7. O que ainda nao foi implementado
- Sons (acerto, aro, tabela, erro, interface).
- Sistema de dificuldade (distancia, variacao de cesta, condicoes especiais).
- Modos de jogo (treino, desafio, serie de acertos etc.).
- Persistencia (recordes, historico de sessoes).
- Menu inicial/configuracoes.
- Testes automatizados (unitarios/integracao).
- Telemetria basica de gameplay (ex.: aproveitamento por faixa de angulo/forca).

## 8. Riscos tecnicos e pontos de atencao
- A fisica e propositalmente simples; casos extremos de colisao podem exigir refinamento futuro.
- Classe principal concentra muitas responsabilidades (facil para MVP, menos escalavel para crescimento).
- Parametros de gameplay estao em constantes; falta camada de tuning dinamico (JSON/config em runtime).
- Nao ha suite de testes para garantir nao regressao ao evoluir colisoes/regras.

## 9. Nivel de maturidade do projeto
Classificacao sugerida: **MVP funcional (jogavel)**.

Estado atual por area:
- Gameplay base: concluido para parte 1.
- Fisica: funcional e consistente para escopo educacional.
- UX/UI: boa leitura para prototipo, com feedback util.
- Conteudo e progressao: inicial.
- Polimento e produto final: em desenvolvimento.

## 10. Proximas prioridades recomendadas
1. Adicionar audio basico para reforcar feedback de acerto/erro/colisoes.
2. Separar logica de fisica/regras da renderizacao para facilitar manutencao.
3. Criar ao menos um modo de dificuldade (distancia e/ou tolerancia menor de cesta).
4. Introduzir persistencia de melhor pontuacao local.
5. Escrever testes para regras de cesta e encerramento de jogada.

## 11. Conclusao
O jogo ja cumpre o objetivo central de simular lances livres com controle do arremesso e resultado mensuravel. A situacao atual e adequada para apresentacao de MVP da disciplina e cria uma base clara para evolucoes de conteudo, audio, dificuldade e qualidade tecnica.