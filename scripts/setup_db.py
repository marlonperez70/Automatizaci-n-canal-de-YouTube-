import sys
from pathlib import Path

# Agregar root al path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.database import init_db

if __name__ == "__main__":
    print("Inicializando base de datos...")
    init_db()
    print("Base de datos lista.")
