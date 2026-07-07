# Tutorial: Baixar áudio do YouTube pelo terminal

## 1. Instalar o yt-dlp

### Linux / macOS
```bash
pip install yt-dlp
```

### Windows (PowerShell ou CMD)
```powershell
pip install yt-dlp
```

Se der erro `yt-dlp não é reconhecido`, use o módulo Python:
```powershell
python -m yt_dlp -x --audio-format wav "URL_DO_VIDEO"
```

Ou adicione o Python Scripts ao PATH (faz uma vez):
1. Abra "Editar variáveis de ambiente do sistema"
2. Clique em "Variáveis de Ambiente"
3. Em "Variáveis do usuário", selecione `Path` → Editar
4. Adicione: `C:\Users\SEU_USUARIO\AppData\Roaming\Python\Python311\Scripts`
5. OK em tudo, feche e reabra o terminal

---

## 2. Baixar o áudio de um vídeo

```bash
yt-dlp -x --audio-format wav "URL_DO_VIDEO"
```

- `-x` = extrair só o áudio (sem baixar o vídeo)
- `--audio-format wav` = formato WAV (compatível com Pygame)

Baixa a música/áudio inteiro — de 3s a 30min, tanto faz.

---

## 3. Verificar a duração do arquivo baixado

```bash
ffprobe arquivo.wav
```

Procure na saída por `Duration: 00:00:XX.XX`.

---

## 4. Detectar silêncio no início (opcional)

Se o áudio tiver silêncio no começo, use este script Python:

### Linux / macOS
```bash
python3 -c "
import wave, struct
with wave.open('arquivo.wav', 'r') as wav:
    frames = wav.readframes(wav.getnframes())
    samples = struct.unpack('<' + 'h' * (len(frames) // 2), frames)
    for start in range(0, min(44100, len(samples)), 441):
        chunk = samples[start:start+441]
        peak = max(abs(s) for s in chunk) if chunk else 0
        print(f'{start/44100:.2f}s: peak={peak}')
        if peak > 5000:
            print('  <- AUDIO COMECA AQUI')
            break
"
```

### Windows (PowerShell/CMD)
```powershell
python -c "
import wave, struct
with wave.open('arquivo.wav', 'r') as wav:
    frames = wav.readframes(wav.getnframes())
    samples = struct.unpack('<' + 'h' * (len(frames) // 2), frames)
    for start in range(0, min(44100, len(samples)), 441):
        chunk = samples[start:start+441]
        peak = max(abs(s) for s in chunk) if chunk else 0
        print(f'{start/44100:.2f}s: peak={peak}')
        if peak > 5000:
            print('  <- AUDIO COMECA AQUI')
            break
"
```

---

## 5. Cortar silêncio com ffmpeg (se necessário)

```bash
ffmpeg -i arquivo.wav -ss 00:00.X -t 00:00.Y arquivo_trimmed.wav
```

- `-ss 00:00.X` = segundo onde o áudio realmente começa
- `-t 00:00.Y` = duração restante (duração total - X)

Exemplo: se o áudio tem 5s e o som começa em 0.3s:
```bash
ffmpeg -i arquivo.wav -ss 00:00.3 -t 00:04.7 arquivo_trimmed.wav
```

---

## 6. Substituir o original pelo cortado

### Linux / macOS
```bash
mv arquivo_trimmed.wav arquivo.wav
```

### Windows
```powershell
Move-Item arquivo_trimmed.wav arquivo.wav -Force
```
