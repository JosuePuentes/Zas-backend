# Backend – Área cliente

Documento principal para los endpoints del panel de área cliente (`/cliente`) tras el login de un cliente aprobado.

**Autenticación:** Todas las rutas del área cliente deben enviar el token del cliente en el header:

```
Authorization: Bearer <access_token>
```

El `access_token` se obtiene de **POST /login/** (login cliente). El backend puede validar que el token sea de tipo cliente y que el `rif` del token coincida con el `rif` de la ruta cuando aplique.

---

## Texto para copiar/pegar a la IA del backend

> El frontend tiene un panel de área cliente (/cliente) tras el login de un cliente aprobado. Necesita estos endpoints (token cliente en Authorization: Bearer):
>
> - **GET /clientes/{rif}** — Datos del cliente (empresa, encargado, direccion, telefono, email, dias_credito, condiciones_comerciales)
> - **PATCH /clientes/{rif}** — Actualizar datos (body parcial)
> - **GET /cuentas-por-cobrar/cliente/{rif}** — Facturas pendientes de pago
> - **GET /facturas/pagadas/cliente/{rif}** — Facturas ya pagadas
>
> Detalle completo en este documento.

---

## Endpoints requeridos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/clientes/{rif}` | Datos del cliente para "Mi cuenta": empresa, encargado, direccion, telefono, email, dias_credito, condiciones_comerciales, limite_credito, limite_consumido, descuentos, etc. |
| PATCH | `/clientes/{rif}` | Actualizar datos del cliente (body parcial: encargado, direccion, telefono, email, password, etc.). Solo el propio cliente (rif del token = rif del path). |
| GET | `/cuentas-por-cobrar/cliente/{rif}` | Facturas pendientes de pago del cliente (pedidos entregados/enviados sin fecha_pago). |
| GET | `/facturas/pagadas/cliente/{rif}` | Facturas ya pagadas del cliente (pedidos con fecha_pago). |

### GET /clientes/{rif} — Campos de respuesta

Incluir al menos: `_id`, `rif`, `empresa`, `encargado`, `direccion`, `telefono`, `email`, `dias_credito`, `condiciones_comerciales`, `limite_credito`, `limite_consumido`, `descuento1`, `descuento2`, `descuento3`, **`descuento_comercial`**, **`descuento_pronto_pago`**, `facturas_vencidas`, `activo`.

- **condiciones_comerciales:** texto que resuma condiciones (ej. "30 días de crédito, límite $X"). Si no existe en BD, se construye desde `dias_credito` y `limite_credito`.
- **descuento_comercial** (%): aplicado en catálogo cliente: `precio_final = precio × (1 - descuento_comercial/100)`.
- **descuento_pronto_pago** (%): para listados e informes. Ver [BACKEND-CLIENTES-DESCUENTOS.md](BACKEND-CLIENTES-DESCUENTOS.md).

---

## Catálogo cliente (productos)

- **Endpoint:** **GET /catalogo/** — No requiere token admin (puede usarse con token cliente o sin token). Respuesta: `{ "productos": [ ... ] }`.
- **Campos por producto (solo lo necesario para el catálogo):**
  - **foto** / **foto_url**: URL de la foto (vacío si no hay).
  - **codigo**: Código del producto.
  - **descripcion**: Descripción.
  - **marca**: Marca (o laboratorio si no hay marca).
  - **precio**: Precio base.
  - **descuento**: Descuento en % (ej. 10 = 10%).
  - **precio_con_descuento**: Precio aplicando descuento (`precio × (1 - descuento/100)`).
  - **existencia**: Stock disponible.
  - **_id**: ID del producto (para enlace a foto o detalle).
- No se muestran costo ni utilidad. Para la foto, el frontend usa `foto`/`foto_url` o **GET** `/inventario_maestro/{id}/foto` (redirect a la imagen; 404 si no hay).

### GET /cuentas-por-cobrar/cliente/{rif}

Respuesta: array de facturas pendientes (sin `fecha_pago`) del cliente. Cada ítem: `numero`, `cliente`, `rif`, `total`, `fecha_emision`, `fecha_vencimiento`, opcionalmente `dias_restantes` o `dias_vencidos`.

### GET /facturas/pagadas/cliente/{rif}

Respuesta: array de facturas pagadas del cliente. Cada ítem: `numero`, `cliente`, `rif`, `total`/`monto`, `fecha_pago`, etc.

---

## Endpoints sugeridos (opcionales)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/promociones/` o `/promociones/cliente/{rif}` | Promociones vigentes (para el cliente). |
| GET | `/inventario_maestro/nuevos` | Productos nuevos (últimos incorporados o con flag). |
| GET | `/precios-bajaron/cliente/{rif}` | Productos con precio reducido (para mostrar al cliente). |
| GET | `/planificacion-compra/cliente/{rif}` | Sugerencias de compra (ej. basado en historial o stock). |

Estos pueden devolver `[]` o estructura mínima hasta que se implemente la lógica de negocio.

**Implementación actual:**  
- `GET /promociones/` y `GET /promociones/cliente/{rif}` → `[]`  
- `GET /inventario_maestro/nuevos` → `{ "productos": [ ... ] }` (últimos 20 productos; no requiere token admin)  
- `GET /precios-bajaron/cliente/{rif}` → `[]`  
- `GET /planificacion-compra/cliente/{rif}` → `[]`
