import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from fastapi import FastAPI, Depends, HTTPException
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

# Configurações
settings = get_settings()

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API completa para e-commerce de brechó especializado em roupas vintage e sustentáveis",
    debug=settings.DEBUG
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

# Middleware para log de requisições
@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    print(f"{request.method} {request.url.path} - {response.status_code}")
    return response

@app.get("/")
def home():
    return {
        "message": "Bem-vindo ao Brechó Cata Roupas!",
        "description": "Moda vintage e sustentável com estilo único",
        "version": settings.APP_VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "categorias": "/categorias", 
            "auth": "/auth",
            "usuarios": "/usuarios",
            "docs": "/docs"
        }
    }

@app.get("/categorias")
def listar_categorias(db: Session = Depends(get_db)):
    """Lista todas as categorias disponíveis"""
    try:
        categorias = db.query(Categoria).all()
        return {"categorias": categorias, "total": len(categorias)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar categorias: {str(e)}")

@app.get("/health")
def health_check():
    """Endpoint de saúde da API"""
    return {"status": "healthy", "timestamp": "2025-12-02"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=settings.DEBUG)
