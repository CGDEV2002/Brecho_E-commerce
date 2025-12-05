# 🛍️ Brechó Cata Roupas - E-commerce Completo

Sistema completo de e-commerce para brechó com carrinho, WhatsApp checkout e painel administrativo.

## ✨ Funcionalidades

### 🛒 Para Clientes
- **Catálogo de produtos** com filtros (categoria, tamanho, preço)
- **Carrinho de compras** persistente 
- **Checkout via WhatsApp** automático
- **Busca** por nome, marca e descrição
- **Produtos únicos** específicos para brechó
- **Interface responsiva** mobile-friendly

### 👑 Para Admin
- **Painel administrativo** completo
- **Dashboard** com estatísticas
- **CRUD de produtos** com upload de imagens
- **Gestão de categorias**
- **Sistema de autenticação** JWT

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
poetry install
```

### 2. Configurar WhatsApp
Edite o arquivo `app/routes/carrinho.py` linha 117:
```python
whatsapp_number = "5511999999999"  # SEU NÚMERO AQUI
```

### 3. Popular Dados Iniciais
```bash
poetry run python scripts/populate_data.py
```

### 4. Rodar Servidor
```bash
poetry run uvicorn app.main:app --reload
```

### 5. Acessar o Sistema
- **Site**: http://127.0.0.1:8080
- **Admin**: http://127.0.0.1:8080/sistema/gerenciamento
- **API Docs**: http://127.0.0.1:8080/docs

## 🔐 Acesso Administrativo

**URL Discreta**: `/sistema/gerenciamento`  
**Email**: `admin@cataroupas.com`  
**Senha**: `admin123`

> ⚠️ O painel admin não aparece na navegação pública para maior segurança

## 📱 Como Funciona o Checkout

1. Cliente adiciona produtos ao carrinho
2. No checkout, clica em "Finalizar no WhatsApp"  
3. Abre WhatsApp com mensagem automática:
   ```
   🛍️ Pedido do Brechó Cata Roupas 🛍️
   
   • Nome do Produto
     💰 R$ 50,00
   
   💯 TOTAL: R$ 50,00
   
   📞 Gostaria de finalizar este pedido!
   🏠 Preciso combinar entrega/retirada
   ```

## 🎨 Estrutura do Projeto

```
brecho-ecommerce/
├── app/
│   ├── models/          # Modelos do banco
│   ├── routes/          # APIs e endpoints  
│   ├── templates/       # Templates HTML
│   ├── static/          # CSS, JS, imagens
│   └── database/        # Configuração banco
├── scripts/            # Scripts utilitários
└── alembic/           # Migrações banco
```

## 🛠️ Tecnologias

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: Bootstrap + JavaScript vanilla
- **Auth**: JWT tokens
- **Upload**: Pillow (redimensionamento automático)
- **Checkout**: WhatsApp API

## 📋 Funcionalidades Técnicas

### Carrinho
- Armazenamento em **cookies** (7 dias)
- **Peças únicas** (quantidade = 1)
- Cálculo automático de totais

### Admin
- **Upload de imagens** com redimensionamento
- **Dashboard** em tempo real
- **Soft delete** dos produtos
- Filtros e busca avançada

### Banco de Dados
- **SQLite** para desenvolvimento
- **Alembic** para migrações
- Modelos específicos para **brechó**

## 🎯 Próximas Melhorias (Opcionais)

- [ ] Sistema de avaliações
- [ ] Multiple imagens por produto  
- [ ] Integração com Correios
- [ ] Relatórios de vendas
- [ ] Newsletter
- [ ] Deploy em produção

## 📞 Suporte

- **WhatsApp**: (11) 99999-9999
- **Email**: admin@cataroupas.com

---

**🎉 Sistema 100% funcional e pronto para uso!**

*Desenvolvido com FastAPI + Bootstrap para máxima simplicidade e eficiência.*
