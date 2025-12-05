import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("🚀 Teste do Sistema JWT - Brechó Cata Roupas")
print("=" * 50)

# Teste 1: Endpoint principal
print("1. Testando endpoint principal...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Status: {response.status_code}")
    print(f"   Resposta: {response.json()['message']}")
except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 2: Login admin
print("\n2. Testando login admin...")
try:
    login_data = {"username": "admin@cataroupas.com", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"✅ Status: {response.status_code}")

    if response.status_code == 200:
        token_data = response.json()
        print(f"   Token gerado: {token_data['access_token'][:30]}...")
        print(f"   Usuário: {token_data['user_name']} (ID: {token_data['user_id']})")

        # Teste 3: Rota protegida
        print("\n3. Testando rota protegida...")
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        profile_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"✅ Status: {profile_response.status_code}")

        if profile_response.status_code == 200:
            profile = profile_response.json()
            print(f"   Nome: {profile['nome']}")
            print(f"   Email: {profile['email']}")
            print(f"   Tipo: {profile['tipo']}")

except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 4: Registro de novo usuário
print("\n4. Testando registro de usuário...")
try:
    user_data = {
        "nome": "João Teste",
        "email": "joao@teste.com",
        "senha": "123456",
        "telefone": "(11) 99999-9999",
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"✅ Status: {response.status_code}")

    if response.status_code == 201:
        user = response.json()
        print(f"   Usuário criado: {user['nome']} (ID: {user['id']})")
    elif response.status_code == 400:
        print(f"   ℹ️  Email já existe: {response.json()['detail']}")

except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 5: Produtos
print("\n5. Testando listagem de produtos...")
try:
    response = requests.get(f"{BASE_URL}/produtos/")
    print(f"✅ Status: {response.status_code}")

    if response.status_code == 200:
        produtos = response.json()
        print(f"   Total de produtos: {len(produtos)}")
        if produtos:
            print(f"   Primeiro produto: {produtos[0]['nome']}")

except Exception as e:
    print(f"❌ Erro: {e}")

print("\n🎉 Testes concluídos!")
print("📚 Acesse: http://127.0.0.1:8000/docs para documentação completa")
