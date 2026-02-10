import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config.settings import LOG_DIR, LOG_LEVEL

def setup_logger(name: str) -> logging.Logger:
    """
    Configura y retorna un logger estandarizado.
    
    Args:
        name (str): Nombre del logger (usualmente __name__)
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # Evitar duplicación de handlers
    if logger.hasHandlers():
        return logger
        
    # Formato de logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler de consola (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler de archivo (rotativo: 10MB, max 5 backups)
    log_file = LOG_DIR / "app.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
