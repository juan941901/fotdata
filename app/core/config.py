import os

# URL de conexión a la base de datos PostgreSQL.
# Formato: postgresql://<usuario>:<contraseña>@<host>:<puerto>/<nombre_base_de_datos>
# Es importante cambiar estos valores por los de tu entorno de producción.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/fotdata")

# --- Configuración de JWT ---

# Clave secreta para firmar los tokens JWT.
# Esta clave debe ser secreta y compleja. En producción, cárgala desde una variable de entorno.
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key")

# Algoritmo utilizado para firmar los tokens JWT.
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Tiempo de expiración del token de acceso en minutos.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Tiempo de expiración del token de refresco en días.
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# --- Configuración para el cliente Gemini ---
# Variables de entorno esperadas:
# GEMINI_API_KEY (required): clave de API para el servicio Gemini.
# GEMINI_ENDPOINT: endpoint HTTP para realizar la llamada (prefix o full URL según provider).
# GEMINI_MODEL: nombre del modelo por defecto.

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_ENDPOINT = os.getenv("GEMINI_ENDPOINT", "https://api.gemini.example/v1/generate")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1")
