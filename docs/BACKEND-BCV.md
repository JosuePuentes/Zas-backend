# Tasa BCV – Backend

Referencia para el backend: endpoints de tasa BCV (Banco Central de Venezuela).

## Reglas

- Todos los valores en BD están en **USD ($)**.
- La tasa BCV se usa solo para mostrar el equivalente en Bs: **Bs = $ × BCV**.
- Si el backend no responde, el frontend puede guardar la tasa en `localStorage`.

## Endpoints

| Método | Ruta   | Auth              | Descripción        |
|--------|--------|-------------------|--------------------|
| GET    | `/bcv/` | Opcional (público) | Devuelve la tasa actual |
| PUT    | `/bcv/` | Requerido (admin)  | Actualiza la tasa  |

### GET /bcv/

**Respuesta:**

```json
{ "tasa": 36.50 }
```

También se aceptan `rate` o `valor` como claves en el frontend (el backend siempre devuelve `tasa`).

### PUT /bcv/

**Request:**

- Header: `Authorization: Bearer <admin_token>`
- Header: `Content-Type: application/json`
- Body: `{ "tasa": 37.00 }` (también acepta `rate` o `valor`)

**Respuesta:**

```json
{ "ok": true, "message": "Tasa BCV actualizada" }
```

## Frontend

- Al hacer clic en **Actualizar** en el Dashboard, se muestra el mensaje verde **"Tasa BCV actualizada"** durante 3 segundos.
