# Instrucciones para el frontend – Catálogo (público y área cliente)

Usar estas instrucciones en el frontend (o con la IA del frontend) para cualquier catálogo de productos: **catálogo público** (ruta `/catalogo`, sin login) y **área cliente** (panel del cliente logueado).

---

## 1. Endpoint del catálogo: usar siempre GET /catalogo/

**GET /inventario_maestro/** exige token de **admin**. Si no se envía token (catálogo público) o se envía token de cliente, el backend responde **401 Unauthorized**. Por eso **no** se debe usar para el catálogo.

**Usar en su lugar:**

- **GET** `{baseUrl}/catalogo/`

- **No requiere token:** Puede usarse en la página pública (CatalogoPage en `/catalogo`) sin enviar `Authorization`. También funciona con token de cliente en el área cliente.
- **Catálogo público (CatalogoPage):** Si actualmente usa `GET /inventario_maestro/` y no envía token, hay que cambiarlo a **GET /catalogo/** para evitar el 401.

**Ejemplo:** `GET https://droclven-back.onrender.com/catalogo/`

---

## 2. Respuesta

```json
{
  "productos": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "codigo": "X001",
      "descripcion": "Nombre del producto",
      "marca": "Marca o laboratorio",
      "foto": "https://...",
      "foto_url": "https://...",
      "precio": 10.50,
      "descuento": 5,
      "precio_con_descuento": 9.98,
      "existencia": 100
    }
  ]
}
```

---

## 3. Campos a mostrar en el catálogo

| Campo | Uso en la UI |
|--------|----------------|
| **foto** / **foto_url** | Imagen del producto. Si viene vacío, mostrar un cuadro/placeholder en blanco. Opcional: para la foto también se puede usar `GET /inventario_maestro/{_id}/foto` (redirección a la imagen; 404 si no hay). |
| **codigo** | Código del producto. |
| **descripcion** | Descripción. |
| **marca** | Marca (o laboratorio). |
| **precio** | Precio base (tachado si hay descuento). |
| **descuento** | Descuento en % (ej. 5 = 5%). Mostrar como "5% off" o similar. |
| **precio_con_descuento** | Precio final. Mostrarlo más destacado cuando `descuento > 0`. |
| **existencia** | Stock. Mostrar "Disponible" / "Agotado" según convenga. |

No mostrar costo ni utilidad (el backend no los envía en este endpoint).

---

## 4. Resumen para copiar/pegar

> **Catálogo (público y área cliente):** Llamar a **GET /catalogo/** (no a /inventario_maestro/). El backend exige token admin en /inventario_maestro/, por eso CatalogoPage (catálogo público en `/catalogo`) debe usar **GET /catalogo/** y no enviar token. Respuesta: `{ "productos": [ ... ] }`. Cada producto: _id, codigo, descripcion, marca, foto/foto_url, precio, descuento (%), precio_con_descuento, existencia. No se muestra costo.
