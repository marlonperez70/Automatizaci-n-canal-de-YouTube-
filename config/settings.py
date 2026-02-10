"""
Configuración centralizada del proyecto
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv('DATA_DIR', './data'))
DOWNLOAD_DIR = DATA_DIR / 'downloads'
PROCESSED_DIR = DATA_DIR / 'processed'
DB_PATH = DATA_DIR / 'database' / 'videos.db'
LOG_DIR = BASE_DIR / 'logs'

# Crear directorios si no existen
for directory in [DATA_DIR, DOWNLOAD_DIR, PROCESSED_DIR, LOG_DIR, DB_PATH.parent]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'AIzaSyBcYSMWLylEyl9eDu2wS_45Ov9DO4MMfHE')
YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID', 'UCcW0N9ph1dLfNmSgAga7RYQ')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyAaPnsMpGnvGX62o9mDJLjq13UsRDPWJUo')

# Configuración de scraping
MAX_VIDEOS_PER_DAY = int(os.getenv('MAX_VIDEOS_PER_DAY', 5))
MIN_VIEWS_THRESHOLD = int(os.getenv('MIN_VIEWS_THRESHOLD', 1000))
HOURS_LOOKBACK = 24  # Buscar videos de últimas 24 horas

# Configuración de procesamiento
SHORT_VIDEO_THRESHOLD = 300  # 5 minutos en segundos
MAX_VIDEO_DURATION = 1800  # 30 minutos (videos más largos se rechazan)

# Configuración de TTS
TTS_VOICE = "es-ES-AlvaroNeural"  # Voz masculina en español
TTS_RATE = "+0%"  # Velocidad normal
TTS_PITCH = "+0Hz"  # Tono normal

# Configuración de video
OUTPUT_VIDEO_CODEC = "libx264"
OUTPUT_AUDIO_CODEC = "aac"
OUTPUT_VIDEO_BITRATE = "2M"
OUTPUT_AUDIO_BITRATE = "128k"
ORIGINAL_AUDIO_VOLUME = 0.1  # 10% del volumen original

# Horario de publicación (hora UTC)
SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', 6))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
