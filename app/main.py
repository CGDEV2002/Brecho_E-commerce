import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.categoria import Categoria
from app.routes.produtos import router as produtos_router

app = FastAPI(
    title="Brechó Cata Roupas - API",
    version="1.0.0",
    description="API completa para e-commerce de brechó",
)

# Registrar rotas
app.include_router(produtos_router)


@app.get("/")
def home():
    return {"message": "Bem-vindo ao Brechó E-commerce!"}


@app.get("/categorias")
def listar_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return {"categorias": categorias}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
