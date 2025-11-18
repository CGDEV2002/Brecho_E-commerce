from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.categoria import Categoria

app = FastAPI(title="Brechó E-commerce", version="1.0.0")


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
