# Módulo de informes – Backend

El módulo de informes del frontend usa **los endpoints actuales**. No hace falta crear nuevos endpoints si ya existen.

## Mapeo informe → endpoint(s)

| Informe | Endpoint(s) |
|--------|-------------|
| **Ventas** | `GET /facturas/pagadas` o `GET /facturas/` (según necesidad) |
| **Inventario** | `GET /inventario_maestro/` |
| **Cuentas por cobrar** | `GET /cuentas-por-cobrar/vigentes`, `GET /cuentas-por-cobrar/vencidas` |
| **Cuentas por pagar** | `GET /cuentas-por-pagar/` |
| **Clientes** | `GET /clientes/all` o `GET /clientes/` |
| **Gastos** | `GET /gastos/?desde=YYYY-MM-DD&hasta=YYYY-MM-DD` |
| **Proveedores** | `GET /proveedores/` |
| **Compras** | `GET /ordenes-compra/` |
| **Picking** | `GET /pedidos/picking/` o `GET /pedidos/por_estado/picking` |
| **Packing** | `GET /pedidos/por_estado/packing` |
| **Solicitudes** | `GET /clientes/solicitudes/pendientes` |
| **Finanzas** | `GET /finanzas/resumen`, `GET /finanzas/gastos`, `GET /cuentas-por-cobrar/total`, `GET /cuentas-por-pagar/total` |

## Formato de respuesta

- Los endpoints devuelven **array** o **objeto** con facturas, items, clientes, etc., según corresponda.
- Sin cambios de contrato: el frontend consume las respuestas actuales.

## Gastos

- Debe soportar query params: **`?desde=YYYY-MM-DD`** y **`?hasta=YYYY-MM-DD`**.
- El backend ya los soporta en `GET /gastos/`.

## Autenticación

- **Todas las peticiones** del módulo de informes deben enviar el token de administrador:  
  `Authorization: Bearer <admin_token>`.
