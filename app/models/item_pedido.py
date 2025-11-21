from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class ItemPedido(BaseModel):
    __tablename__ = "itens_pedido"

    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)

    # Para brechó, quantidade sempre será 1 (peça única)
    quantidade = Column(Integer, default=1, nullable=False)
    preco_unitario = Column(Float, nullable=False)  # Preço no momento da compra
    subtotal = Column(Float, nullable=False)

    # Relacionamentos
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_pedido")

    def calcular_subtotal(self):
        """Calcula o subtotal do item"""
        self.subtotal = self.quantidade * self.preco_unitario
        return self.subtotal
