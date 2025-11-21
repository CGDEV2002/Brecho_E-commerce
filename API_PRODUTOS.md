# 🛍️ API de Produtos - Brechó Cata Roupas

## 🚀 CRUD Completo Implementado!

### 📋 **Endpoints Disponíveis:**

#### **GET /produtos/** - Listar produtos com filtros

```bash
# Todos os produtos
curl http://127.0.0.1:8000/produtos/

# Com filtros
curl "http://127.0.0.1:8000/produtos/?categoria_id=1&tamanho=M&preco_max=100"

# Busca por texto
curl "http://127.0.0.1:8000/produtos/?busca=blusa"
```

#### **GET /produtos/{id}** - Obter produto específico

```bash
curl http://127.0.0.1:8000/produtos/1
```

#### **POST /produtos/** - Criar produto

```bash
curl -X POST "http://127.0.0.1:8000/produtos/" \
-H "Content-Type: application/json" \
-d '{
  "nome": "Camiseta Vintage Rock",
  "descricao": "Camiseta de banda dos anos 90",
  "marca": "Hanes",
  "cor_principal": "Preto",
  "tamanho": "M",
  "condicao": "USADO_BOM",
  "preco_original": 50.0,
  "preco_venda": 25.0,
  "categoria_id": 1,
  "ano_aproximado": 1995,
  "material": "Algodão",
  "historia_peca": "Camiseta de show original"
}'
```

#### **PUT /produtos/{id}** - Atualizar produto

```bash
curl -X PUT "http://127.0.0.1:8000/produtos/1" \
-H "Content-Type: application/json" \
-d '{
  "preco_venda": 30.0,
  "status": "DISPONIVEL"
}'
```

#### **DELETE /produtos/{id}** - Remover produto (soft delete)

```bash
curl -X DELETE http://127.0.0.1:8000/produtos/1
```

### 🎯 **Endpoints Especiais:**

#### **GET /produtos/categoria/{categoria_id}** - Produtos por categoria

```bash
curl http://127.0.0.1:8000/produtos/categoria/1
```

#### **GET /produtos/mais-vistos/** - Produtos mais visualizados

```bash
curl http://127.0.0.1:8000/produtos/mais-vistos/
```

#### **GET /produtos/lancamentos/** - Produtos mais recentes

```bash
curl http://127.0.0.1:8000/produtos/lancamentos/
```

#### **POST /produtos/{id}/favoritar** - Favoritar produto

```bash
curl -X POST http://127.0.0.1:8000/produtos/1/favoritar
```

#### **POST /produtos/{id}/imagem-principal** - Upload de imagem

```bash
curl -X POST "http://127.0.0.1:8000/produtos/1/imagem-principal" \
-F "file=@caminho/para/imagem.jpg"
```

### 🔍 **Filtros Disponíveis:**

- **categoria_id**: ID da categoria
- **tamanho**: PP, P, M, G, GG, XGG, UNICO
- **condicao**: NOVO, SEMI_NOVO, USADO_BOM, USADO_REGULAR
- **status**: DISPONIVEL, VENDIDO, RESERVADO, INATIVO
- **preco_min** / **preco_max**: Faixa de preço
- **marca**: Nome da marca
- **busca**: Busca no nome, descrição e marca

### 📊 **Funcionalidades Especiais do Brechó:**

✅ **Peça única**: Cada produto é único (não tem estoque)  
✅ **História da peça**: Campo para contar a origem  
✅ **Condição detalhada**: Estado de conservação  
✅ **Soft delete**: Produtos removidos ficam inativos  
✅ **Contador de visualizações**: Incrementa automaticamente  
✅ **Sistema de favoritos**: Contador de curtidas  
✅ **Upload de imagens**: Com redimensionamento automático  
✅ **Filtros avançados**: Busca por múltiplos critérios

### 🎨 **Campos Específicos para Brechó:**

- **historia_peca**: História/origem da peça
- **condicao**: Estado de conservação
- **ano_aproximado**: Ano estimado da peça
- **preco_original**: Preço quando nova
- **material**: Tipo de tecido/material
- **cuidados**: Instruções de lavagem

### 🔗 **Documentação Interativa:**

Acesse: **http://127.0.0.1:8000/docs**

### 🎯 **Próximos Passos:**

1. **Teste as APIs** usando os exemplos acima
2. **Implemente autenticação** (próxima etapa)
3. **Crie o frontend** para consumir as APIs
4. **Sistema de carrinho** e pedidos

**🎉 CRUD de produtos 100% funcional e específico para brechó!**
