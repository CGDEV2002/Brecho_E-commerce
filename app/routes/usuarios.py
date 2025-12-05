"""
Rotas para gerenciamento de usuários
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from app.database.connection import get_db
from app.models.usuario import Usuario, TipoUsuario
from app.routes.auth import (
    get_current_active_user,
    get_current_admin_user,
    get_password_hash,
)

# Router para usuários
router = APIRouter(prefix="/usuarios", tags=["usuários"])


# Schemas
class UserUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    cpf: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: Optional[str]
    cpf: Optional[str]
    tipo: TipoUsuario
    ativo: bool
    email_verificado: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    senha_atual: str
    senha_nova: str


# ENDPOINTS


@router.get("/perfil", response_model=UserResponse)
def get_user_profile(current_user: Usuario = Depends(get_current_active_user)):
    """Obtém perfil do usuário logado"""
    return UserResponse.from_orm(current_user)


@router.put("/perfil", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Atualiza perfil do usuário logado"""

    # Verificar CPF se fornecido
    if user_update.cpf and user_update.cpf != current_user.cpf:
        existing_cpf = (
            db.query(Usuario)
            .filter(Usuario.cpf == user_update.cpf, Usuario.id != current_user.id)
            .first()
        )
        if existing_cpf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado por outro usuário",
            )

    # Atualizar campos fornecidos
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return UserResponse.from_orm(current_user)


@router.post("/alterar-senha")
def change_password(
    password_data: PasswordChange,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Altera senha do usuário"""
    from app.routes.auth import verify_password

    # Verificar senha atual
    if not verify_password(password_data.senha_atual, current_user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta"
        )

    # Atualizar senha
    current_user.senha_hash = get_password_hash(password_data.senha_nova)
    db.commit()

    return {"message": "Senha alterada com sucesso"}


# ENDPOINTS ADMIN


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 50,
    admin_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Lista todos os usuários (apenas admin)"""
    users = db.query(Usuario).offset(skip).limit(limit).all()
    return [UserResponse.from_orm(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    admin_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Obtém usuário por ID (apenas admin)"""
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    return UserResponse.from_orm(user)


@router.put("/{user_id}/ativo")
def toggle_user_status(
    user_id: int,
    ativo: bool,
    admin_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Ativa/desativa usuário (apenas admin)"""
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    user.ativo = ativo
    db.commit()

    status_text = "ativado" if ativo else "desativado"
    return {"message": f"Usuário {status_text} com sucesso"}


@router.put("/{user_id}/tipo")
def change_user_type(
    user_id: int,
    tipo: TipoUsuario,
    admin_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Altera tipo do usuário (apenas admin)"""
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    user.tipo = tipo
    db.commit()

    return {"message": f"Tipo do usuário alterado para {tipo.value}"}


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    admin_user: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Remove usuário (apenas admin)"""
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    # Soft delete - marca como inativo
    user.ativo = False
    db.commit()

    return {"message": "Usuário removido com sucesso"}
