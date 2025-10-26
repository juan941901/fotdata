from .core.database import SessionLocal
from .services.gemini_client import GeminiClient


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_gemini_client():
    """Dependency that yields an async GeminiClient and closes it after use.

    Use like: client: GeminiClient = Depends(get_gemini_client)
    """
    client = GeminiClient()
    try:
        yield client
    finally:
        try:
            await client.aclose()
        except Exception:
            pass
