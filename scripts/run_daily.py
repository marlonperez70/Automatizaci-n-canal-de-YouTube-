import sys
from pathlib import Path

# Agregar root al path para imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

import time
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from config.settings import SCHEDULE_HOUR, BASE_DIR, LOG_DIR
from src.utils.logger import setup_logger
from src.utils.database import init_db, SessionLocal, Video
from src.scraper.youtube_scraper import YouTubeScraper
from src.processor.gemini_client import GeminiClient
from src.media.tts_generator import TTSGenerator
from src.media.video_composer import VideoComposer
from src.publisher.youtube_client import YouTubeClient

# Configurar logger principal
logger = setup_logger('main_pipeline')

def run_pipeline():
    """Flujo principal de ejecución"""
    logger.info("=== Iniciando Pipeline Diario ===")
    
    # 1. Inicializar componentes
    scraper = YouTubeScraper()
    gemini = GeminiClient()
    tts = TTSGenerator()
    composer = VideoComposer()
    uploader = YouTubeClient()
    
    db = None
    try:
        # 2. Buscar candidatos
        candidates = scraper.find_new_videos(BASE_DIR / 'config' / 'channels.json')
        
        if not candidates:
            logger.info("No se encontraron videos nuevos para procesar hoy.")
            return

        # Procesar solo el mejor candidato (Top 1) para el MVP
        top_candidate = candidates[0]
        video_details = top_candidate['video']
        logger.info(f"Procesando candidato: {video_details['title']} (Score: {top_candidate['score']:.2f})")
        
        db = SessionLocal()
        
        # Registrar en DB
        video_record = Video(
            youtube_id=video_details['id'],
            channel_id=video_details['channel_id'],
            title=video_details['title'],
            url=video_details['webpage_url'],
            duration=video_details['duration'],
            views=video_details['view_count'],
            published_at=datetime.strptime(video_details['upload_date'], '%Y%m%d'),
            status="processing"
        )
        db.add(video_record)
        db.commit()
        
        # 3. Descargar Video
        video_path = scraper.download_video(video_details['webpage_url'])
        if not video_path:
            raise Exception("Fallo en descarga")
            
        video_record.file_path = video_path
        
        # 4. Obtener Transcripción (Simulada usando Gemini sobre metadata si no hay subs)
        # En producción real: extraer subtitulos del archivo descargado (.vtt)
        # Para MVP: Generamos resumen basado en titulo y descripción si no extrae texto
        # TODO: Implementar extracción real de subtitulos si existen
        
        # 5. Generar Guion y Metadata con Gemini
        # Usamos descripción como input básico para el MVP
        transcript_input = f"{video_details['title']}\n{video_details['description']}"
        
        summary_script = gemini.generate_summary(transcript_input)
        if not summary_script:
            raise Exception("Fallo generando resumen")
            
        video_record.summary = summary_script
        
        metadata = gemini.generate_metadata(summary_script)
        
        # 6. Generar Audio TTS
        audio_filename = f"{video_details['id']}_tts.mp3"
        audio_path = tts.generate_audio_sync(summary_script, audio_filename)
        
        if not audio_path:
            raise Exception("Fallo generando audio")
            
        # 7. Componer Video
        output_filename = f"{video_details['id']}_final.mp4"
        final_video_path = composer.combine_video_audio(video_path, audio_path, output_filename)
        
        if not final_video_path:
            raise Exception("Fallo componiendo video")
            
        video_record.status = "ready"
        db.commit()
        
        # 8. Subir a YouTube (Opcional en primeras pruebas)
        # video_id = uploader.upload_video(
        #     final_video_path,
        #     metadata['title'],
        #     metadata['description'],
        #     metadata['tags']
        # )
        
        # if video_id:
        #     video_record.status = "uploaded"
        #     logger.info(f"Video publicado exitosamente: https://youtu.be/{video_id}")
        # else:
        #     logger.warning("Video listo pero no subido (o fallo subida)")
            
        logger.info("Pipeline completado exitosamente para 1 video.")
        
    except Exception as e:
        logger.error(f"Fallo en pipeline: {e}")
        if 'video_record' in locals():
            video_record.status = "error"
            video_record.error_message = str(e)
            db.commit()
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    # Inicializar DB
    init_db()
    
    # Modo manual para pruebas inmediatas si se pasa argumento
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        run_pipeline()
    else:
        # Modo Scheduler
        scheduler = BlockingScheduler()
        # Ejecutar todos los días a la hora programada
        scheduler.add_job(run_pipeline, 'cron', hour=SCHEDULE_HOUR)
        
        logger.info(f"Scheduler iniciado. Ejecución programada a las {SCHEDULE_HOUR}:00 UTC")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass
