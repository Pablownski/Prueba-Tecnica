# Prompt
 
Tengo un proyecto en python avanzado acerca de un MiniCatalogo con una Api Fakestore (https://fakestoreapi.com/products). Cuento con una estructura de app (donde esta la lógica) y una carpeta sql donde se encuentra la base de datos "products.db" y un schema.sql donde se guarda la estrucutura para las tablas. La tabla de products esta hecha de la siguiente manera:
id - PK, name - text Not null, price Real not null, category text nn, source text nn, created_at timestamp ct.
 
Ahora bien en la app tengo un archivo de database que me guarda la base de datos en una ruta y hace una conexión hacia schema.sql y abre la conexión. Además cuento con un archivo llamado repository.py, el cual se encarga de funciones como 1. insertar y actualizar, en caso de id repetido con upsert. 2 listar los productos con un limit y offset y 3. listar por id. Por otro, lado cuento con un apartado de sincronización para poder sincronizar la api con la base de datos y por ultimo un main.py el cual se encarga de hacer los get y post con fastapi y uvicorn para probar con swaggerui.
 
Ahora a este proyecto, le debo implementar la función de añadir al carrito, la cual cuenta con algunas recomendaciones como lo son que un cart_id puede tener varios productos (iguales o diferentes). Para esto, debes crear las tablas de carrito, con un id como PK, productos id, cantidades. Por último, debe hacer persistencia de datos a la hora de querer añadir al carrito.
 