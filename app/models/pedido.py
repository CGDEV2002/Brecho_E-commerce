from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum
from datetime import datetime


class StatusPedido(enum.Enum):
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    PREPARANDO = "preparando"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class FormaPagamento(enum.Enum):
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    BOLETO = "boleto"


class Pedido(BaseModel):
    __tablename__ = "pedidos"

    numero_pedido = Column(String(20), unique=True, nullable=False)  # Ex: BR2024001
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    endereco_entrega_id = Column(Integer, ForeignKey("enderecos.id"), nullable=False)

    # Status e datas
    status = Column(Enum(StatusPedido), default=StatusPedido.PENDENTE)
    data_confirmacao = Column(DateTime)
    data_envio = Column(DateTime)
    data_entrega = Column(DateTime)

    # Valores
    subtotal = Column(Float, nullable=False)
    taxa_entrega = Column(Float, default=0.0)
    desconto = Column(Float, default=0.0)
    total = Column(Float, nullable=False)

    # Pagamento
    forma_pagamento = Column(Enum(FormaPagamento))
    status_pagamento = Column(String(50), default="pendente")
    id_transacao = Column(String(100))  # ID do gateway de pagamento

    # Entrega
    codigo_rastreamento = Column(String(50))
    transportadora = Column(String(100))
    observacoes = Column(Text)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="pedidos")
    endereco_entrega = relationship("Endereco", back_populates="pedidos")
    itens = relationship(
        "ItemPedido", back_populates="pedido", cascade="all, delete-orphan"
    )

    def gerar_numero_pedido(self):
        """Gera número único do pedido"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"BR{timestamp}"
