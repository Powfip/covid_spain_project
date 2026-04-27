import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar variables
load_dotenv()

def get_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")

    # Uso pymysql como driver
    url = f"mysql+pymysql://{user}:{password}@{host}/{db}"
    return create_engine(url)

