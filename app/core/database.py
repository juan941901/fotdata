# Importa las funciones y clases necesarias de SQLAlchemy.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Importa la URL de la base de datos desde el archivo de configuración.
from .config import DATABASE_URL

# Crea el motor de la base de datos.
# El motor es el punto de entrada a la base de datos.
engine = create_engine(
    DATABASE_URL
)

# Crea una clase SessionLocal.
# Esta clase será la que cree las sesiones de la base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea una clase Base.
# Esta clase será la base para todos los modelos de la base de datos.
Base = declarative_base()