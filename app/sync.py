import requests
from app.repository import upsert_product

API_URL = "https://fakestoreapi.com/products"

def sync_products():
    try:
        response = requests.get(API_URL)
        products = response.json()

        for product in products:
            upsert_product(product)
        return ("Productos sincronizados exitosamente.")
    
    except requests.RequestException as e:
        print(f"Error al sincronizar productos: {e}")


