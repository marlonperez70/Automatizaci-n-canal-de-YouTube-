from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import DB_PATH
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Configuración de SQLAlchemy
Base = declarative_base()

# Crear engine con SQLite
# check_same_thread=False es necesario para SQLite con multithreading (como APScheduler)
# Usar as_posix() para evitar problemas con backslashes en Windows y SQLAlchemy URLs
# Usar path absoluto resuelto
abs_db_path = DB_PATH.resolve().as_posix()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{abs_db_path}"
print(f"DEBUG: SQLALCHEMY_DATABASE_URL = {SQLALCHEMY_DATABASE_URL}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Video(Base):
    """Modelo para rastrear videos procesados"""
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    youtube_id = Column(String, unique=True, index=True, nullable=False)
    channel_id = Column(String, index=True)
    title = Column(String)
    url = Column(String)
    duration = Column(Integer)  # En segundos
    views = Column(Integer)
    published_at = Column(DateTime)
    
    # Estados del procesamiento
    status = Column(String, default="pending")  # pending, downloaded, processing, ready, uploaded, error
    error_message = Column(Text, nullable=True)
    
    # Metadata del proceso
    file_path = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Video {self.youtube_id}: {self.title} ({self.status})>"

def init_db():
    """Inicializa la base de datos creando las tablas"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Base de datos inicializada en: {DB_PATH}")
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        raise

def get_db():
    """Generador de sesiones de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
