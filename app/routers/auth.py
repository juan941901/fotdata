# Importa las clases y funciones necesarias de FastAPI y otros módulos.
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Importa los módulos de la aplicación.
from .. import crud, schemas
from ..core import security
from ..dependencies import get_db

# Crea un nuevo router de FastAPI.
# Los routers se utilizan para agrupar rutas relacionadas.
router = APIRouter()

# Define la ruta para crear un nuevo usuario.
@router.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en la base de datos.
    """
    # Busca si ya existe un usuario con el mismo email.
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        # Si el email ya está registrado, lanza una excepción HTTP.
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Busca si ya existe un usuario con el mismo nombre de usuario.
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        # Si el nombre de usuario ya está registrado, lanza una excepción HTTP.
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Si no hay conflictos, crea el nuevo usuario.
    return crud.create_user(db=db, user=user)

# Define la ruta para el login de usuarios.
@router.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica a un usuario y devuelve un token de acceso y un token de refresco.
    """
    # Busca al usuario por su nombre de usuario.
    user = crud.get_user_by_username(db, username=form_data.username)
    
    # Si el usuario no existe o la contraseña es incorrecta, lanza una excepción HTTP.
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Si las credenciales son correctas, crea un token de acceso y un token de refresco.
    access_token = security.create_access_token(data={"sub": user.username})
    refresh_token = security.create_refresh_token(data={"sub": user.username})
    
    # Devuelve los tokens.
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}