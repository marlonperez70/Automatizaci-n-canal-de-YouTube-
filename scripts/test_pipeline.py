"""
Script de prueba para el pipeline completo de un solo video.
Este script permite validar que cada componente (Scraper, Gemini, TTS, FFmpeg)
funcione correctamente antes de activar el orquestador diario.
"""
import sys
import os
import asyncio
from pathlib import Path

# Añadir el directorio raíz al path para poder importar src
sys.path.append(str(Path(__file__).parent.parent))

from src.scraper.youtube_scraper import YouTubeScraper
from src.processor.gemini_client import GeminiClient
from src.media.tts_generator import TTSGenerator
from src.media.video_composer import VideoComposer
from src.utils.database import get_session, Video, init_db
from src.utils.logger import setup_logger

logger = setup_logger("test_pipeline")

async def test_single_video(video_url):
    logger.info(f"--- INICIANDO TEST PARA VIDEO: {video_url} ---")
    
    # 0. Inicializar DB si no existe
    init_db()
    
    scraper = YouTubeScraper()
    gemini = GeminiClient()
    tts = TTSGenerator()
    composer = VideoComposer()
    
    video_id = video_url.split("v=")[-1]
    
    try:
        # 1. TEST SCRAPER (Descarga)
        logger.info("Paso 1: Probando descarga con yt-dlp...")
        video_path = scraper.download_video(video_id)
        if not video_path or not os.path.exists(video_path):
            logger.error("Error en la descarga.")
            return

        # 2. TEST GEMINI (Traducción/Resumen)
        logger.info("Paso 2: Probando procesamiento con Gemini...")
        # Usamos un texto dummy para el test o intentamos leer subtítulos si existieran
        test_text = "This is a test transcription of a video about artificial intelligence and its impact on the world."
        metadata = gemini.translate_and_summarize(test_text, "AI Revolution 2024")
        if not metadata:
            logger.error("Error en el procesamiento de Gemini.")
            return
        logger.info(f"Título generado: {metadata.get('spanish_title')}")

        # 3. TEST TTS (Voz)
        logger.info("Paso 3: Probando generación de voz (edge-tts)...")
        tts_output = f"data/downloads/{video_id}_test_tts.mp3"
        await tts.generate(metadata['spanish_description'], tts_output)
        if not os.path.exists(tts_output):
            logger.error("Error generando el archivo de audio.")
            return

        # 4. TEST COMPOSER (FFmpeg)
        logger.info("Paso 4: Probando composición final con FFmpeg...")
        final_video = composer.compose(video_path, tts_output, f"{video_id}_FINAL_TEST")
        if final_video and os.path.exists(final_video):
            logger.info(f"--- TEST EXITOSO! ---")
            logger.info(f"Video final disponible en: {final_video}")
        else:
            logger.error("Error en la composición del video final.")

    except Exception as e:
        logger.exception(f"Ocurrió un error inesperado durante el test: {e}")

if __name__ == "__main__":
    # Puedes cambiar esta URL por cualquier video corto en inglés para probar
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # URL de ejemplo
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    asyncio.run(test_single_video(test_url))
