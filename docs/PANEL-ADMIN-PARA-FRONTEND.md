# Panel administrativo – Guía para el frontend

**Objetivo:** El admin ya hace login correctamente (`role: "admin"`, `modulos`, `usuario`). Falta construir la interfaz del panel: menú, páginas y llamadas al backend. Este documento indica qué pantallas crear y qué rutas de la API usar en cada una.

**Base URL de la API:** `VITE_API_URL` (ej: `https://droclven-back.onrender.com`).  
**Headers en todas las peticiones admin:** `Content-Type: application/json` y `Authorization: Bearer <access_token>` (token que devuelve `POST /login/admin/`).

---

## 1. Qué muestra el menú del panel (según `modulos`)

Al hacer login admin, la respuesta trae:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "role": "admin",
  "rol": "master",
  "modulos": ["solicitudes_clientes", "pedidos", "inventario", "clientes"],
  "usuario": "master"
}
```

El frontend debe mostrar en el menú lateral (o superior) **solo** las secciones que correspondan a esos `modulos`. Sugerencia de mapeo:

| Valor en `modulos`   | Sección en el menú              | Descripción breve                    |
|----------------------|----------------------------------|--------------------------------------|
| `solicitudes_clientes` | Solicitudes de clientes         | Aprobar/rechazar nuevos clientes     |
| `pedidos`            | Pedidos (submenú o páginas)     | Dashboard, Administración, Picking, Packing, Envíos, Crear pedido |
| `inventario`         | Inventario                      | Ver/editar productos                 |
| `clientes`           | Clientes                        | Listar, crear, editar clientes      |

Además, se recomienda tener siempre:
- **Dashboard:** resumen (contadores, pedidos recientes, solicitudes pendientes).
- **Usuarios (admin):** si el backend lo soporta más adelante; por ahora se puede ocultar o dejar un placeholder.

---

## 2. Dashboard

**Qué mostrar:** Resumen del negocio: cantidad de solicitudes pendientes, pedidos por estado (nuevo, picking, packing, enviado), tal vez últimos pedidos.

**Rutas a usar:**

| Acción                    | Método | Ruta                               | Uso en el dashboard                         |
|---------------------------|--------|------------------------------------|--------------------------------------------|
| Solicitudes pendientes    | GET    | `/clientes/solicitudes/pendientes` | Contador y/o lista corta                   |
| Pedidos para administración | GET  | `/pedidos/administracion/`          | Pedidos nuevos sin validar (contador/lista) |
| Pedidos en picking        | GET    | `/pedidos/picking/`                | Contador/lista                             |
| Pedidos por estado        | GET    | `/pedidos/por_estado/{estado}`     | Para `packing`, `enviado`, etc. (contadores) |
| Listado general (filtros) | GET    | `/obtener_pedidos/?estados[]=nuevo&estados[]=picking` (opcional) | Si necesitas filtros por fecha/estado       |

Ejemplo de estados útiles: `nuevo`, `picking`, `check_picking`, `packing`, `para_facturar`, `facturando`, `enviado`, `entregado`, `cancelado`.

---

## 3. Solicitudes de clientes

**Qué mostrar:** Lista de clientes con `estado_aprobacion: "pendiente"`. Por cada uno: empresa, RIF, teléfono, encargado, email, dirección. Botones **Aprobar** y **Rechazar**.

**Rutas:**

| Acción    | Método | Ruta                        | Body / params      |
|-----------|--------|-----------------------------|--------------------|
| Listar    | GET    | `/clientes/solicitudes/pendientes` | —                  |
| Aprobar   | PATCH  | `/clientes/{rif}/aprobar`   | Path: `rif`        |
| Rechazar  | PATCH  | `/clientes/{rif}/rechazar`  | Path: `rif`        |

Respuesta de listar: array de objetos con `_id`, `empresa`, `rif`, `telefono`, `encargado`, `email`, `direccion`, `estado_aprobacion`. Tras aprobar o rechazar, volver a llamar a listar para refrescar.

---

## 4. Pedidos – Administración

**Qué mostrar:** Pedidos en estado `nuevo` que aún **no** han sido validados (para que pasen a picking).

**Ruta:**

| Acción | Método | Ruta                       |
|--------|--------|----------------------------|
| Listar | GET    | `/pedidos/administracion/`  |

Cada pedido tiene `_id`, `cliente`, `rif`, `estado`, `productos`, etc. Acción típica: **Validar** (o “Enviar a picking”). Para cambiar estado:

| Acción        | Método | Ruta                                   | Body (ejemplo)                                                                 |
|---------------|--------|----------------------------------------|---------------------------------------------------------------------------------|
| Actualizar estado | PUT    | `/pedidos/actualizar_estado/{pedido_id}` | `{ "nuevo_estado": "nuevo", "verificaciones": {}, "usuario": "master" }` (validar puede implicar marcar validado y/o pasar a picking; ver backend). |

Para validar con PIN (si aplica): `POST /pedidos/{pedido_id}/validar` con body `{ "pin": "..." }`.

---

## 5. Picking

**Qué mostrar:** Lista de pedidos listos para picking (validados, en estado `nuevo`). Por cada pedido: datos del pedido y productos a preparar; posibilidad de registrar cantidades encontradas y marcar inicio/fin de picking.

**Rutas:**

| Acción                    | Método | Ruta                                      | Body / params |
|---------------------------|--------|-------------------------------------------|---------------|
| Listar pedidos en picking | GET    | `/pedidos/picking/`                       | —             |
| Actualizar cantidades     | PATCH  | `/pedidos/actualizar_cantidades/{pedido_id}` | `{ "cantidades": { "CODIGO1": 10, "CODIGO2": 5 } }` |
| Actualizar info picking   | PATCH  | `/pedidos/actualizar_picking/{pedido_id}`  | Objeto con usuario, fechainicio_picking, fechafin_picking, estado_picking |
| Finalizar check picking   | POST   | `/pedidos/{pedido_id}/finalizar_check_picking` | Body con verificaciones, usuario |
| Pedidos para check picking| GET    | `/pedidos/checkpicking/`                  | —             |

Estados: de `nuevo` (validado) se pasa a picking; luego puede haber `check_picking` y después `packing`. El flujo exacto depende de cómo uses `actualizar_estado` y `actualizar_picking`.

---

## 6. Packing

**Qué mostrar:** Pedidos en estado `packing`. Listar, y por cada uno permitir completar packing (actualizar datos de packing).

**Rutas:**

| Acción              | Método | Ruta                                      | Body |
|---------------------|--------|-------------------------------------------|------|
| Listar (por estado) | GET    | `/pedidos/por_estado/packing`              | —    |
| Actualizar packing  | PATCH  | `/pedidos/actualizar_packing/{pedido_id}`  | PackingInfo (peso, cajas, observaciones, etc.) |

---

## 7. Envíos

**Qué mostrar:** Pedidos en estado `enviado` (o “para enviar”). Listar y, si aplica, asignar conductor o actualizar datos de envío.

**Rutas:**

| Acción               | Método | Ruta                                     | Body |
|----------------------|--------|------------------------------------------|------|
| Listar (enviados)    | GET    | `/pedidos/por_estado/enviado`             | —    |
| Actualizar envío     | PATCH  | `/pedidos/actualizar_envio/{pedido_id}`  | EnvioInfo (conductor, fecha, etc.) |
| Listar conductores   | GET    | `/conductores/`                          | —    |

Para pedidos “para facturar” antes de envío: `GET /pedidos/para_facturar/` y `PUT /pedidos/actualizar_facturacion/{pedido_id}`, `PUT /pedidos/finalizar_facturacion/{pedido_id}`.

---

## 8. Crear clientes

**Qué mostrar:** Formulario para dar de alta un cliente (RIF, empresa, encargado, dirección, teléfono, email, contraseña, descuentos, etc.).

**Ruta:**

| Acción | Método | Ruta          | Body |
|--------|--------|---------------|------|
| Crear  | POST   | `/clientes/`  | Objeto tipo Client: `rif`, `empresa`, `encargado`, `direccion`, `telefono`, `email`, `password`, `activo`, `descuento1`, `descuento2`, `descuento3`, opcionales: `descripcion`, `dias_credito`, `limite_credito`. |

El backend puede guardar `estado_aprobacion: "pendiente"` o "aprobado" según implementación; si es pendiente, el cliente no podrá hacer login hasta que un admin lo apruebe desde **Solicitudes de clientes**.

Para listar todos los clientes (y poder editar): `GET /clientes/all` o `GET /clientes/`. Para editar: `PATCH /clientes/{rif}`. Para ver uno: `GET /clientes/{rif}`.

---

## 9. Usuarios (administrativos)

**Qué mostrar:** Por ahora el backend no expone un `GET` para listar usuarios admin. Sí permite:
- Crear admin: `POST /register/admin/` con `{ "usuario", "password", "rol", "modulos": ["solicitudes_clientes", "pedidos", "inventario", "clientes"] }`.
- Actualizar admin: `PUT /admin/usuarios/{usuario}` con body parcial (password, rol, modulos, etc.).

Opciones para el frontend:
- Mostrar una pantalla **“Crear usuario admin”** (formulario que llama a `POST /register/admin/`).
- Pantalla **“Usuarios”** con mensaje tipo “Próximamente” o solo “Crear usuario” hasta que el backend ofrezca listado.

---

## 10. Crear pedidos

**Qué mostrar:** Formulario para crear un pedido: cliente (RIF), observación, lista de productos (código, descripción, cantidad, precios, descuentos) y total/subtotal.

**Ruta:**

| Acción | Método | Ruta         | Body |
|--------|--------|--------------|------|
| Crear  | POST   | `/pedidos/`  | `PedidoResumen`: `cliente`, `rif`, `observacion`, `total`, `subtotal`, `productos` (array de objetos con `codigo`, `descripcion`, `precio`, `descuento1`–`descuento4`, `cantidad_pedida`, etc.). Opcional: `estado`. |

Para buscar clientes y productos al armar el pedido: `GET /clientes/` o `/clientes/all`, `GET /inventario_maestro/` o `/inventario_maestro/`.

---

## 11. Inventario

**Qué mostrar:** Lista de productos (inventario maestro). Filtrar/buscar y editar producto (precio, existencia, etc.).

**Rutas:**

| Acción           | Método | Ruta                     |
|------------------|--------|--------------------------|
| Listar todo      | GET    | `/inventario_maestro/`   |
| Un producto      | GET    | `/inventario_maestro/{id}` |
| Actualizar       | PUT    | `/inventario_maestro/{id}` |

Body de actualización según campos del producto en el backend (código, descripcion, precio, existencia, etc.).

---

## 12. Resumen de menú sugerido para el panel

1. **Dashboard** – Resumen (solicitudes pendientes, pedidos por estado).
2. **Solicitudes de clientes** – Lista, Aprobar, Rechazar (`modulo: solicitudes_clientes`).
3. **Pedidos**
   - Administración – Pedidos nuevos sin validar.
   - Picking – Lista picking, actualizar cantidades y picking.
   - Packing – Lista packing, actualizar packing.
   - Envíos – Lista enviados, actualizar envío / conductores.
   - Crear pedido – Formulario POST `/pedidos/`.
4. **Clientes** – Listar, Crear cliente, Editar (`modulo: clientes`).
5. **Inventario** – Listar y editar productos (`modulo: inventario`).
6. **Usuarios** – Crear usuario admin (y luego listar cuando el backend lo tenga).

Mostrar u ocultar cada bloque según el array `modulos` que devuelve el login admin. Todas las peticiones con `Authorization: Bearer <access_token>`.

---

## 13. Referencia rápida de rutas (solo admin / panel)

```
GET  /clientes/solicitudes/pendientes
PATCH /clientes/{rif}/aprobar
PATCH /clientes/{rif}/rechazar
GET  /pedidos/administracion/
GET  /pedidos/picking/
GET  /pedidos/por_estado/{estado}
GET  /pedidos/checkpicking/
GET  /pedido/{pedido_id}
PUT  /pedidos/actualizar_estado/{pedido_id}
PATCH /pedidos/actualizar_cantidades/{pedido_id}
PATCH /pedidos/actualizar_picking/{pedido_id}
PATCH /pedidos/actualizar_packing/{pedido_id}
PATCH /pedidos/actualizar_envio/{pedido_id}
POST /pedidos/{pedido_id}/finalizar_check_picking
GET  /conductores/
GET  /pedidos/para_facturar/
PUT  /pedidos/actualizar_facturacion/{pedido_id}
PUT  /pedidos/finalizar_facturacion/{pedido_id}
POST /pedidos/          (crear pedido)
GET  /obtener_pedidos/
GET  /clientes/all
GET  /clientes/
GET  /clientes/{rif}
POST /clientes/
PATCH /clientes/{rif}
GET  /inventario_maestro/
GET  /inventario_maestro/{id}
PUT  /inventario_maestro/{id}
POST /register/admin/
PUT  /admin/usuarios/{usuario}
```

Documento de referencia completa de la API: **BACKEND-ESTADO-PARA-FRONTEND.md** (en la raíz del repo del backend).
