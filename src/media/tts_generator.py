import asyncio
import logging
from pathlib import Path
import edge_tts
from config.settings import TTS_VOICE, TTS_RATE, TTS_PITCH, PROCESSED_DIR

logger = logging.getLogger(__name__)

class TTSGenerator:
    def __init__(self):
        self.voice = TTS_VOICE
        self.rate = TTS_RATE
        self.pitch = TTS_PITCH

    async def generate_audio(self, text: str, output_filename: str) -> str:
        """
        Genera audio a partir de texto usando Edge TTS.
        
        Args:
            text (str): Texto a convertir
            output_filename (str): Nombre del archivo de salida (sin ruta completa)
            
        Returns:
            str: Ruta absoluta del archivo de audio generado
        """
        output_path = PROCESSED_DIR / output_filename
        
        # Asegurar que el directorio existe
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
            await communicate.save(str(output_path))
            
            logger.info(f"Audio generado exitosamente: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generando TTS: {e}")
            return None

    def generate_audio_sync(self, text: str, output_filename: str) -> str:
        """Wrapper síncrono para generar audio"""
        return asyncio.run(self.generate_audio(text, output_filename))
