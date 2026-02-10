# YouTube AI Automation (MVP)

Este proyecto automatiza la creación y publicación de videos cortos en YouTube basándose en contenido de otros canales (curación de contenido + resumen con IA).

## Requisitos Previos

1. **Python 3.11+**
2. **FFmpeg**: Debe estar instalado y agregado al PATH del sistema.
   - Windows: `choco install ffmpeg` o descargar de [ffmpeg.org](https://ffmpeg.org/download.html)
3. **Google Cloud Project**:
   - YouTube Data API v3 habilitada.
   - `client_secrets.json` descargado (Credenciales OAuth 2.0).
4. **Google Gemini API Key**:
   - Obtener en [Google AI Studio](https://makersuite.google.com/app/apikey).

## Configuración

1. **Entorno Virtual**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Variables de Entorno**:
   - Copia `.env.example` a `.env`.
   - Rellena las claves:
     - `YOUTUBE_API_KEY`: Para búsquedas (Scraper).
     - `GEMINI_API_KEY`: Para resúmenes y traducción (Processor).
     - `YOUTUBE_CHANNEL_ID`: Tu ID de canal.

3. **Autenticación de YouTube (Subida)**:
   - Coloca tu archivo `client_secrets.json` en la carpeta `config/`.
   - La primera vez que se intente subir un video, se abrirá el navegador para autorizar la app.

4. **Base de Datos**:
   - Inicializa la base de datos:
     ```bash
     python scripts/setup_db.py
     ```

## Ejecución

### Modo Manual (Prueba inmediata)
Para ejecutar el pipeline completo una vez (buscar, descargar, procesar, crear video):
```bash
python scripts/run_daily.py --now
```

### Modo Automático (Scheduler)
Para dejarlo corriendo y que se ejecute todos los días a las 6:00 AM UTC:
```bash
python scripts/run_daily.py
```

### Docker
```bash
docker-compose up -d
```

## Estructura del Proyecto

- `src/scraper`: Busca videos en canales configurados (`config/channels.json`) usando `yt-dlp`.
- `src/processor`: Usa Gemini para resumir y traducir el contenido.
- `src/media`: Genera audio (Edge-TTS) y compone el video final (FFmpeg).
- `src/publisher`: Sube el video a YouTube.
- `data/`: Almacena videos descargados, procesados y la base de datos SQLite.
