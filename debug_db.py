import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from src.utils.database import engine
from config.settings import DB_PATH

# Reproduce imports from run_daily.py
import time
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from src.utils.logger import setup_logger
from src.scraper.youtube_scraper import YouTubeScraper
from src.processor.gemini_client import GeminiClient
from src.media.tts_generator import TTSGenerator
from src.media.video_composer import VideoComposer
from src.publisher.youtube_client import YouTubeClient


print(f"DB_PATH raw: {DB_PATH}")
print(f"DB_PATH as_posix: {DB_PATH.as_posix()}")
# Accessing private attribute for debugging purposes, or just reconstruction
print(f"Engine URL: {engine.url}")

try:
    with engine.connect() as conn:
        print("Successfully connected to the database!")
except Exception as e:
    print(f"Failed to connect: {e}")

