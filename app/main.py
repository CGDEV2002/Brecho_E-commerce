from fastapi import FastAPI

app = FastAPI(title="Brechó E-commerce", version="1.0.0")


@app.get("/")
def home():
    return {"message": "Bem-vindo ao Brechó E-commerce!", "status": "funcionando"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
