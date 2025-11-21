from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Endereco(BaseModel):
    __tablename__ = "enderecos"

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nome = Column(String(100), nullable=False)  # Ex: Casa, Trabalho
    cep = Column(String(10), nullable=False)
    logradouro = Column(String(200), nullable=False)
    numero = Column(String(10), nullable=False)
    complemento = Column(String(100))
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    principal = Column(Boolean, default=False)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="enderecos")
    pedidos = relationship("Pedido", back_populates="endereco_entrega")
