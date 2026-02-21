# Estado del Backend – Guía para adaptar el frontend (Vite)

Este documento describe la API del backend (FastAPI en Render) para que el frontend estático (Vite) se conecte correctamente.

**Para la IA del backend:** Ver instrucciones de mantenimiento en [docs/INSTRUCCIONES-PARA-IA-BACKEND.md](docs/INSTRUCCIONES-PARA-IA-BACKEND.md).

### Rutas usadas por el frontend Virgen del Carmen

| Método | Ruta | Uso |
|--------|------|-----|
| POST | `/login/` | Login cliente |
| POST | `/register/` | Registro cliente |
| POST | `/contacto` | Formulario de contacto |
| POST | `/api/chat` | Chatbot |
| GET | `/inventario_maestro/` | Catálogo |
| GET | `/pedidos/por_cliente/{rif}` | Pedidos del cliente |
| POST | `/reclamos/cliente` | Crear reclamo |
| GET | `/reclamos/cliente/{rif}` | Listar reclamos |
| GET | `/clientes/solicitudes/pendientes` | (Admin) Solicitudes de nuevos clientes |
| PATCH | `/clientes/{rif}/aprobar` | (Admin) Aprobar cliente |
| PATCH | `/clientes/{rif}/rechazar` | (Admin) Rechazar cliente |

---

## 1. Configuración base

| Concepto | Valor |
|----------|--------|
| **Base URL** | Variable de entorno en Vercel: `VITE_API_URL` (ej: `https://droclven-back.onrender.com`) |
| **Content-Type** | `application/json` en POST/PUT/PATCH |
| **Autenticación** | JWT en header: `Authorization: Bearer <token>` (donde el backend lo requiera; actualmente muchos endpoints no validan token) |

### Multi-tenant (un backend, varios frontends y bases de datos)

El backend elige la **base de datos** según el **Origin** del request (desde qué URL llama el frontend). En Render configura:

- **MONGO_URI:** una sola cadena de conexión a un **cluster** de MongoDB (en ese cluster pueden existir varias bases: DROCOLVEN, VIRGENCARMEN, etc.).
- **TENANT_ORIGIN_DB:** mapa `host:nombre_base`, por ejemplo:  
  `virgen-del-carmen-frontend.vercel.app:VIRGENCARMEN,www.drocolven.com:DROCOLVEN,drocolven.com:DROCOLVEN,localhost:3000:DROCOLVEN`
- **DEFAULT_TENANT_DB:** base por defecto si el Origin no está en el mapa (ej: `DROCOLVEN`).

Cada petición usa la base correspondiente a su Origin; no hace falta un Render ni una MONGO_URI por frontend.

---

## 2. Autenticación

### 2.1 Registro de cliente (público)

- **POST** `/register/`
- **Body:** `UserRegister` / `Client` (el endpoint usa Client). **email** y **password** son obligatorios en registro público. Incluye **empresa** (nombre de la empresa), opcional.
```json
{
  "email": "string",
  "password": "string",
  "rif": "string",
  "empresa": "string",
  "direccion": "string",
  "telefono": "string",
  "encargado": "string",
  "activo": true,
  "descuento1": 0,
  "descuento2": 0,
  "descuento3": 0
}
```
- **Respuesta:** `{ "message": "Cliente registrado exitosamente. Su cuenta está pendiente de aprobación." }` o error 400 (correo/RIF ya existe). Los nuevos clientes quedan con `estado_aprobacion: "pendiente"` hasta que un admin los apruebe.

### 2.2 Login cliente (público)

- **POST** `/login/`
- **Body:**
```json
{ "email": "string", "password": "string" }
```
- **Respuesta:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "username": "email",
  "modules": [],
  "role": "client",
  "rif": "string"
}
```
- **Errores de estado:** Si el cliente está pendiente de aprobación: **403** `detail: "Pendiente de aprobación. Su solicitud está en revisión."`. Si fue rechazado: **403** `detail: "Solicitud rechazada. Contacte al administrador."`. El frontend debe mostrar ese mensaje y no dar acceso.
- Guardar `access_token` y enviarlo en `Authorization: Bearer <access_token>` en llamadas que lo requieran.

### 2.3 Registro admin (público, uso interno)

- **POST** `/register/admin/`
- **Body:** `{ "usuario": "string", "password": "string", "rol": "string", "modulos": ["string"] }`
- **Respuesta:** `{ "message": "Usuario administrativo registrado exitosamente" }`

### 2.4 Login admin (público)

- **POST** `/login/admin/`
- **Body:** `{ "usuario": "string", "password": "string" }`
- **Respuesta:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "role": "admin",
  "rol": "string",
  "modulos": ["string"],
  "usuario": "string"
}
```
- **role** siempre es `"admin"` para identificar al usuario como administrador. **rol** es el rol guardado en BD (ej: `"master"`, `"admin"`).

---

## 3. Clientes

| Método | Ruta | Descripción | Body / Params |
|--------|------|-------------|----------------|
| POST | `/clientes/` | Crear cliente (admin) | `Client`: rif, empresa (opc.), encargado, direccion, telefono, **email** (opc., se genera si no se envía), **password** (opc., se genera si no se envía), descripcion, dias_credito, limite_credito, activo, descuento1, descuento2, descuento3. Se guarda con `estado_aprobacion: "pendiente"`. Si no se envía email/password, se generan automáticamente basados en el RIF. |
| GET | `/clientes/solicitudes/pendientes` | **(Admin)** Listar solicitudes pendientes | —. Respuesta: array con `_id`, `empresa`, `rif`, `telefono`, `encargado`, `email`, `direccion`, `estado_aprobacion`. |
| PATCH | `/clientes/{rif}/aprobar` | **(Admin)** Aprobar cliente; podrá hacer login | Path: rif. Body opcional: `{ "limite_credito", "dias_credito", "monto" }`. |
| PATCH | `/clientes/{rif}/rechazar` | **(Admin)** Rechazar solicitud (motivo obligatorio) | Path: rif. Body: `{ "motivo": "string" }`. El motivo se guarda para informes. Respuesta: `{ "message": "Solicitud rechazada." }`. |
| GET | `/clientes/solicitudes/historial` | **(Admin)** Historial de solicitudes (aprobadas/rechazadas) | —. Respuesta: array con `_id`, `empresa`, `rif`, `estado_aprobacion`, `motivo_rechazo` (si rechazado), etc. |
| GET | `/clientes/all` | Listar todos (con `_id` como string) | — |
| GET | `/clientes/` | Lista resumida (email, rif, encargado) | — |
| GET | `/clientes/{rif}` | Cliente por RIF (incl. limite_credito, limite_consumido, facturas_vencidas) | Path: `rif` |
| PATCH | `/clientes/{rif}` | Actualizar cliente | Parcial: encargado, direccion, telefono, email, password, etc. (todos opcionales) |
| DELETE | `/clientes/{rif}` | Eliminar cliente | Path: `rif` |

---

## 4. Pedidos

**Estados válidos:** `nuevo`, `picking`, `check_picking`, `packing`, `para_facturar`, `facturando`, `enviado`, `entregado`, `cancelado`.

| Método | Ruta | Descripción | Body / Params |
|--------|------|-------------|----------------|
| POST | `/pedidos/` | Crear pedido | `PedidoResumen`: cliente, rif, observacion, total, subtotal, productos (array de ProductoPedido). Opcional: estado. El backend asigna `nuevo` si no se envía. |
| GET | `/obtener_pedidos/` | Listar pedidos | Query opcionales: `estados[]`, `fecha_desde`, `fecha_hasta` (YYYY-MM-DD) |
| GET | `/pedidos/administracion/` | Pedidos para administración | — |
| GET | `/pedidos/picking/` | Pedidos en picking | — |
| GET | `/pedidos/por_estado/{estado}` | Por estado | Path: estado |
| GET | `/pedido/{pedido_id}` | Un pedido por ID | Path: pedido_id (ObjectId string) |
| GET | `/pedidos/por_cliente/{rif}` | Pedidos de un cliente | Path: rif |
| POST | `/pedidos/armados/` | Registrar pedido armado | `PedidoArmado`: cliente, rif, observacion, total, productos |
| PUT | `/pedidos/actualizar_estado/{pedido_id}` | Cambiar estado | Body: `{ "nuevo_estado", "verificaciones"?, "usuario"?, "pin"? }` (pin para validación con facturas vencidas) |
| PATCH | `/pedidos/actualizar_cantidades/{pedido_id}` | Actualizar cantidades encontradas | Body: `{ "cantidades": { "codigo_producto": cantidad } }` |
| PATCH | `/pedidos/actualizar_picking/{pedido_id}` | Actualizar info picking | Body: PickingInfo (usuario, fechainicio_picking, fechafin_picking, estado_picking) |
| PATCH | `/pedidos/actualizar_packing/{pedido_id}` | Actualizar packing | Body: PackingInfo |
| PATCH | `/pedidos/actualizar_envio/{pedido_id}` | Actualizar envío | Body: EnvioInfo |
| PUT | `/pedidos/{pedido_id}/cancelar` | Cancelar pedido | Body con usuario, etc. |
| PUT | `/pedidos/actualizar/{id}` | Actualizar pedido completo | Body: campos a actualizar |
| POST | `/pedidos/{pedido_id}/finalizar_check_picking` | Finalizar check picking | Body: { verificaciones, usuario } |
| GET | `/pedidos/checkpicking/` | Listar para check picking | — |
| POST | `/pedidos/{pedido_id}/validar` | Validar pedido (PIN) | Body: `{ "pin": "string" }` |
| GET | `/conductores/` | Listar conductores | — |
| GET | `/pedidos/para_facturar/` | Pedidos para facturar | — |
| PUT | `/pedidos/actualizar_facturacion/{pedido_id}` | Actualizar facturación | Body: FacturacionInfo |
| PUT | `/pedidos/finalizar_facturacion/{pedido_id}` | Finalizar facturación | — |

**ProductoPedido (dentro de pedido):** codigo, descripcion, precio, descuento1–4, cantidad_pedida, cantidad_encontrada, subtotal, cantidad, cantidad_pendiente; opcionales: existencia, laboratorio, fv, nacional, dpto, frio, advertencia, calendario, lotes, limpieza.

---

## 5. Inventario

| Método | Ruta | Descripción | Body / Params |
|--------|------|-------------|----------------|
| GET | `/inventario/` | Listar inventario | — |
| GET | `/inventario_maestro/` | Inventario maestro | —. Incluye `stock_minimo`, `stock_maximo` por producto. |
| GET | `/inventario_maestro/{id}` | Un producto por ID | Path: id |
| POST | `/inventario_maestro/` | Crear producto | Body: codigo (requerido), descripcion, existencia, precio, dpto, nacional, laboratorio, fv, descuento1–3, **stock_minimo**, **stock_maximo** (opc.). |
| PUT | `/inventario_maestro/{id}` | Actualizar producto | Body: campos a actualizar (incl. **stock_minimo**, **stock_maximo**). |
| POST | `/subir_inventario/` | Carga de inventario (archivo/form) | Form/archivo. Excel puede incluir columnas **Stock_minimo**, **Stock_maximo**. |
| POST | `/convenios/cargar` | Cargar convenios | Body: ConvenioCarga (fecha, usuario, descripcion, estado, clientes[], productos{codigo: precio}) |
| POST | `/inventarios/upload-excel` | Subir Excel | — |
| POST | `/inventarios/cargar-existencia` | Cargar existencia | — |
| POST | `/inventarios/{inventario_id}/items` | Items de inventario | — |

---

## 6. Contacto y reclamos (públicos)

### Contacto

- **POST** `/contacto`
- **Body:** `{ "nombre": "string", "email": "string", "telefono": "string", "mensaje": "string" }`
- **Respuesta:** `{ "message": "Mensaje recibido correctamente" }`

### Reclamos

- **POST** `/reclamos/cliente`  
  Body: `{ "pedido_id": "string", "rif": "string", "cliente": "string", "productos": [{ "id", "descripcion", "cantidad", "motivo" }], "observacion": "string", "fecha": "string" }`  
  Respuesta: `{ "message": "...", "reclamo_id": "string" }`
- **GET** `/reclamos/cliente/{rif}`  
  Respuesta: array de reclamos del cliente.

---

## 7. Módulos

- **GET** `/modulos/` — Lista de módulos (cada uno con `_id` como string).
- **GET** `/modulos/{modulo_id}` — Un módulo por ID.

---

## 8. Transacciones (prefix `/transaccion`)

- **POST** `/transaccion/transaccion`  
  Body: `{ "tipo_movimiento": "compra"|"descargo"|"cargo"|"venta"|"ajuste"|"devolucion"|"transferencia"|"pedido"|"apartado"|"anulacion", "usuario": "string", "observaciones": "string", "productos": [{ "producto_codigo": "string", "cantidad": number }] }`
- **POST** `/transaccion/anular-transaccion`  
  Body: `{ "movimiento_id": "string", "usuario": "string" }`

---

## 9. Formatos de impresión (prefix `/formatos-impresion`)

- **GET** `/formatos-impresion/` — Listar.
- **GET** `/formatos-impresion/{tipo}` — Por tipo.
- **POST** `/formatos-impresion/` — Crear.
- **PUT** `/formatos-impresion/{tipo}` — Actualizar.
- **DELETE** `/formatos-impresion/{tipo}` — Eliminar por tipo.
- **DELETE** `/formatos-impresion/id/{id}` — Eliminar por ID.
- **GET** `/formatos-impresion/{tipo}/preview` — Vista previa.

---

## 10. Facturación dinámica (prefix `/pedidos` en main)

Rutas completas (el router tiene prefix `/pedidos`, las rutas del router empiezan por `/pedidos/`):

- **GET** `/pedidos/pedidos/{pedido_id}/factura-preliminar` — Factura preliminar (devuelve JSON con `html`, `datos_empresa`, `configuracion_diseno`, `pedido_id`, `numero_factura`, `fecha_factura`).
- **GET** `/pedidos/pedidos/{pedido_id}/factura-final` — Factura final (mismo formato).
- **GET** `/pedidos/pedidos/{pedido_id}/etiqueta-envio` — Etiqueta de envío.

---

## 11. Punto de venta

- **POST** `/punto-venta/ventas`  
  Body: `{ "usuario": "string", "cliente_rif": "string", "cliente_nombre": "string", "productos": [{ "codigo", "descripcion", "cantidad", "precio_unitario", "descuento", "subtotal" }], "total": number, "metodo_pago": "string", "observaciones": "string" }`
- **GET** `/punto-venta/ventas` — Listar ventas.
- **GET** `/punto-venta/ventas/{venta_id}` — Una venta por ID.

---

## 12. Chatbot IA

- **POST** `/api/chat`  
  Body: `{ "prompt": "string" }`  
  Respuesta: `{ "response": "string" }`  
  (Sin autenticación en el endpoint actual.)

---

## 13. Usuario admin (actualización)

- **GET** `/usuarios/admin/` — Listar usuarios admin (cada item: _id, usuario, nombre, rol, modulos; sin password).
- **PATCH** `/usuarios/admin/{id}` — Actualizar por _id. Body: `{ "modulos"?, "rol"?, "nombre"?, "telefono"?, "password"? }`.
- **PUT** `/admin/usuarios/{usuario}` — Actualizar por nombre usuario. Body (parcial): `{ "usuario", "password", "rol", "modulos", "nombreCompleto", "nombre", "telefono", "identificador" }`.

---

## 14. Control de fallas (productos faltantes)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/fallas/` | Listar productos con cantidad_pedida > cantidad_encontrada. Query opcional: `?pedido_id=...`. Cada item: pedido_id, item_index, codigo, descripcion, cantidad_pedida, cantidad_encontrada, proveedor_id, proveedor_empresa, precio_venta. |
| PATCH | `/fallas/{pedido_id}` | Actualizar proveedor_id y/o precio_venta de un item faltante. Body: `{ "proveedor_id"?, "precio_venta"? }`. Query opcional: `?item_index=...`. |

---

## 15. Cuentas por cobrar

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/cuentas-por-cobrar/vigentes` | Facturas con días de crédito restantes (numero, cliente, rif, monto, fecha_emision, dias_restantes, fecha_vencimiento). |
| GET | `/cuentas-por-cobrar/vencidas` | Facturas vencidas (dias_vencidos, etc.). |
| GET | `/cuentas-por-cobrar/total` | `{ "total" }` monto total por cobrar. |

---

## 16. Cuentas por pagar

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/cuentas-por-pagar/` | Obligaciones con proveedores (proveedor_empresa, proveedor_rif, concepto, monto, fecha_vencimiento, dias_credito). |
| GET | `/cuentas-por-pagar/total` | `{ "total" }` monto total por pagar. |

---

## 17. Facturas finalizadas

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/facturas/top-clientes` | Top 10 clientes (cliente, rif, total, cantidad_pedidos). |
| GET | `/facturas/clientes-poco-frecuentes` | Clientes poco frecuentes (cliente, rif, ultimo_pedido, dias_sin_comprar). |
| GET | `/facturas/pagadas` | Facturas pagadas (numero, cliente, rif, monto, fecha_pago). |

---

## 18. Proveedores

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/proveedores/` | Listar proveedores. |
| POST | `/proveedores/` | Crear. Body: rif, empresa, dias_credito, condiciones_comerciales (%), pronto_pago_porcentaje (%). |
| PUT | `/proveedores/{id}` | Actualizar. |
| DELETE | `/proveedores/{id}` | Eliminar. |

---

## 19. Compras

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/compras/totalizar` | Body: `{ "proveedor_id", "productos": [{ "codigo", "cantidad" }] }`. Suma cantidades al inventario. |

---

## 20. Órdenes de compra

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/ordenes-compra/` | Listar (proveedor_empresa, proveedor_rif, total, totalizada, fecha). |
| POST | `/ordenes-compra/` | Crear. Body: proveedor_id, proveedor_rif?, productos: [{ codigo, descripcion?, costo?, cantidad }], total. |
| GET | `/ordenes-compra/{id}` | Detalle. |
| PUT | `/ordenes-compra/{id}` | Actualizar productos y total. |
| POST | `/ordenes-compra/{id}/totalizar` | Marcar totalizada y sumar cantidades al inventario. |

---

## 21. Lista comparativa

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/listas-comparativas/` | Listar listas por proveedor. |
| GET | `/listas-comparativas/productos` | Todos los productos de todas las listas (precio_final con descuento). |
| POST | `/listas-comparativas/upload` | FormData: file (Excel), proveedor_id. Columnas: codigo, descripcion, marca, precio, existencia. |

---

## 22. Dashboard finanzas

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/finanzas/resumen` | `{ productos_vendidos, valor_vendido, utilidad }`. |
| GET | `/finanzas/top-productos?tipo=mas` | Top 10 más vendidos. |
| GET | `/finanzas/top-productos?tipo=menos` | Top 10 menos vendidos. |
| GET | `/finanzas/graficas` | Array `{ mes, valor }` por mes. |
| GET | `/finanzas/gastos` | `{ total }` gastos. |

---

## 23. Gastos

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/gastos/` | Registrar. Body: monto, descripcion?, fecha?, categoria?. |
| GET | `/gastos/?desde=YYYY-MM-DD&hasta=YYYY-MM-DD` | Listar con filtros. |
| DELETE | `/gastos/{id}` | Eliminar. |

---

## 24. Cierre diario

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/cierre-diario/?fecha=YYYY-MM-DD` | Resumen del día. |
| GET | `/cierre-diario/?desde=YYYY-MM-DD&hasta=YYYY-MM-DD` | Resumen por rango. Respuesta: productos_vendidos, cantidad_clientes, monto_total, gastos, utilidad. |

---

## 25. Tasa BCV

| Método | Ruta   | Auth   | Descripción |
|--------|--------|--------|-------------|
| GET    | `/bcv/` | Público | Devuelve `{ "tasa": number }` (tasa actual en USD; Bs = $ × tasa). |
| PUT    | `/bcv/` | Admin (Bearer) | Body: `{ "tasa": number }` (también acepta `rate` o `valor`). Respuesta: `{ "ok": true, "message": "Tasa BCV actualizada" }`. |

Referencia: `docs/BACKEND-BCV.md`.

---

## 26. Resumen para el frontend Vite

1. **Variable de entorno:** `VITE_API_URL` = base del backend (ej: `https://droclven-back.onrender.com`).
2. **Llamadas:** `fetch(\`${import.meta.env.VITE_API_URL}/ruta\`, { method, headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token }, body: JSON.stringify(...) })`.
3. **Páginas a conectar (sugerencia):**
   - Login/registro → `/login/`, `/register/`.
   - Contacto → POST `/contacto`.
   - Reclamos → POST `/reclamos/cliente`, GET `/reclamos/cliente/{rif}`.
   - Catálogo/productos → GET `/inventario/` o `/inventario_maestro/`.
   - Pedidos (si aplica) → según flujo: POST `/pedidos/`, GET `/obtener_pedidos/`, GET `/pedidos/por_cliente/{rif}`.
   - Chat → POST `/api/chat`.
4. **IDs:** Los `_id` de MongoDB vienen como string en las respuestas (el backend los convierte).
5. **Errores:** Respuestas de error con `detail` (string o lista); usar `response.ok` y `response.json()` para mensajes.

Con esto la IA del frontend puede adaptar el sitio estático a la lógica y rutas de este backend.
