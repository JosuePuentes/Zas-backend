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

---

## 1. Configuración base

| Concepto | Valor |
|----------|--------|
| **Base URL** | Variable de entorno en Vercel: `VITE_API_URL` (ej: `https://droclven-back.onrender.com`) |
| **Content-Type** | `application/json` en POST/PUT/PATCH |
| **Autenticación** | JWT en header: `Authorization: Bearer <token>` (donde el backend lo requiera; actualmente muchos endpoints no validan token) |

---

## 2. Autenticación

### 2.1 Registro de cliente (público)

- **POST** `/register/`
- **Body:** `UserRegister`
```json
{
  "email": "string",
  "password": "string",
  "rif": "string",
  "direccion": "string",
  "telefono": "string",
  "encargado": "string",
  "activo": true,
  "descuento1": 0,
  "descuento2": 0,
  "descuento3": 0
}
```
- **Respuesta:** `{ "message": "Cliente registrado exitosamente" }` o error 400 (correo/RIF ya existe).

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
- Guardar `access_token` y enviarlo en `Authorization: Bearer <access_token>` en llamadas que lo requieran. El backend usa el mismo token para identificar al cliente (rif, email en el payload del JWT).

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
  "modulos": ["string"],
  "usuario": "string"
}
```

---

## 3. Clientes

| Método | Ruta | Descripción | Body / Params |
|--------|------|-------------|----------------|
| POST | `/clientes/` | Crear cliente | `Client`: rif, encargado, direccion, telefono, email, password, descripcion, dias_credito, limite_credito, activo, descuento1, descuento2, descuento3 |
| GET | `/clientes/all` | Listar todos (con `_id` como string) | — |
| GET | `/clientes/` | Lista resumida (email, rif, encargado) | — |
| GET | `/clientes/{rif}` | Cliente por RIF | Path: `rif` |
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
| PUT | `/pedidos/actualizar_estado/{pedido_id}` | Cambiar estado | Body: `{ "nuevo_estado": "string", "verificaciones": {}, "usuario": "string" }` |
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
| GET | `/inventario_maestro/` | Inventario maestro | — |
| GET | `/inventario_maestro/{id}` | Un producto por ID | Path: id |
| PUT | `/inventario_maestro/{id}` | Actualizar producto | Body: campos a actualizar |
| POST | `/subir_inventario/` | Carga de inventario (archivo/form) | Form/archivo según implementación |
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

- **PUT** `/admin/usuarios/{usuario}`  
  Body (parcial): `{ "usuario", "password", "rol", "modulos", "nombreCompleto", "identificador" }`

---

## 14. Resumen para el frontend Vite

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
