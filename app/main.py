from fastapi import FastAPI
from app.sync import sync_products
from app.database import init_db
from app.repository import (
    list_products,
    get_product_by_id
)

app = FastAPI(title="Mini Catalog")

@app.post("/sync")
def sync():
    return sync_products()

@app.get("/products")
def get_products(limit: int = 10, offset: int = 0):
    return list_products(limit, offset)

@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = get_product_by_id(product_id)
    if not product:
        return {"error": "Producto no encontrado"}
    return product

init_db()
