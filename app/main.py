from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.sync import sync_products
from app.database import init_db
from app.repository import (
    list_products,
    get_product_by_id
)
from .cart_repository import (
    create_cart,
    get_cart,
    list_carts,
    delete_cart,
    add_item,
    update_item_quantity,
    remove_item,
    clear_cart,
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

 
# ================================================================
# SCHEMAS  (Pydantic)
# ================================================================
 
class AddItemRequest(BaseModel):
    product_id: int = Field(..., gt=0, description="ID del producto a agregar")
    quantity:   int = Field(1,  gt=0, description="Cantidad a agregar (acumula si ya existe)")
 
 
class UpdateItemRequest(BaseModel):
    quantity: int = Field(..., ge=0, description="Nueva cantidad (0 = eliminar item)")
 
 
# ================================================================
# CARTS  — CRUD
# ================================================================
 
@app.post("/carts", status_code=201, tags=["Cart"])
def create_new_cart():
    """Crea un carrito vacío y retorna su id."""
    cart_id = create_cart()
    return {"cart_id": cart_id, "message": "Carrito creado exitosamente."}
 
 
@app.get("/carts", tags=["Cart"])
def get_all_carts():
    """Lista todos los carritos con resumen (cantidad de items y total)."""
    return list_carts()
 
 
@app.get("/carts/{cart_id}", tags=["Cart"])
def get_cart_detail(cart_id: int):
    """Retorna el detalle completo de un carrito con sus productos y totales."""
    cart = get_cart(cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail=f"Carrito {cart_id} no encontrado.")
    return cart
 
 
@app.delete("/carts/{cart_id}", tags=["Cart"])
def delete_existing_cart(cart_id: int):
    """Elimina un carrito y todos sus items."""
    if not delete_cart(cart_id):
        raise HTTPException(status_code=404, detail=f"Carrito {cart_id} no encontrado.")
    return {"message": f"Carrito {cart_id} eliminado."}
 
 
# ================================================================
# CART ITEMS  — Añadir / Actualizar / Eliminar
# ================================================================
 
@app.post("/carts/{cart_id}/items", status_code=201, tags=["Cart"])
def add_product_to_cart(cart_id: int, body: AddItemRequest):
    """
    Añade un producto al carrito.  
    Si el producto ya existe en el carrito, **acumula** la cantidad indicada.
    """
    try:
        item = add_item(cart_id, body.product_id, body.quantity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return item
 
 
@app.patch("/carts/{cart_id}/items/{product_id}", tags=["Cart"])
def update_product_quantity(cart_id: int, product_id: int, body: UpdateItemRequest):
    """
    Establece la cantidad de un producto en el carrito.  
    Enviar `quantity: 0` elimina el item del carrito.
    """
    try:
        item = update_item_quantity(cart_id, product_id, body.quantity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return item
 
 
@app.delete("/carts/{cart_id}/items/{product_id}", tags=["Cart"])
def remove_product_from_cart(cart_id: int, product_id: int):
    """Elimina un producto específico del carrito."""
    if not remove_item(cart_id, product_id):
        raise HTTPException(
            status_code=404,
            detail=f"Producto {product_id} no encontrado en el carrito {cart_id}.",
        )
    return {"message": f"Producto {product_id} eliminado del carrito {cart_id}."}
 
 
@app.delete("/carts/{cart_id}/items", tags=["Cart"])
def clear_all_items(cart_id: int):
    """Vacía todos los productos de un carrito (el carrito persiste vacío)."""
    cart = get_cart(cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail=f"Carrito {cart_id} no encontrado.")
    count = clear_cart(cart_id)
    return {"message": f"Se eliminaron {count} item(s) del carrito {cart_id}."}
 

init_db()

