# Backend – Descuentos en clientes

## Campos de descuento

En el modelo de cliente (crear y actualizar) además de `descuento1`, `descuento2`, `descuento3` existen:

| Campo | Tipo | Descripción |
|--------|------|-------------|
| **descuento_comercial** | number (%) | Descuento comercial. En catálogo cliente: `precio_final = precio × (1 - descuento_comercial/100)`. |
| **descuento_pronto_pago** | number (%) | Descuento por pronto pago. Se envía al backend y se muestra en listado de clientes. |

## Endpoints

- **POST /clientes/** (crear): Acepta `descuento_comercial` y `descuento_pronto_pago` en el body (opcionales, default 0).
- **PATCH /clientes/{rif}** (actualizar): Acepta body parcial con `descuento_comercial`, `descuento_pronto_pago`.
- **GET /clientes/{rif}** (detalle): Incluye en la respuesta `descuento_comercial` y `descuento_pronto_pago`.
- **GET /clientes/all** y listados: Los documentos devueltos incluyen estos campos si están guardados en BD.

## Uso en frontend

- **Admin – Crear/editar cliente:** Mostrar campos "Descuento comercial (%)" y "Descuento pronto pago (%)" y enviarlos al backend.
- **Listado de clientes:** Mostrar ambas columnas.
- **Catálogo cliente:** Aplicar `descuento_comercial` al precio: `precio_final = precio × (1 - descuento_comercial/100)`.
