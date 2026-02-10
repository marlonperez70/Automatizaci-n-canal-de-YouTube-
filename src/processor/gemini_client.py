import google.generativeai as genai
import logging
from config.settings import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY no encontrada en variables de entorno")
            raise ValueError("GEMINI_API_KEY is missing")
            
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_summary(self, transcript_text: str) -> str:
        """
        Genera un resumen en español del texto proporcionado.
        """
        prompt = f"""
        Actúa como un editor de video experto. Tu tarea es resumir la siguiente transcripción de un video de YouTube 
        para crear un guion de video corto y atractivo en ESPAÑOL.
        
        El resumen debe:
        1. Ser narrativo y fluido (no lista de puntos).
        2. Capturar las ideas principales y más impactantes.
        3. Estar escrito en un tono emocionante y educativo.
        4. Tener una longitud aproximada de 150-200 palabras (apto para un video de 1-2 minutos).
        5. NO usar frases como "En este video..." o "El orador dice...", ve directo al contenido.
        
        Transcripción original (en inglés):
        {transcript_text[:10000]}  # Limitamos a 10k caracteres para no exceder quota del tier gratuito si es muy largo
        
        Guion en Español:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generando resumen con Gemini: {e}")
            return None

    def translate_text(self, text: str) -> str:
        """
        Traduce texto al español manteniendo el contexto.
        """
        prompt = f"""
        Traduce el siguiente texto al español. Mantén un tono natural y técnico si es necesario.
        
        Texto:
        {text}
        
        Traducción:
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error traduciendo con Gemini: {e}")
            return None

    def generate_metadata(self, summary: str):
        """
        Genera Título, Descripción y Tags OPTIMIZADOS para SEO en YouTube.
        """
        prompt = f"""
        Basado en el siguiente guion de video, genera metadatos para YouTube en formato JSON.
        
        Guion:
        {summary}
        
        Formato de respuesta esperado (SOLO JSON):
        {{
            "title": "Título clickbait pero honesto (max 60 car)",
            "description": "Descripción optimizada con palabras clave (primeras 2 lineas son clave)",
            "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            # Limpiar posible markdown ```json ... ```
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            if text.startswith("```"): # Caso generico
                 text = text[3:-3]
                 
            import json
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error generando metadata: {e}")
            # Fallback simple
            return {
                "title": "Novedades de IA - Resumen Diario",
                "description": summary,
                "tags": ["IA", "Inteligencia Artificial", "Tecnología"]
            }
