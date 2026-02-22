# Backend – Descuentos en clientes

## Texto para copiar/pegar a la IA del backend

> El módulo Clientes en el área admin tiene un botón Editar por cada cliente. Al guardar, el frontend llama:
>
> **PATCH /clientes/{rif}**
>
> Body (campos editables):
>
> ```json
> {
>   "empresa": "string",
>   "encargado": "string",
>   "direccion": "string",
>   "telefono": "string",
>   "email": "string",
>   "password": "string (opcional, solo si se cambia)",
>   "dias_credito": 0,
>   "limite_credito": 0,
>   "descuento_comercial": 0,
>   "descuento_pronto_pago": 0
> }
> ```
>
> - **Autenticación:** Token admin en `Authorization: Bearer <token>` (cuando se edita desde el módulo admin).
> - **RIF:** No se envía en el body (es el identificador en la URL). El backend no debe permitir cambiar el RIF.
>
> Detalle completo: docs/BACKEND-CLIENTES-DESCUENTOS.md

---

## Campos de descuento

En el modelo de cliente (crear y actualizar) además de `descuento1`, `descuento2`, `descuento3` existen:

| Campo | Tipo | Descripción |
|--------|------|-------------|
| **descuento_comercial** | number (%) | Descuento comercial. En catálogo cliente: `precio_final = precio × (1 - descuento_comercial/100)`. |
| **descuento_pronto_pago** | number (%) | Descuento por pronto pago. Se envía al backend y se muestra en listado de clientes. |

---

## PATCH /clientes/{rif} (actualizar cliente)

- **Uso:** Edición desde admin (modal Editar cliente) o desde área cliente (Mi cuenta).
- **Autenticación:** En el módulo admin el frontend envía token admin en `Authorization: Bearer <token>`.
- **Path:** `rif` — identificador del cliente. **No se puede cambiar el RIF**; el backend ignora `rif` si viene en el body.
- **Body (todos opcionales):** Solo se envían los campos que se modifican.
  - `empresa`, `encargado`, `direccion`, `telefono`, `email`
  - `password` — opcional; solo si se cambia la contraseña (el backend la hashea antes de guardar).
  - `dias_credito`, `limite_credito`
  - `descuento_comercial`, `descuento_pronto_pago`
  - `descuento1`, `descuento2`, `descuento3`, `activo`, `descripcion`
- **Respuesta 200:** `{ "message": "Documento actualizado correctamente" }`.
- **Respuesta 404:** Cliente no encontrado.

## Otros endpoints

- **POST /clientes/** (crear): Acepta `descuento_comercial` y `descuento_pronto_pago` en el body (opcionales, default 0).
- **GET /clientes/{rif}** (detalle): Incluye `descuento_comercial` y `descuento_pronto_pago`.
- **GET /clientes/all** y listados: Incluyen estos campos si están en BD.

## Uso en frontend

- **Admin – Crear/editar cliente:** Mostrar campos "Descuento comercial (%)" y "Descuento pronto pago (%)" y enviarlos al backend. RIF solo lectura en el modal Editar. Guardar → PATCH /clientes/{rif} con los datos actualizados.
- **Listado de clientes:** Mostrar ambas columnas.
- **Catálogo cliente:** Aplicar `descuento_comercial` al precio: `precio_final = precio × (1 - descuento_comercial/100)`.
