#!/usr/bin/env python3
"""
Script para testar o sistema de autenticação JWT
Execute com: poetry run python test_auth.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_register():
    """Teste de registro"""
    print("🧪 Testando registro de usuário...")

    user_data = {
        "nome": "João Silva",
        "email": "joao@teste.com",
        "senha": "123456",
        "telefone": "(11) 99999-9999",
    }

    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)

    if response.status_code == 201:
        print("✅ Usuário registrado com sucesso!")
        return user_data
    else:
        print(f"❌ Erro no registro: {response.text}")
        return None


def test_login(user_data):
    """Teste de login"""
    print("🧪 Testando login...")

    login_data = {
        "username": user_data["email"],  # OAuth2 usa 'username'
        "password": user_data["senha"],
    }

    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

    if response.status_code == 200:
        token_data = response.json()
        print("✅ Login realizado com sucesso!")
        print(f"Token: {token_data['access_token'][:50]}...")
        return token_data["access_token"]
    else:
        print(f"❌ Erro no login: {response.text}")
        return None


def test_protected_route(token):
    """Teste de rota protegida"""
    print("🧪 Testando rota protegida...")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        print("✅ Acesso autorizado!")
        print(f"Usuário: {user_data['nome']} ({user_data['email']})")
    else:
        print(f"❌ Erro na rota protegida: {response.text}")


def test_admin_login():
    """Teste de login admin"""
    print("🧪 Testando login admin...")

    login_data = {"username": "admin@cataroupas.com", "password": "admin123"}

    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

    if response.status_code == 200:
        token_data = response.json()
        print("✅ Login admin realizado com sucesso!")
        return token_data["access_token"]
    else:
        print(f"❌ Erro no login admin: {response.text}")
        return None


def test_produtos(token):
    """Teste de acesso aos produtos"""
    print("🧪 Testando acesso aos produtos...")

    response = requests.get(f"{BASE_URL}/produtos/")

    if response.status_code == 200:
        produtos = response.json()
        print(f"✅ {len(produtos)} produtos encontrados!")
    else:
        print(f"❌ Erro ao buscar produtos: {response.text}")


def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do sistema de autenticação JWT\n")

    # Verificar se servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/")
        print("✅ Servidor está rodando!")
        print(f"Resposta: {response.json()['message']}\n")
    except:
        print("❌ Servidor não está rodando!")
        print("Execute: poetry run uvicorn app.main:app --reload")
        return

    # Teste 1: Registro de usuário
    user_data = test_register()
    print()

    if user_data:
        # Teste 2: Login
        token = test_login(user_data)
        print()

        if token:
            # Teste 3: Rota protegida
            test_protected_route(token)
            print()

    # Teste 4: Login admin
    admin_token = test_admin_login()
    print()

    # Teste 5: Produtos (rota pública)
    test_produtos(admin_token)
    print()

    print("🎉 Testes concluídos!")
    print("\n📚 Próximos passos:")
    print("1. Acesse http://127.0.0.1:8000/docs para ver a documentação")
    print("2. Teste manualmente no Swagger UI")
    print("3. Implemente o frontend com os tokens JWT")


if __name__ == "__main__":
    main()
