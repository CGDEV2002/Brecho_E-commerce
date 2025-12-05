# Sistema de Carrinho (Sessão)

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
import json

from app.database.connection import get_db
from app.models.produto import Produto

router = APIRouter(prefix="/carrinho", tags=["carrinho"])


class CarrinhoItem(BaseModel):
    produto_id: int
    quantidade: int = 1


class CarrinhoResponse(BaseModel):
    produto_id: int
    nome: str
    preco: float
    quantidade: int
    subtotal: float
    imagem: Optional[str] = None


# Função para gerenciar carrinho na sessão
def get_carrinho(request: Request) -> Dict:
    carrinho_json = request.cookies.get("carrinho", "{}")
    try:
        return json.loads(carrinho_json)
    except:
        return {}


def set_carrinho(response: Response, carrinho: Dict):
    response.set_cookie("carrinho", json.dumps(carrinho), max_age=86400 * 7)  # 7 dias


@router.post("/adicionar")
def adicionar_ao_carrinho(
    item: CarrinhoItem,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Adicionar produto ao carrinho"""
    # Verificar se produto existe
    produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Para brechó, quantidade sempre 1
    carrinho = get_carrinho(request)
    carrinho[str(item.produto_id)] = 1  # Sempre quantidade 1 para brechó
    set_carrinho(response, carrinho)

    return {"message": "Produto adicionado ao carrinho", "total_items": len(carrinho)}


@router.delete("/remover/{produto_id}")
def remover_do_carrinho(produto_id: int, request: Request, response: Response):
    """Remover produto do carrinho"""
    carrinho = get_carrinho(request)
    if str(produto_id) in carrinho:
        del carrinho[str(produto_id)]
        set_carrinho(response, carrinho)
        return {"message": "Produto removido do carrinho"}

    raise HTTPException(status_code=404, detail="Produto não está no carrinho")


@router.get("/", response_model=List[CarrinhoResponse])
def ver_carrinho(request: Request, db: Session = Depends(get_db)):
    """Ver itens do carrinho"""
    carrinho = get_carrinho(request)
    if not carrinho:
        return []

    itens = []
    for produto_id, quantidade in carrinho.items():
        produto = db.query(Produto).filter(Produto.id == int(produto_id)).first()
        if produto:
            itens.append(
                CarrinhoResponse(
                    produto_id=produto.id,
                    nome=produto.nome,
                    preco=produto.preco_venda,
                    quantidade=quantidade,
                    subtotal=produto.preco_venda * quantidade,
                    imagem=produto.imagem_principal,
                )
            )

    return itens


@router.get("/total")
def total_carrinho(request: Request, db: Session = Depends(get_db)):
    """Calcular total do carrinho"""
    carrinho = get_carrinho(request)
    total = 0
    total_items = 0

    for produto_id, quantidade in carrinho.items():
        produto = db.query(Produto).filter(Produto.id == int(produto_id)).first()
        if produto:
            total += produto.preco_venda * quantidade
            total_items += quantidade

    return {"total": total, "total_items": total_items, "items_count": len(carrinho)}


@router.delete("/limpar")
def limpar_carrinho(response: Response):
    """Limpar todo o carrinho"""
    response.delete_cookie("carrinho")
    return {"message": "Carrinho limpo"}


@router.get("/whatsapp")
def gerar_link_whatsapp(request: Request, db: Session = Depends(get_db)):
    """Gerar link do WhatsApp com pedido"""
    carrinho = get_carrinho(request)
    if not carrinho:
        raise HTTPException(status_code=400, detail="Carrinho vazio")

    # Montar mensagem
    mensagem = "🛍️ *Pedido do Brechó Cata Roupas* 🛍️\n\n"
    total = 0

    for produto_id, quantidade in carrinho.items():
        produto = db.query(Produto).filter(Produto.id == int(produto_id)).first()
        if produto:
            subtotal = produto.preco_venda * quantidade
            mensagem += f"• {produto.nome}\n"
            mensagem += f"  💰 R$ {produto.preco_venda:.2f}\n\n"
            total += subtotal

    mensagem += f"💯 *TOTAL: R$ {total:.2f}*\n\n"
    mensagem += "📞 Gostaria de finalizar este pedido!\n"
    mensagem += "🏠 Preciso combinar entrega/retirada"

    # URL encode da mensagem
    import urllib.parse

    mensagem_encoded = urllib.parse.quote(mensagem)

    # Número do WhatsApp - ALTERE AQUI PARA O NÚMERO REAL DO BRECHÓ
    whatsapp_number = "5511999999999"  # Formato: 55 + DDD + número (sem espaços)
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={mensagem_encoded}"

    return {"whatsapp_url": whatsapp_url, "mensagem": mensagem, "total": total}
