# Painel Admin

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
from PIL import Image

from app.database.connection import get_db
from app.models.produto import Produto, StatusProduto, CondicaoProduto, TamanhoProduto
from app.models.categoria import Categoria
from app.models.usuario import Usuario
from app.routes.auth import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminStats(BaseModel):
    total_produtos: int
    produtos_disponiveis: int
    produtos_vendidos: int
    total_categorias: int
    total_usuarios: int


class ProdutoAdmin(BaseModel):
    nome: str
    descricao: Optional[str] = None
    marca: Optional[str] = None
    cor_principal: Optional[str] = None
    tamanho: TamanhoProduto
    condicao: CondicaoProduto
    preco_original: Optional[float] = None
    preco_venda: float
    categoria_id: int
    material: Optional[str] = None
    historia_peca: Optional[str] = None


def save_admin_image(file: UploadFile) -> str:
    """Salvar imagem do admin"""
    upload_dir = "app/static/images/produtos"
    os.makedirs(upload_dir, exist_ok=True)

    file_extension = file.filename.split(".")[-1].lower()
    filename = f"admin_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Redimensionar
    with Image.open(file_path) as img:
        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        img.save(file_path, optimize=True, quality=85)

    return f"/static/images/produtos/{filename}"


@router.get("/dashboard", response_model=AdminStats)
def admin_dashboard(
    admin: Usuario = Depends(get_current_admin_user), db: Session = Depends(get_db)
):
    """Dashboard com estatísticas"""
    return AdminStats(
        total_produtos=db.query(Produto).count(),
        produtos_disponiveis=db.query(Produto)
        .filter(Produto.status == StatusProduto.DISPONIVEL)
        .count(),
        produtos_vendidos=db.query(Produto)
        .filter(Produto.status == StatusProduto.VENDIDO)
        .count(),
        total_categorias=db.query(Categoria).count(),
        total_usuarios=db.query(Usuario).count(),
    )


@router.post("/produtos", status_code=201)
def criar_produto_admin(
    nome: str = Form(),
    descricao: str = Form(None),
    marca: str = Form(None),
    cor_principal: str = Form(None),
    tamanho: TamanhoProduto = Form(),
    condicao: CondicaoProduto = Form(),
    preco_original: float = Form(None),
    preco_venda: float = Form(),
    categoria_id: int = Form(),
    material: str = Form(None),
    historia_peca: str = Form(None),
    imagem: UploadFile = File(None),
    admin: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Criar novo produto (admin)"""

    # Verificar categoria
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=400, detail="Categoria inválida")

    # Criar produto
    produto = Produto(
        nome=nome,
        descricao=descricao,
        marca=marca,
        cor_principal=cor_principal,
        tamanho=tamanho,
        condicao=condicao,
        preco_original=preco_original,
        preco_venda=preco_venda,
        categoria_id=categoria_id,
        material=material,
        historia_peca=historia_peca,
    )

    # Salvar imagem se fornecida
    if imagem and imagem.filename:
        produto.imagem_principal = save_admin_image(imagem)

    db.add(produto)
    db.commit()
    db.refresh(produto)

    return {"message": "Produto criado", "produto_id": produto.id}


@router.put("/produtos/{produto_id}")
def atualizar_produto_admin(
    produto_id: int,
    nome: str = Form(None),
    descricao: str = Form(None),
    marca: str = Form(None),
    preco_venda: float = Form(None),
    status: StatusProduto = Form(None),
    admin: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Atualizar produto (admin)"""

    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Atualizar campos fornecidos
    if nome:
        produto.nome = nome
    if descricao:
        produto.descricao = descricao
    if marca:
        produto.marca = marca
    if preco_venda:
        produto.preco_venda = preco_venda
    if status:
        produto.status = status

    db.commit()
    return {"message": "Produto atualizado"}


@router.delete("/produtos/{produto_id}")
def deletar_produto_admin(
    produto_id: int,
    admin: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Deletar produto (admin)"""

    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.status = StatusProduto.INATIVO
    db.commit()

    return {"message": "Produto removido"}


@router.get("/produtos")
def listar_produtos_admin(
    skip: int = 0,
    limit: int = 50,
    admin: Usuario = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Listar produtos para admin"""

    produtos = db.query(Produto).offset(skip).limit(limit).all()
    result = []

    for produto in produtos:
        result.append(
            {
                "id": produto.id,
                "nome": produto.nome,
                "preco_venda": produto.preco_venda,
                "status": produto.status.value,
                "categoria": produto.categoria.nome,
                "created_at": produto.created_at.strftime("%d/%m/%Y"),
                "imagem": produto.imagem_principal,
            }
        )

    return result
