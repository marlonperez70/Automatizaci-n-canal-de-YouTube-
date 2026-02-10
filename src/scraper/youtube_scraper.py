import json
import logging
from datetime import datetime, timedelta
import yt_dlp
from config.settings import (
    DOWNLOAD_DIR, 
    MIN_VIEWS_THRESHOLD, 
    HOURS_LOOKBACK,
    MAX_VIDEO_DURATION,
    SHORT_VIDEO_THRESHOLD
)
from src.utils.database import Video, SessionLocal
from pathlib import Path

logger = logging.getLogger(__name__)

class YouTubeScraper:
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': str(DOWNLOAD_DIR / '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'es'],
            'skip_download': True,  # Default to just fetching metadata first
        }

    def get_channel_videos(self, channel_id: str, limit: int = 5):
        """
        Obtiene los videos más recientes de un canal.
        """
        # URL del canal (tab de videos)
        channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"
        
        logger.info(f"Buscando videos en {channel_url}")
        
        # Opciones para extracción rápida (flat extraction)
        flat_opts = self.ydl_opts.copy()
        flat_opts.update({
            'extract_flat': True,
            'playlistend': limit,
        })

        try:
            with yt_dlp.YoutubeDL(flat_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                if 'entries' in info:
                    return info['entries']
        except Exception as e:
            logger.error(f"Error scraping channel {channel_id}: {e}")
            return []
        return []

    def get_video_details(self, video_url: str):
        """
        Obtiene detalles completos de un video específico.
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                return ydl.extract_info(video_url, download=False)
        except Exception as e:
            logger.error(f"Error getting details for {video_url}: {e}")
            return None

    def download_video(self, video_url: str) -> str:
        """
        Descarga el video y retorna la ruta del archivo.
        """
        download_opts = self.ydl_opts.copy()
        download_opts['skip_download'] = False
        
        try:
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)
                logger.info(f"Video descargado en: {filename}")
                return filename
        except Exception as e:
            logger.error(f"Error descargando {video_url}: {e}")
            return None

    def find_new_videos(self, channels_file: Path):
        """
        Busca videos nuevos candidatos para procesar.
        """
        with open(channels_file, 'r', encoding='utf-8') as f:
            channels_data = json.load(f)

        candidates = []
        db = SessionLocal()
        
        try:
            # Calcular fecha límite (hace X horas)
            cutoff_date = datetime.utcnow() - timedelta(hours=HOURS_LOOKBACK)
            
            for channel in channels_data['channels']:
                logger.info(f"Escaneando canal: {channel['name']}")
                videos = self.get_channel_videos(channel['channel_id'])
                
                for vid in videos:
                    # Verificar si ya existe en DB
                    if db.query(Video).filter_by(youtube_id=vid['id']).first():
                        continue
                        
                    # Obtener detalles completos para filtrar
                    details = self.get_video_details(vid['url'])
                    if not details:
                        continue
                        
                    # 1. Filtro de fecha (aproximado por upload_date)
                    upload_date = datetime.strptime(details['upload_date'], '%Y%m%d')
                    if upload_date < cutoff_date:
                        continue
                        
                    # 2. Filtro de Vistas
                    if details.get('view_count', 0) < MIN_VIEWS_THRESHOLD:
                        logger.info(f"Skip {vid['id']}: Pocas vistas ({details.get('view_count')})")
                        continue
                        
                    # 3. Filtro de Duración
                    duration = details.get('duration', 0)
                    if duration > MAX_VIDEO_DURATION:
                        logger.info(f"Skip {vid['id']}: Muy largo ({duration}s)")
                        continue
                        
                    if duration < SHORT_VIDEO_THRESHOLD:
                        logger.info(f"Skip {vid['id']}: Muy corto ({duration}s)")
                        continue

                    # Si pasa filtros, agregar a candidatos
                    priority = channel.get('priority', 3)
                    # Puntuación simple: prioridad (menor es mejor) + vistas
                    score = (details.get('view_count', 0) / 1000) / priority
                    
                    candidates.append({
                        'video': details,
                        'score': score,
                        'channel_name': channel['name']
                    })
                    
        finally:
            db.close()
            
        # Ordenar por score descendente
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates
