import os
import logging
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config.settings import YOUTUBE_CHANNEL_ID, BASE_DIR

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly']

class YouTubeClient:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.token_file = BASE_DIR / 'config' / 'token.pickle'
        self.secrets_file = BASE_DIR / 'config' / 'client_secrets.json'
        
    def authenticate(self):
        """Autenticación OAuth 2.0"""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.credentials = pickle.load(token)
                
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                logger.info("Refrescando token de acceso...")
                self.credentials.refresh(Request())
            else:
                if not os.path.exists(self.secrets_file):
                    logger.error(f"No se encontró {self.secrets_file}. No se puede autenticar.")
                    return False
                    
                logger.info("Iniciando flujo de autenticación (requiere interacción)...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.secrets_file, SCOPES)
                self.credentials = flow.run_local_server(port=0)
                
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.credentials, token)
                
        self.service = build('youtube', 'v3', credentials=self.credentials)
        return True

    def upload_video(self, file_path: str, title: str, description: str, tags: list, category_id: str = "28"):
        """
        Sube un video a YouTube.
        Category 28 = Science & Technology
        """
        if not self.service:
            if not self.authenticate():
                logger.error("Fallo autenticación, no se puede subir video.")
                return None
        
        try:
            body = {
                'snippet': {
                    'title': title[:100],  # Max 100 chars
                    'description': description[:5000],  # Max 5000 chars
                    'tags': tags,
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': 'private',  # Empezar como privado por seguridad
                    'selfDeclaredMadeForKids': False
                }
            }
            
            media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
            
            logger.info(f"Iniciando subida: {title}")
            request = self.service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Subido {int(status.progress() * 100)}%")
            
            logger.info(f"Subida completada! Video ID: {response.get('id')}")
            return response.get('id')
            
        except Exception as e:
            logger.error(f"Error subiendo video: {e}")
            return None
