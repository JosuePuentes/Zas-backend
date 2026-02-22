# Instrucciones para la IA del backend

Puedes enviarle algo como esto:

> **Catálogo público:** El frontend llama a **GET /catalogo/** sin header `Authorization` para el catálogo público (ruta `/catalogo`). El backend debe permitir acceso sin token.
>
> **Editar producto con foto:** Al editar un producto desde el admin, el frontend puede enviar **PUT /inventario_maestro/{id}** con `multipart/form-data` y un archivo en el campo **foto** para actualizar la imagen. El backend debe aceptar tanto **JSON** como **FormData** en ese endpoint.
>
> **Documentos de referencia en el repo del frontend:** docs/BACKEND-INVENTARIO.md, docs/INSTRUCCIONES-FRONTEND-CATALOGO-CLIENTE.md

---

## Estado en este backend

- **GET /catalogo/** — Permite acceso sin token (no exige `Authorization`). Uso: catálogo público y área cliente.
- **PUT /inventario_maestro/{id}** — Acepta **JSON** (`Content-Type: application/json`) o **multipart/form-data** con campo **foto** (archivo) para actualizar la imagen. Con FormData se pueden enviar también el resto de campos (codigo, descripcion, precio, etc.). La foto se guarda en `uploads/productos/{id}.{ext}` y se actualiza `foto_url` a `/archivos/productos/{id}.{ext}`. Las fotos se sirven en **GET /archivos/productos/...** (montaje estático).
- **GET /inventario_maestro/{id}/foto** — Redirige a la foto (URL externa o misma base + `/archivos/...`).
