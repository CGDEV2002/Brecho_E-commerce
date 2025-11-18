from sqlalchemy import Column, String, Boolean, Integer
from .base import BaseModel

class Categoria(BaseModel):
    __tablename__ = "categorias"

    nome = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(200))
    ativa = Column(Boolean, default=True)
    ordem_exibicao = Column(Integer, default=0)