"""
Sistema de Autenticação JWT - Versão Simplificada
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional

from app.database.connection import get_db
from app.models.usuario import Usuario, TipoUsuario
from app.config import get_settings

settings = get_settings()

# Router
router = APIRouter(prefix="/auth", tags=["autenticação"])

# Configurações de segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_name: str


class UserRegister(BaseModel):
    nome: str
    email: str
    senha: str
    telefone: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    nome: str
    email: str
    tipo: str
    ativo: bool

    class Config:
        from_attributes = True


# Funções utilitárias
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return user


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    if not current_user.ativo:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user


def get_current_admin_user(
    current_user: Usuario = Depends(get_current_active_user),
) -> Usuario:
    if current_user.tipo != TipoUsuario.ADMIN:
        raise HTTPException(status_code=403, detail="Apenas administradores")
    return current_user


# ENDPOINTS
@router.post("/login", response_model=Token)
def login(
    username: str = Form(), password: str = Form(), db: Session = Depends(get_db)
):
    """Login com email e senha"""
    # Buscar usuário
    user = db.query(Usuario).filter(Usuario.email == username).first()
    if not user or not verify_password(password, user.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    if not user.ativo:
        raise HTTPException(status_code=401, detail="Usuário inativo")

    # Criar token
    token = create_access_token(data={"sub": user.email, "user_id": user.id})

    return Token(access_token=token, user_id=user.id, user_name=user.nome)


@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registrar novo usuário"""
    # Verificar se email já existe
    if db.query(Usuario).filter(Usuario.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # Criar usuário
    hashed_password = get_password_hash(user_data.senha)
    new_user = Usuario(
        nome=user_data.nome,
        email=user_data.email,
        senha_hash=hashed_password,
        telefone=user_data.telefone,
        tipo=TipoUsuario.CLIENTE,
        ativo=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        nome=new_user.nome,
        email=new_user.email,
        tipo=new_user.tipo.value,
        ativo=new_user.ativo,
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: Usuario = Depends(get_current_active_user)):
    """Perfil do usuário logado"""
    return UserResponse(
        id=current_user.id,
        nome=current_user.nome,
        email=current_user.email,
        tipo=current_user.tipo.value,
        ativo=current_user.ativo,
    )


@router.post("/logout")
def logout():
    """Logout (frontend deve descartar o token)"""
    return {"message": "Logout realizado com sucesso"}
