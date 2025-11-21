from sqlalchemy import Column, String, Boolean, Integer, Float, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class StatusProduto(enum.Enum):
    DISPONIVEL = "disponivel"
    VENDIDO = "vendido"
    RESERVADO = "reservado"
    INATIVO = "inativo"


class CondicaoProduto(enum.Enum):
    NOVO = "novo"
    SEMI_NOVO = "semi_novo"
    USADO_BOM = "usado_bom"
    USADO_REGULAR = "usado_regular"


class TamanhoProduto(enum.Enum):
    PP = "PP"
    P = "P"
    M = "M"
    G = "G"
    GG = "GG"
    XGG = "XGG"
    UNICO = "unico"


class Produto(BaseModel):
    __tablename__ = "produtos"

    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    marca = Column(String(100))
    cor_principal = Column(String(50))
    tamanho = Column(Enum(TamanhoProduto), nullable=False)
    condicao = Column(Enum(CondicaoProduto), nullable=False)
    preco_original = Column(Float)  # Preço quando novo
    preco_venda = Column(Float, nullable=False)
    status = Column(Enum(StatusProduto), default=StatusProduto.DISPONIVEL)

    # Específico para brechó
    ano_aproximado = Column(Integer)  # Ano aproximado da peça
    material = Column(String(100))  # Algodão, poliéster, etc.
    cuidados = Column(Text)  # Instruções de lavagem
    historia_peca = Column(Text)  # História da peça, se houver

    # Imagens (URLs separadas por vírgula ou JSON)
    imagem_principal = Column(String(500))
    imagens_adicionais = Column(Text)  # JSON com URLs das imagens

    # Relacionamentos
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    categoria = relationship("Categoria")
    itens_pedido = relationship("ItemPedido", back_populates="produto")

    # Métricas
    visualizacoes = Column(Integer, default=0)
    favoritado = Column(Integer, default=0)
