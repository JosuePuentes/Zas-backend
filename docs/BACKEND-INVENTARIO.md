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
- **utilidad**: número; porcentaje de utilidad (ej. 40 = 40%). Fórmula: `precio = costo × (1 + utilidad / 100)`.
- **precio**: precio de venta.
- **existencia**, **stock_minimo**, **stock_maximo**: números.

---

## Implementación (backend)

- **GET** `/inventario_maestro/`: Requiere `Authorization: Bearer <admin_token>`. Respuesta: `{ "productos": [ ... ] }`. Cada ítem tiene `_id`, `id`, `codigo`, `descripcion`, `marca`, `costo`, `utilidad`, `precio`, `existencia`, `stock_minimo`, `stock_maximo`. Si el documento tiene `laboratorio` y no `marca`, se expone como `marca`. Si tiene `precio_costo` y no `costo`, se expone como `costo`. La `utilidad` se calcula a partir de precio/costo si no está guardada.
- **POST** `/inventario_maestro/`: Requiere token admin. Body JSON: `codigo` (requerido), `descripcion`, `marca`, `costo`, `utilidad`, `precio`, `existencia`, `stock_minimo`, `stock_maximo`. Si se envían `costo` y `utilidad`, se calcula `precio = costo * (1 + utilidad/100)`. Respuesta: el producto creado (objeto con `_id`, `id` y el resto de campos).
- **PUT** `/inventario_maestro/{id}`: Requiere token admin. Body parcial con los mismos campos. Si se envían `costo` y `utilidad`, se actualiza `precio` con la misma fórmula. Respuesta: producto actualizado normalizado.
- **GET** `/inventario_maestro/{id}`: Requiere token admin. Devuelve un solo producto con la misma forma normalizada.
