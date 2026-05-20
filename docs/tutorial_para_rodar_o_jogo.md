# Como rodar o jogo

## Requisitos

- Python 3.10 ou superior instalado
- Conexão com internet (só para instalar as dependências)

---

## Passo a passo

### 1. Baixe o projeto

Faça o download do repositório e extraia a pasta (ou clone via Git):

```
git clone <url-do-repositorio>
```

Entre na pasta do projeto:

```
cd jogo-basquete-topicos1
```

---

### 2. Crie o ambiente virtual

**Linux / macOS:**
```
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```
python -m venv .venv
.venv\Scripts\activate
```

---

### 3. Instale as dependências

```
pip install -r requirements.txt
```

---

### 4. Rode o jogo

**Linux / macOS:**
```
python3 -m src.main
```

**Windows:**
```
python -m src.main
```

---
