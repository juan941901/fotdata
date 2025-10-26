1. Crear y activar un entorno virtual (recomendado):

```bash
python3 -m venv env
source env/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno (ejemplo `.env`):

```bash
export DATABASE_URL="postgresql://user:pass@localhost/fotdata"
export GEMINI_API_KEY="tu_api_key"
export GEMINI_ENDPOINT="https://api.tu-proveedor/v1/generate"
export GEMINI_EMBED_ENDPOINT="https://api.tu-proveedor/v1/embeddings"
```

4. Ejecutar la aplicación en modo desarrollo:

```bash
uvicorn app.main:app --reload
```

## Estructura de carpetas y por qué se organiza así

La organización del proyecto está pensada para separar responsabilidades y facilitar mantenimiento, pruebas y escalabilidad. A continuación se explica cada carpeta principal y el motivo de su existencia:

- `app/` — Contiene el código de la aplicación FastAPI. Mantener todo bajo `app` ayuda a que la raíz del repositorio sea limpia y facilita importar el paquete como un módulo.

- `app/core/` — Código de infraestructura y configuración central (conexión a la base de datos, seguridad, ajustes globales). Aquí colocamos la lógica que es transversal a toda la aplicación y que no pertenece a una entidad concreta.

- `app/models/` — Definiciones de modelos SQLAlchemy (esquema de la base de datos). Separar los modelos facilita cambiar la capa de persistencia sin mezclarla con la lógica de negocio.

- `app/schemas/` — Modelos Pydantic que definen los contratos de entrada/salida de la API. Mantenerlos separados permite validación clara y evita acoplar los modelos de DB con los contratos de la API.

- `app/routers/` — Rutas (endpoints) agrupadas por dominio (auth, gemini, etc.). Usar routers permite modularizar la API y registrar rutas en `app.main` de forma ordenada.

- `app/services/` — Clientes externos, adaptadores y lógica relacionada con servicios (por ejemplo, cliente Gemini, generación de embeddings). Los services encapsulan las integraciones externas y políticas como retries y timeouts.

- `app/crud.py` — Operaciones CRUD reutilizables que interactúan con los modelos y la base de datos. Centralizar estas funciones reduce duplicación en los endpoints.

- `app/dependencies.py` — Dependencias de FastAPI (inyección de DB, cliente Gemini, etc.). Aquí definimos factories/cleanup para usar con `Depends()`.

- `app/core/config.py` — Variables de configuración que pueden leerse desde variables de entorno. Mantener la configuración en un único sitio facilita pruebas y despliegue.

- `env/` — Entorno virtual local (no versionado normalmente). Contiene el Python y paquetes cuando se activa el entorno de desarrollo.

- `requirements.txt` — Lista de dependencias del proyecto para instalación reproducible.

- `tests/` — Pruebas unitarias e integradas. Tener un directorio `tests` con la misma estructura lógica ayuda a encontrar rápidamente las pruebas relacionadas con cada componente.

Esta disposición sigue principios de separación de responsabilidades (SoC) y ayuda a mantener un flujo de trabajo claro: los routers manejan HTTP, los schemas validan datos, los services encapsulan integraciones externas, y los models + crud gestionan la persistencia.

Si quieres que adapte la estructura (por ejemplo, usar un layout hexagonal más estricto, o mover `crud` dentro de cada módulo), dímelo y lo ajusto según las necesidades del equipo.
