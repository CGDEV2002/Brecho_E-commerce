import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database.connection import get_db, engine
from app.models.categoria import Categoria
from app.models import Base
from app.config import get_settings

# Importar routers
from app.routes.produtos import router as produtos_router
from app.routes.auth import router as auth_router
from app.routes.usuarios import router as usuarios_router
from app.routes.carrinho import router as carrinho_router
from app.routes.admin import router as admin_router

# Importar para templates
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="app/templates")

# Configurações
settings = get_settings()

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API completa para e-commerce de brechó especializado em roupas vintage e sustentáveis",
    debug=settings.DEBUG,
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Registrar rotas
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(produtos_router)
app.include_router(carrinho_router)
app.include_router(admin_router)


# Middleware para log de requisições
@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    print(f"{request.method} {request.url.path} - {response.status_code}")
    return response


@app.get("/api")
def api_info():
    return {
        "message": "Bem-vindo ao Brechó Cata Roupas!",
        "description": "Moda vintage e sustentável com estilo único",
        "version": settings.APP_VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "categorias": "/categorias",
            "auth": "/auth",
            "usuarios": "/usuarios",
            "docs": "/docs",
        },
    }


@app.get("/categorias")
def listar_categorias(db: Session = Depends(get_db)):
    """Lista todas as categorias disponíveis"""
    try:
        categorias = db.query(Categoria).all()
        return {"categorias": categorias, "total": len(categorias)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar categorias: {str(e)}"
        )


# ROTAS DE TEMPLATES
@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/shop", response_class=HTMLResponse)
def shop_page(request: Request):
    return templates.TemplateResponse("shop.html", {"request": request})


@app.get("/carrinho", response_class=HTMLResponse)
def carrinho_page(request: Request):
    return templates.TemplateResponse("carrinho.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Rota de acesso administrativo (URL discreta)
@app.get("/sistema/gerenciamento", response_class=HTMLResponse)
def admin_painel(request: Request):
    return templates.TemplateResponse("admin_painel.html", {"request": request})


@app.get("/sistema/acesso", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/health")
def health_check():
    """Endpoint de saúde da API"""
    return {"status": "healthy", "timestamp": "2025-12-05"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=settings.DEBUG)
