from sqlalchemy import Column, String, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class TipoUsuario(enum.Enum):
    CLIENTE = "cliente"
    ADMIN = "admin"


class Usuario(BaseModel):
    __tablename__ = "usuarios"

    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    telefone = Column(String(20))
    cpf = Column(String(14), unique=True)
    data_nascimento = Column(DateTime)
    tipo = Column(Enum(TipoUsuario), default=TipoUsuario.CLIENTE)
    ativo = Column(Boolean, default=True)
    email_verificado = Column(Boolean, default=False)

    # Relacionamentos
    enderecos = relationship(
        "Endereco", back_populates="usuario", cascade="all, delete-orphan"
    )
    pedidos = relationship("Pedido", back_populates="usuario")
