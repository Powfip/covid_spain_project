import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar las rutas
try: # Para usar en ficheros .py
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError: # si no es fichero .py, es un notebook utiliza ese metodo
    BASE_DIR = Path.cwd().parent

#Demas rutas
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DB_DIR = BASE_DIR / "database"
FIGURES_DIR = BASE_DIR / "figures"

# Me aseguro que existen las carpetas
for path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, DB_DIR, FIGURES_DIR]:
    path.mkdir(parents=True,exist_ok=True)

# Confirmamos con un print que las rutas fueron creadas
print(f"Rutas Creadas correctamente.")