import subprocess
import logging
import json
from pathlib import Path
from config.settings import (
    OUTPUT_VIDEO_CODEC,
    OUTPUT_AUDIO_CODEC,
    OUTPUT_VIDEO_BITRATE,
    OUTPUT_AUDIO_BITRATE,
    ORIGINAL_AUDIO_VOLUME,
    PROCESSED_DIR
)

logger = logging.getLogger(__name__)

class VideoComposer:
    def __init__(self):
        pass

    def get_duration(self, file_path: str) -> float:
        """Obtiene la duración de un archivo multimedia usando ffprobe"""
        cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            str(file_path)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            logger.error(f"Error obteniendo duración de {file_path}: {e}")
            return 0.0

    def combine_video_audio(self, video_path: str, audio_path: str, output_filename: str) -> str:
        """
        Combina video y audio:
        - Mantiene el video original pero ajusta su volumen.
        - Agrega el audio TTS como track principal.
        - Corta el video para que coincida con la duración del audio TTS (si el video es más largo).
        """
        output_path = PROCESSED_DIR / output_filename
        
        # Obtener duraciones
        video_duration = self.get_duration(video_path)
        audio_duration = self.get_duration(audio_path)
        
        logger.info(f"Duración Video: {video_duration}s, Audio TTS: {audio_duration}s")
        
        # Lógica de recorte: El video final durará lo que dure el audio TTS (más un margen pequeño)
        # Si el video es más corto que el audio, tendríamos un problema (pantalla negra),
        # pero para este MVP asumimos que el video original es largo y el resumen es corto.
        
        # Comando FFmpeg complejo
        # 1. Input 0: Video
        # 2. Input 1: Audio TTS
        # 3. Filter_complex:
        #    [0:a]volume=0.1[a0]; -> Bajar volumen audio original
        #    [a0][1:a]amix=inputs=2:duration=longest[a_out] -> Mezclar audios
        #    -t {audio_duration} -> Cortar video al final del audio
        
        cmd = [
            'ffmpeg',
            '-y',  # Sobreescribir
            '-i', str(video_path),
            '-i', str(audio_path),
            '-filter_complex',
            f'[0:a]volume={ORIGINAL_AUDIO_VOLUME}[original_audio];[original_audio][1:a]amix=inputs=2:duration=first:dropout_transition=2[a_out]',
            '-map', '0:v',
            '-map', '[a_out]',
            '-c:v', OUTPUT_VIDEO_CODEC,
            '-b:v', OUTPUT_VIDEO_BITRATE,
            '-c:a', OUTPUT_AUDIO_CODEC,
            '-b:a', OUTPUT_AUDIO_BITRATE,
            '-t', str(audio_duration + 1), # Dar 1 segundo extra
            str(output_path)
        ]
        
        logger.info(f"Comenzando renderizado: {output_filename}")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            logger.info(f"Video renderizado exitosamente: {output_path}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error en FFmpeg: {e.stderr.decode()}")
            return None
