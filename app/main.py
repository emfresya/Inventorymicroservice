from fastapi import FastAPI
from app.api import orders

app = FastAPI(title="Inventory Service")

app.include_router(orders.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}