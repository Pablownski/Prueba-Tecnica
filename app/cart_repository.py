# app/cart_repository.py
"""
Repositorio para operaciones CRUD del carrito de compras.
Un cart_id puede tener múltiples productos (iguales o diferentes),
acumulando cantidades si el mismo producto se agrega varias veces.
"""
 
from .database import get_db_connection
 
 
# ------------------------------------------------------------------
# Carts
# ------------------------------------------------------------------
 
def create_cart() -> int:   
    """Crea un carrito vacío y retorna su id."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO carts DEFAULT VALUES"
        )
        conn.commit()
        return cursor.lastrowid
 
 
def get_cart(cart_id: int) -> dict | None:
    """Retorna el carrito con sus items o None si no existe."""
    with get_db_connection() as conn:
        cart = conn.execute(
            "SELECT id, created_at, updated_at FROM carts WHERE id = ?",
            (cart_id,),
        ).fetchone()
 
        if cart is None:
            return None
 
        items = conn.execute(
            """
            SELECT
                ci.id          AS item_id,
                ci.product_id,
                p.name         AS product_name,
                p.price,
                p.category,
                ci.quantity,
                ROUND(p.price * ci.quantity, 2) AS subtotal,
                ci.added_at
            FROM cart_items ci
            JOIN products p ON p.id = ci.product_id
            WHERE ci.cart_id = ?
            ORDER BY ci.added_at ASC
            """,
            (cart_id,),
        ).fetchall()
 
        items_list = [dict(row) for row in items]
        total = sum(item["subtotal"] for item in items_list)
 
        return {
            "id": cart["id"],
            "created_at": cart["created_at"],
            "updated_at": cart["updated_at"],
            "items": items_list,
            "total": round(total, 2),
        }
 
 
def list_carts() -> list[dict]:
    """Lista todos los carritos con resumen de items y total."""
    with get_db_connection() as conn:
        carts = conn.execute(
            "SELECT id, created_at, updated_at FROM carts ORDER BY created_at DESC"
        ).fetchall()
 
        result = []
        for cart in carts:
            summary = conn.execute(
                """
                SELECT
                    COUNT(*)                          AS item_count,
                    COALESCE(SUM(ci.quantity), 0)     AS total_qty,
                    COALESCE(SUM(p.price * ci.quantity), 0) AS total
                FROM cart_items ci
                JOIN products p ON p.id = ci.product_id
                WHERE ci.cart_id = ?
                """,
                (cart["id"],),
            ).fetchone()
 
            result.append({
                "id": cart["id"],
                "created_at": cart["created_at"],
                "updated_at": cart["updated_at"],
                "item_count": summary["item_count"],
                "total_quantity": summary["total_qty"],
                "total": round(summary["total"], 2),
            })
 
        return result
 
 
def delete_cart(cart_id: int) -> bool:
    """Elimina un carrito y en cascada sus items. Retorna True si existía."""
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM carts WHERE id = ?", (cart_id,))
        conn.commit()
        return cursor.rowcount > 0
 
 
# ------------------------------------------------------------------
# Cart Items
# ------------------------------------------------------------------
 
def add_item(cart_id: int, product_id: int, quantity: int = 1) -> dict:
    """
    Agrega un producto al carrito.
    - Si el producto ya existe en el carrito, acumula la cantidad.
    - Retorna el item actualizado/creado.
    Lanza ValueError si el carrito o el producto no existen.
    """
    if quantity < 1:
        raise ValueError("La cantidad debe ser mayor a 0.")
 
    with get_db_connection() as conn:
        # Validar que el carrito existe
        cart = conn.execute(
            "SELECT id FROM carts WHERE id = ?", (cart_id,)
        ).fetchone()
        if cart is None:
            raise ValueError(f"Carrito {cart_id} no encontrado.")
 
        # Validar que el producto existe
        product = conn.execute(
            "SELECT id FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if product is None:
            raise ValueError(f"Producto {product_id} no encontrado.")
 
        # Verificar si el item ya existe en el carrito
        existing = conn.execute(
            "SELECT id, quantity FROM cart_items WHERE cart_id = ? AND product_id = ?",
            (cart_id, product_id),
        ).fetchone()
 
        if existing:
            # Acumular cantidad
            new_qty = existing["quantity"] + quantity
            conn.execute(
                "UPDATE cart_items SET quantity = ? WHERE id = ?",
                (new_qty, existing["id"]),
            )
            item_id = existing["id"]
        else:
            # Insertar nuevo item
            cursor = conn.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)",
                (cart_id, product_id, quantity),
            )
            item_id = cursor.lastrowid
 
        # Actualizar timestamp del carrito
        conn.execute(
            "UPDATE carts SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (cart_id,),
        )
        conn.commit()
 
        # Retornar item completo
        row = conn.execute(
            """
            SELECT
                ci.id AS item_id, ci.cart_id, ci.product_id,
                p.name AS product_name, p.price, p.category,
                ci.quantity,
                ROUND(p.price * ci.quantity, 2) AS subtotal,
                ci.added_at
            FROM cart_items ci
            JOIN products p ON p.id = ci.product_id
            WHERE ci.id = ?
            """,
            (item_id,),
        ).fetchone()
 
        return dict(row)
 
 
def update_item_quantity(cart_id: int, product_id: int, quantity: int) -> dict:
    """
    Establece (no acumula) la cantidad de un producto en el carrito.
    Si quantity == 0, elimina el item.
    Lanza ValueError si el item no existe.
    """
    if quantity < 0:
        raise ValueError("La cantidad no puede ser negativa.")
 
    with get_db_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM cart_items WHERE cart_id = ? AND product_id = ?",
            (cart_id, product_id),
        ).fetchone()
 
        if existing is None:
            raise ValueError(
                f"Producto {product_id} no está en el carrito {cart_id}."
            )
 
        if quantity == 0:
            conn.execute("DELETE FROM cart_items WHERE id = ?", (existing["id"],))
            conn.execute(
                "UPDATE carts SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (cart_id,),
            )
            conn.commit()
            return {"item_id": existing["id"], "deleted": True, "quantity": 0}
 
        conn.execute(
            "UPDATE cart_items SET quantity = ? WHERE id = ?",
            (quantity, existing["id"]),
        )
        conn.execute(
            "UPDATE carts SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (cart_id,),
        )
        conn.commit()
 
        row = conn.execute(
            """
            SELECT
                ci.id AS item_id, ci.cart_id, ci.product_id,
                p.name AS product_name, p.price, p.category,
                ci.quantity,
                ROUND(p.price * ci.quantity, 2) AS subtotal,
                ci.added_at
            FROM cart_items ci
            JOIN products p ON p.id = ci.product_id
            WHERE ci.id = ?
            """,
            (existing["id"],),
        ).fetchone()
 
        return dict(row)
 
 
def remove_item(cart_id: int, product_id: int) -> bool:
    """Elimina un producto del carrito. Retorna True si existía."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?",
            (cart_id, product_id),
        )
        if cursor.rowcount > 0:
            conn.execute(
                "UPDATE carts SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (cart_id,),
            )
        conn.commit()
        return cursor.rowcount > 0
 
 
def clear_cart(cart_id: int) -> int:
    """Vacía todos los items de un carrito. Retorna cantidad de items eliminados."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM cart_items WHERE cart_id = ?", (cart_id,)
        )
        if cursor.rowcount > 0:
            conn.execute(
                "UPDATE carts SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (cart_id,),
            )
        conn.commit()
        return cursor.rowcount