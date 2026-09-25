from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import crear_token, hash_password, verificar_password
from app.dependencies import get_current_user, get_db
from app.models import Usuario
from app.schemas import Token, UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Autenticación"])


# Esquema auxiliar para recibir el refresh token en JSON
class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post(
    "/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED
)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="El email ya está registrado"
        )

    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        password_hash=hash_password(usuario.password),
        acepto_tratamiento=usuario.acepto_tratamiento,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # form_data.username recibe el email ingresado
    usuario = (
        db.query(Usuario).filter(Usuario.email == form_data.username).first()
    )
    if not usuario or not verificar_password(
        form_data.password, usuario.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = crear_token(
        data={"sub": usuario.email, "rol": usuario.rol, "tipo": "access"},
        expires_delta=timedelta(minutes=settings.ACCESS_MIN),
    )
    refresh_token = crear_token(
        data={"sub": usuario.email, "rol": usuario.rol, "tipo": "refresh"},
        expires_delta=timedelta(minutes=settings.REFRESH_MIN),
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# GET /auth/me: Devuelve los datos del usuario logueado
@router.get("/me", response_model=UsuarioOut)
def obtener_perfil(current_user: Usuario = Depends(get_current_user)):
    return current_user


# POST /auth/refresh: Valida que sea un token de tipo "refresh"
@router.post("/refresh", response_model=Token)
def renovar_token(payload_req: RefreshTokenRequest):
    try:
        payload = jwt.decode(
            payload_req.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        # Verificamos que el token recibido sea de tipo 'refresh' y no de tipo 'access'
        if payload.get("tipo") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El token provisto no es un refresh token válido",
            )

        email: str = payload.get("sub")
        rol: str = payload.get("rol")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )

        nuevo_access_token = crear_token(
            data={"sub": email, "rol": rol, "tipo": "access"},
            expires_delta=timedelta(minutes=settings.ACCESS_MIN),
        )
        nuevo_refresh_token = crear_token(
            data={"sub": email, "rol": rol, "tipo": "refresh"},
            expires_delta=timedelta(minutes=settings.REFRESH_MIN),
        )

        return {
            "access_token": nuevo_access_token,
            "refresh_token": nuevo_refresh_token,
            "token_type": "bearer",
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )