# 🏀 Como rodar o jogo (passo a passo)

## Antes de começar

Você vai precisar de:

- **Python 3.10 ou mais novo** instalado no computador
- **Conexão com internet** (só na hora de instalar as dependências, depois pode desligar)
- Uns **5 minutinhos** pra fazer tudo

---

## Instalar o Python (se não tiver)

### Windows

1. Abre o navegador e vai em: https://www.python.org/downloads/
2. Clica naquele botão amarelão que baixa a versão mais recente
3. Abre o instalador e **ativa a opção "Add Python to PATH"** (isso é importante!)
4. Clica em "Install Now" e espera terminar
5. Pra ver se deu certo: abre o Prompt de Comando (cmd) e digita:
   ```
   python --version
   ```
   Se aparecer "Python 3.10.x" ou superior, tá pronto.

### Linux (Ubuntu/Debian)

Na maioria das vezes o Python já vem instalado. Verifica com:
```bash
python3 --version
```
Se não tiver, instala com:
```bash
sudo apt install python3 python3-pip python3-venv
```

---

## Baixar o projeto

Tem duas opções:

### Opção 1 — Baixar o ZIP (mais fácil)

1. Vai na página do projeto no GitHub
2. Clica no botão verde **"Code"** e depois em **"Download ZIP"**
3. Extrai a pasta zipada em qualquer lugar (Área de Trabalho, Documentos, etc.)
4. Abre o terminal na pasta que você extraiu

### Opção 2 — Clonar com Git (se tiver o Git instalado)

```bash
git clone <URL_DO_REPOSITORIO>
cd jogo-basquete-topicos1
```

---

## Criar o ambiente virtual

Sempre bom criar um ambientinho separado pro jogo, assim não bagunça as outras coisas no seu Python.

### Windows (no Prompt de Comando / PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Quando rodar o `activate`, vai aparecer um `(.venv)` no começo da linha — sinal que deu certo.

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Mesma coisa: se aparecer `(.venv)` no terminal, funcionou.

> ⚠️ **Dica importante**: toda vez que você fechar e abrir o terminal de novo, vai precisar reativar o ambiente virtual. É só rodar o comando `activate` de novo (o de cima, do seu sistema).

---

## Instalar as dependências

Com o ambiente virtual ativado (aquele `(.venv)` aparecendo), roda:

```bash
pip install -r requirements.txt
```

Isso vai baixar e instalar o Pygame (a única coisa que o jogo usa). Pode demorar uns segundos.

---

## Rodar o jogo

Com o ambiente virtual ativado ainda:

### Windows

```powershell
python -m src.main
```

### Linux

```bash
python3 -m src.main
```

Pronto! O jogo vai abrir em tela cheia. Se aparecer uma janela preta, é normal — é o Pygame iniciando.

---

## Se der problema

### "Pygame não encontrado" / "ModuleNotFoundError"

Você esqueceu de ativar o ambiente virtual ou de instalar as dependências. Volta lá nos passos.

### "python não é reconhecido" (Windows)

O Python não foi adicionado ao PATH. Reinstala o Python e marca a opção "Add Python to PATH" dessa vez.

### "dsp: No such audio device" (Linux)

O jogo não encontrou placa de som. Não esquenta — ele roda normal sem som. É só um aviso.

### "pygame.error: video system not initialized"

Tenta rodar com o ambiente virtual ativado. Se ainda assim der erro, roda no terminal normal (sem ser pelo PowerShell ISE ou VS Code integrado).

---

## Controles do jogo

| Tecla / Ação | O que faz |
|---|---|
| Clicar e arrastar na bola | Mira e define a força |
| Soltar o mouse | Arremessa a bola |
| `R` | Reseta a bola de volta pra mão |
| `N` | Começa uma partida nova |
| `F11` | Alterna entre tela cheia e janela |

### Como funciona a pontuação

1. Você começa no **Lance Livre** — se acertar, ganha **1 ponto** e vai pra **Linha de 3**
2. Na **Linha de 3** — se acertar, ganha **3 pontos** e continua na linha de 3
3. Se errar na linha de 3, volta pro lance livre
4. Você tem **10 tentativas** no total. Quando acabar, aparece sua pontuação final

Boa sorte e divirta-se! 🏀
