"""
CRUD completo de produtos para o Brechó Cata Roupas
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import os
import uuid
from PIL import Image

from app.database.connection import get_db
from app.models.produto import Produto, StatusProduto, CondicaoProduto, TamanhoProduto
from app.models.categoria import Categoria

# Router para produtos
router = APIRouter(prefix="/produtos", tags=["produtos"])


# Schemas Pydantic
class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=200)
    descricao: Optional[str] = None
    marca: Optional[str] = Field(None, max_length=100)
    cor_principal: Optional[str] = Field(None, max_length=50)
    tamanho: TamanhoProduto
    condicao: CondicaoProduto
    preco_original: Optional[float] = Field(None, gt=0)
    preco_venda: float = Field(..., gt=0)
    categoria_id: int
    ano_aproximado: Optional[int] = Field(None, ge=1950, le=2025)
    material: Optional[str] = Field(None, max_length=100)
    cuidados: Optional[str] = None
    historia_peca: Optional[str] = None


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = None
    marca: Optional[str] = Field(None, max_length=100)
    cor_principal: Optional[str] = Field(None, max_length=50)
    tamanho: Optional[TamanhoProduto] = None
    condicao: Optional[CondicaoProduto] = None
    preco_original: Optional[float] = Field(None, gt=0)
    preco_venda: Optional[float] = Field(None, gt=0)
    status: Optional[StatusProduto] = None
    categoria_id: Optional[int] = None
    ano_aproximado: Optional[int] = Field(None, ge=1950, le=2025)
    material: Optional[str] = Field(None, max_length=100)
    cuidados: Optional[str] = None
    historia_peca: Optional[str] = None


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    marca: Optional[str]
    cor_principal: Optional[str]
    tamanho: TamanhoProduto
    condicao: CondicaoProduto
    preco_original: Optional[float]
    preco_venda: float
    status: StatusProduto
    categoria_id: int
    categoria_nome: Optional[str] = None
    ano_aproximado: Optional[int]
    material: Optional[str]
    cuidados: Optional[str]
    historia_peca: Optional[str]
    imagem_principal: Optional[str]
    imagens_adicionais: Optional[str]
    visualizacoes: int
    favoritado: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ProdutoFilter(BaseModel):
    categoria_id: Optional[int] = None
    tamanho: Optional[TamanhoProduto] = None
    condicao: Optional[CondicaoProduto] = None
    status: Optional[StatusProduto] = None
    preco_min: Optional[float] = None
    preco_max: Optional[float] = None
    marca: Optional[str] = None
    cor: Optional[str] = None


# Funções auxiliares
def save_image(file: UploadFile, produto_id: int) -> str:
    """Salva imagem do produto e retorna o caminho"""
    # Criar diretório se não existir
    upload_dir = "app/static/images/produtos"
    os.makedirs(upload_dir, exist_ok=True)

    # Gerar nome único
    file_extension = file.filename.split(".")[-1].lower()
    filename = f"produto_{produto_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    # Salvar arquivo
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Redimensionar imagem
    with Image.open(file_path) as img:
        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        img.save(file_path, optimize=True, quality=85)

    return f"/static/images/produtos/{filename}"


# ENDPOINTS


@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    categoria_id: Optional[int] = Query(None),
    tamanho: Optional[TamanhoProduto] = Query(None),
    condicao: Optional[CondicaoProduto] = Query(None),
    status: Optional[StatusProduto] = Query(StatusProduto.DISPONIVEL),
    preco_min: Optional[float] = Query(None, ge=0),
    preco_max: Optional[float] = Query(None, ge=0),
    marca: Optional[str] = Query(None),
    busca: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lista produtos com filtros opcionais"""
    query = db.query(Produto).join(Categoria, Produto.categoria_id == Categoria.id)

    # Aplicar filtros
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)

    if tamanho:
        query = query.filter(Produto.tamanho == tamanho)

    if condicao:
        query = query.filter(Produto.condicao == condicao)

    if status:
        query = query.filter(Produto.status == status)

    if preco_min:
        query = query.filter(Produto.preco_venda >= preco_min)

    if preco_max:
        query = query.filter(Produto.preco_venda <= preco_max)

    if marca:
        query = query.filter(Produto.marca.ilike(f"%{marca}%"))

    if busca:
        query = query.filter(
            or_(
                Produto.nome.ilike(f"%{busca}%"),
                Produto.descricao.ilike(f"%{busca}%"),
                Produto.marca.ilike(f"%{busca}%"),
            )
        )

    # Ordenar por criação (mais recentes primeiro)
    query = query.order_by(Produto.created_at.desc())

    produtos = query.offset(skip).limit(limit).all()

    # Adicionar nome da categoria
    result = []
    for produto in produtos:
        produto_dict = produto.__dict__.copy()
        produto_dict["categoria_nome"] = produto.categoria.nome
        produto_dict["created_at"] = produto.created_at.isoformat()
        produto_dict["updated_at"] = produto.updated_at.isoformat()
        result.append(ProdutoResponse(**produto_dict))

    return result


@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """Obtém um produto específico e incrementa visualizações"""
    produto = (
        db.query(Produto)
        .join(Categoria, Produto.categoria_id == Categoria.id)
        .filter(Produto.id == produto_id)
        .first()
    )

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Incrementar visualizações
    produto.visualizacoes += 1
    db.commit()

    # Adicionar nome da categoria
    produto_dict = produto.__dict__.copy()
    produto_dict["categoria_nome"] = produto.categoria.nome
    produto_dict["created_at"] = produto.created_at.isoformat()
    produto_dict["updated_at"] = produto.updated_at.isoformat()

    return ProdutoResponse(**produto_dict)


@router.post("/", response_model=ProdutoResponse, status_code=201)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    """Cria um novo produto"""

    # Verificar se categoria existe
    categoria = db.query(Categoria).filter(Categoria.id == produto.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=400, detail="Categoria não encontrada")

    # Criar produto
    db_produto = Produto(**produto.dict())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)

    # Adicionar nome da categoria
    produto_dict = db_produto.__dict__.copy()
    produto_dict["categoria_nome"] = categoria.nome
    produto_dict["created_at"] = db_produto.created_at.isoformat()
    produto_dict["updated_at"] = db_produto.updated_at.isoformat()

    return ProdutoResponse(**produto_dict)


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int, produto_update: ProdutoUpdate, db: Session = Depends(get_db)
):
    """Atualiza um produto existente"""

    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Verificar categoria se foi informada
    if produto_update.categoria_id:
        categoria = (
            db.query(Categoria)
            .filter(Categoria.id == produto_update.categoria_id)
            .first()
        )
        if not categoria:
            raise HTTPException(status_code=400, detail="Categoria não encontrada")

    # Atualizar campos fornecidos
    update_data = produto_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(produto, field, value)

    db.commit()
    db.refresh(produto)

    # Buscar categoria para adicionar nome
    categoria = db.query(Categoria).filter(Categoria.id == produto.categoria_id).first()

    # Adicionar nome da categoria
    produto_dict = produto.__dict__.copy()
    produto_dict["categoria_nome"] = categoria.nome if categoria else None
    produto_dict["created_at"] = produto.created_at.isoformat()
    produto_dict["updated_at"] = produto.updated_at.isoformat()

    return ProdutoResponse(**produto_dict)


@router.delete("/{produto_id}")
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Deleta um produto (soft delete - marca como inativo)"""

    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Soft delete - marca como inativo
    produto.status = StatusProduto.INATIVO
    db.commit()

    return {"message": "Produto removido com sucesso"}


@router.post("/{produto_id}/imagem-principal")
def upload_imagem_principal(
    produto_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Upload da imagem principal do produto"""

    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Validar tipo de arquivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")

    # Salvar imagem
    try:
        image_path = save_image(file, produto_id)
        produto.imagem_principal = image_path
        db.commit()

        return {"message": "Imagem principal atualizada", "url": image_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar imagem: {str(e)}")


@router.post("/{produto_id}/favoritar")
def favoritar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Adiciona produto aos favoritos (incrementa contador)"""

    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.favoritado += 1
    db.commit()

    return {"message": "Produto favoritado", "total_favoritos": produto.favoritado}


@router.get("/categoria/{categoria_id}", response_model=List[ProdutoResponse])
def produtos_por_categoria(
    categoria_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista produtos de uma categoria específica"""

    # Verificar se categoria existe
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    produtos = (
        db.query(Produto)
        .filter(
            and_(
                Produto.categoria_id == categoria_id,
                Produto.status == StatusProduto.DISPONIVEL,
            )
        )
        .order_by(Produto.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Adicionar nome da categoria
    result = []
    for produto in produtos:
        produto_dict = produto.__dict__.copy()
        produto_dict["categoria_nome"] = categoria.nome
        produto_dict["created_at"] = produto.created_at.isoformat()
        produto_dict["updated_at"] = produto.updated_at.isoformat()
        result.append(ProdutoResponse(**produto_dict))

    return result


@router.get("/mais-vistos/", response_model=List[ProdutoResponse])
def produtos_mais_vistos(
    limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)
):
    """Lista produtos mais visualizados"""

    produtos = (
        db.query(Produto)
        .filter(Produto.status == StatusProduto.DISPONIVEL)
        .order_by(Produto.visualizacoes.desc())
        .limit(limit)
        .all()
    )

    result = []
    for produto in produtos:
        produto_dict = produto.__dict__.copy()
        produto_dict["categoria_nome"] = produto.categoria.nome
        produto_dict["created_at"] = produto.created_at.isoformat()
        produto_dict["updated_at"] = produto.updated_at.isoformat()
        result.append(ProdutoResponse(**produto_dict))

    return result


@router.get("/lancamentos/", response_model=List[ProdutoResponse])
def lancamentos(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Lista produtos mais recentes (lançamentos)"""

    produtos = (
        db.query(Produto)
        .filter(Produto.status == StatusProduto.DISPONIVEL)
        .order_by(Produto.created_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for produto in produtos:
        produto_dict = produto.__dict__.copy()
        produto_dict["categoria_nome"] = produto.categoria.nome
        produto_dict["created_at"] = produto.created_at.isoformat()
        produto_dict["updated_at"] = produto.updated_at.isoformat()
        result.append(ProdutoResponse(**produto_dict))

    return result
