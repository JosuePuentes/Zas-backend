# Backend – Inventario Maestro (especificación)

## Endpoints a implementar

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/inventario_maestro/` | Listar productos (array o `{ items \| data \| productos \| results }`) |
| POST | `/inventario_maestro/` | Crear producto (JSON o FormData con foto) |
| PUT | `/inventario_maestro/{id}` | Actualizar producto |

## Requisitos

- **GET** debe devolver un array o un objeto con una propiedad array (`items`, `data`, `productos` o `results`).
- **POST** debe devolver el producto creado con `_id` o `id`.
- Todas las rutas requieren **token admin**: `Authorization: Bearer <token>`.

## Campos por producto

`_id`, `codigo`, `descripcion`, `marca`, `costo`, `utilidad`, `precio`, `existencia`, `stock_minimo`, `stock_maximo`.

- **marca**: string (opcional).
- **costo**: número; precio de costo.
- **utilidad**: número; porcentaje de utilidad sobre el precio de venta (utilidad comercial/contable). Fórmula: `precio = costo / (1 - utilidad/100)`. Ejemplo: costo $1, utilidad 30% → precio = 1 / 0.70 = $1.43 (no $1.30).
- **precio**: precio de venta.
- **existencia**, **stock_minimo**, **stock_maximo**: números.

---

## Implementación (backend)

- **Fórmula de utilidad:** `precio = costo / (1 - utilidad/100)`. La utilidad es margen sobre precio (comercial/contable). En informes, la columna **Utilidad** se muestra como porcentaje (ej. 30%), no como monto en $.
- **GET** `/inventario_maestro/`: Requiere `Authorization: Bearer <admin_token>`. Respuesta: `{ "productos": [ ... ] }`. Cada ítem incluye `_id`, `id`, `codigo`, `descripcion`, `marca`, `costo`, `utilidad` (%), `precio`, `existencia`, `stock_minimo`, `stock_maximo`, `foto_url`. La `utilidad` se calcula como margen: `(1 - costo/precio)*100` si no está guardada.
- **POST** `/inventario_maestro/`: Requiere token admin. Body: `codigo` (requerido), `descripcion`, `marca`, `costo`, `utilidad`, `precio`, `existencia`, `stock_minimo`, `stock_maximo`, `foto_url` (opcional). Si se envían `costo` y `utilidad`, se calcula `precio = costo / (1 - utilidad/100)`. Respuesta: producto creado con `_id`, `id`.
- **PUT** `/inventario_maestro/{id}`: Requiere token admin. Body parcial; misma fórmula para costo/utilidad/precio. Acepta `foto_url`, `foto`.
- **GET** `/inventario_maestro/{id}`: Requiere token admin. Devuelve un producto con la misma forma normalizada.
- **GET** `/inventario_maestro/{id}/foto`: Sin token admin (público). Si el producto tiene `foto_url` (o `foto`) con URL http(s), responde con redirect (302) a esa URL. Si no hay foto, 404.
