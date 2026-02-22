# Instrucciones para el frontend – Catálogo en área cliente

Usar estas instrucciones en el frontend (o con la IA del frontend) para el catálogo de productos en el **área cliente** (panel del cliente logueado).

---

## 1. Endpoint del catálogo

En el área cliente **no** se debe llamar a `GET /inventario_maestro/` (ese endpoint exige token de **admin** y devuelve 401 con token de cliente).

**Usar en su lugar:**

- **GET** `{baseUrl}/catalogo/`

No requiere token de administrador. Puede enviarse el token del cliente en `Authorization: Bearer <token>` o no enviar token; el backend devuelve el catálogo en ambos casos.

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

> **Catálogo área cliente:** Llamar a **GET /catalogo/** (no a /inventario_maestro/). Respuesta: `{ "productos": [ ... ] }`. Cada producto tiene: _id, codigo, descripcion, marca, foto/foto_url, precio, descuento (%), precio_con_descuento, existencia. Mostrar foto (o placeholder si no hay), código, descripción, marca, precio, descuento y precio con descuento, y existencia. No se muestra costo.
