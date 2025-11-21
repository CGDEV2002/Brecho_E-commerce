#!/usr/bin/env python3
"""
Script para popular dados iniciais do Brechó Cata Roupas

Execute com: poetry run python scripts/populate_data.py
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from sqlalchemy.orm import sessionmaker
from app.database.connection import engine
from app.models import (
    Categoria,
    Usuario,
    Endereco,
    Produto,
    TipoUsuario,
    StatusProduto,
    CondicaoProduto,
    TamanhoProduto,
)
import hashlib
from datetime import datetime

# Criar sessão
Session = sessionmaker(bind=engine)


def hash_password(password: str) -> str:
    """Hash da senha usando SHA256 (temporário para desenvolvimento)"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_categories():
    """Cria categorias iniciais para o brechó"""
    session = Session()

    categorias = [
        {
            "nome": "Blusas",
            "descricao": "Blusas femininas e masculinas",
            "ordem_exibicao": 1,
        },
        {
            "nome": "Calças",
            "descricao": "Calças jeans, sociais e casuais",
            "ordem_exibicao": 2,
        },
        {
            "nome": "Vestidos",
            "descricao": "Vestidos casuais e sociais",
            "ordem_exibicao": 3,
        },
        {"nome": "Saias", "descricao": "Saias de todos os tipos", "ordem_exibicao": 4},
        {"nome": "Casacos", "descricao": "Casacos e jaquetas", "ordem_exibicao": 5},
        {
            "nome": "Acessórios",
            "descricao": "Bolsas, cintos e acessórios",
            "ordem_exibicao": 6,
        },
        {
            "nome": "Calçados",
            "descricao": "Sapatos, sandálias e tênis",
            "ordem_exibicao": 7,
        },
    ]

    for cat_data in categorias:
        # Verifica se já existe
        existing = session.query(Categoria).filter_by(nome=cat_data["nome"]).first()
        if not existing:
            categoria = Categoria(**cat_data)
            session.add(categoria)
            print(f"✅ Categoria criada: {cat_data['nome']}")
        else:
            print(f"ℹ️  Categoria já existe: {cat_data['nome']}")

    session.commit()
    session.close()


def create_admin_user():
    """Cria usuário administrador"""
    session = Session()

    # Verifica se admin já existe
    admin = session.query(Usuario).filter_by(email="admin@cataroupas.com").first()

    if not admin:
        admin = Usuario(
            nome="Administrador Cata Roupas",
            email="admin@cataroupas.com",
            senha_hash=hash_password("admin123"),
            telefone="(11) 99999-9999",
            tipo=TipoUsuario.ADMIN,
            ativo=True,
            email_verificado=True,
        )
        session.add(admin)
        session.commit()
        print("✅ Usuário administrador criado")
        print("   Email: admin@cataroupas.com")
        print("   Senha: admin123")
    else:
        print("ℹ️  Usuário administrador já existe")

    session.close()


def create_sample_products():
    """Cria produtos de exemplo"""
    session = Session()

    # Busca categorias
    cat_blusas = session.query(Categoria).filter_by(nome="Blusas").first()
    cat_calcas = session.query(Categoria).filter_by(nome="Calças").first()
    cat_vestidos = session.query(Categoria).filter_by(nome="Vestidos").first()

    produtos_exemplo = [
        {
            "nome": "Blusa Vintage Floral",
            "descricao": "Linda blusa vintage com estampa floral, perfeita para ocasiões especiais",
            "marca": "Zara",
            "cor_principal": "Azul",
            "tamanho": TamanhoProduto.M,
            "condicao": CondicaoProduto.SEMI_NOVO,
            "preco_original": 89.90,
            "preco_venda": 45.00,
            "ano_aproximado": 2020,
            "material": "Viscose",
            "categoria_id": cat_blusas.id if cat_blusas else 1,
            "historia_peca": "Peça pouco usada, comprada em viagem à Europa",
        },
        {
            "nome": "Calça Jeans Skinny",
            "descricao": "Calça jeans skinny de excelente qualidade",
            "marca": "Levi's",
            "cor_principal": "Azul Escuro",
            "tamanho": TamanhoProduto.P,
            "condicao": CondicaoProduto.USADO_BOM,
            "preco_original": 199.90,
            "preco_venda": 85.00,
            "ano_aproximado": 2019,
            "material": "Algodão e Elastano",
            "categoria_id": cat_calcas.id if cat_calcas else 2,
        },
        {
            "nome": "Vestido Midi Estampado",
            "descricao": "Vestido midi com estampa tropical, muito confortável",
            "marca": "Farm",
            "cor_principal": "Verde",
            "tamanho": TamanhoProduto.G,
            "condicao": CondicaoProduto.NOVO,
            "preco_original": 159.90,
            "preco_venda": 120.00,
            "ano_aproximado": 2023,
            "material": "Modal",
            "categoria_id": cat_vestidos.id if cat_vestidos else 3,
            "historia_peca": "Peça nova, nunca usada, etiqueta ainda anexa",
        },
    ]

    for prod_data in produtos_exemplo:
        # Verifica se produto já existe
        existing = session.query(Produto).filter_by(nome=prod_data["nome"]).first()
        if not existing:
            produto = Produto(**prod_data)
            session.add(produto)
            print(f"✅ Produto criado: {prod_data['nome']}")
        else:
            print(f"ℹ️  Produto já existe: {prod_data['nome']}")

    session.commit()
    session.close()


def main():
    """Função principal para popular dados"""
    print("🛍️  Populando dados iniciais do Brechó Cata Roupas...\n")

    try:
        print("📁 Criando categorias...")
        create_categories()

        print("\n👤 Criando usuário administrador...")
        create_admin_user()

        print("\n👗 Criando produtos de exemplo...")
        create_sample_products()

        print("\n🎉 Dados iniciais criados com sucesso!")
        print("\n📝 Próximos passos:")
        print("   1. Execute: poetry run python app/main.py")
        print("   2. Acesse: http://localhost:8000")
        print("   3. Login admin: admin@cataroupas.com / admin123")

    except Exception as e:
        print(f"❌ Erro ao popular dados: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
