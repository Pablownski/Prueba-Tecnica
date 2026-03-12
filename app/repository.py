from app.database import get_db_connection

 # Función para insertar o actualizar un producto en la base de datos
def upsert_product(product):
     conn = get_db_connection()
     cursor = conn.cursor()
     cursor.execute("""
         INSERT INTO products (id, name, price, category, source)
         VALUES (?, ?, ?, ?, ?)
         ON CONFLICT(id) DO UPDATE SET
             name=excluded.name,
             price=excluded.price,
             category=excluded.category,
             source=excluded.source
     """, (product['id'], product['title'], product['price'], product['category'], "fakestore"))

     conn.commit()
     conn.close()

# Función para listar productos con paginación
def list_products(limit, offset):
     conn = get_db_connection()
     cursor = conn.cursor()
     cursor.execute("""SELECT * FROM products LIMIT ? OFFSET ?""", (limit, offset))
     rows = cursor.fetchall()
     conn.close()
     return [dict(r) for r in rows]

# Función para obtener un producto por su ID
def get_product_by_id(product_id):
     conn = get_db_connection()
     cursor = conn.cursor()

     cursor.execute("""SELECT * FROM products WHERE id = ?""", (product_id,))
     row = cursor.fetchone()
     conn.close()
     return dict(row) if row else None

