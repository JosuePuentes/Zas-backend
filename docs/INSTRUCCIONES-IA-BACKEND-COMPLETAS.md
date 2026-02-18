# Instrucciones completas para la IA del backend (especificación desde el frontend)

Este documento referencia la **especificación completa de endpoints** que el frontend Virgen del Carmen espera. La implementación del backend debe alinearse con esa especificación.

---

## Origen del documento de especificación

La especificación detallada (endpoints, cuerpos, flujos) está en el **repositorio del frontend**:

- **Archivo:** `docs/INSTRUCCIONES-IA-BACKEND-COMPLETAS.md`
- **Repositorio:** https://github.com/JosuePuentes/Virgen-del-carmen-frontend
- **Enlace directo:** https://github.com/JosuePuentes/Virgen-del-carmen-frontend/blob/main/docs/INSTRUCCIONES-IA-BACKEND-COMPLETAS.md

**Cómo usarlo:**

1. **Opción A (recomendada):** Abre el archivo en el repo del frontend, copia todo el contenido (Ctrl+A, Ctrl+C) y pégalo en el chat de la IA del backend junto con:  
   *"Implementa todos los endpoints descritos en este documento para el backend de Virgen del Carmen."*

2. **Opción B:** Si la IA tiene acceso al repo del frontend, indica:  
   *"Lee el archivo docs/INSTRUCCIONES-IA-BACKEND-COMPLETAS.md del repositorio Virgen-del-carmen-frontend (https://github.com/JosuePuentes/Virgen-del-carmen-frontend) e implementa todos los endpoints que describe para mi backend."*

3. **Opción C:** Después de copiar el contenido del documento del frontend aquí (en este mismo archivo o en `docs/ESPEC-FRONTEND-COMPLETA.md`), pide a la IA del backend:  
   *"Implementa todos los endpoints descritos en docs/INSTRUCCIONES-IA-BACKEND-COMPLETAS.md (o docs/ESPEC-FRONTEND-COMPLETA.md)."*

---

## Áreas que debe cubrir el backend (según la especificación del frontend)

La especificación del frontend incluye, entre otros:

| Área | Descripción |
|------|-------------|
| **Dashboard** | Resumen, contadores, datos para el panel principal |
| **Solicitudes** | Solicitudes de nuevos clientes (pendientes, aprobar, rechazar) |
| **Pedidos** | CRUD pedidos, listados por estado, administración |
| **Picking** | Pedidos en picking, actualizar cantidades, info picking |
| **Packing** | Pedidos en packing, actualizar packing |
| **Facturación** | Preliminar, final, estados para facturar |
| **Control de fallas** | PATCH para proveedor y precio de venta (cuando aplique) |
| **Inventario** | Maestro, productos, existencias, cargas |
| **Clientes** | CRUD clientes, listar, crear, editar |
| **Usuarios** | Usuarios administrativos (crear, editar, listar si aplica) |
| **Cuentas por cobrar / por pagar** | Endpoints que el frontend use para estos módulos |
| **Facturas finalizadas** | Listado y detalle de facturas finalizadas |
| **Proveedores** | CRUD o listado de proveedores |
| **Compras** | Registro y listado de compras |
| **Órdenes de compra** | Crear, listar, actualizar órdenes de compra |
| **Lista comparativa** | Carga Excel por proveedor, buscador |
| **Finanzas** | Endpoints para finanzas |
| **Gastos** | Registro y listado de gastos |
| **Cierre diario** | Endpoint(s) para cierre diario |
| **Tabla resumen** | La especificación incluye una tabla resumen de todos los endpoints |

---

## Tareas para la IA del backend

1. **Leer la especificación completa** desde el frontend (archivo o contenido pegado) y comparar con lo ya implementado en este backend (`BACKEND-ESTADO-PARA-FRONTEND.md`, rutas en `src/api/routes/`).

2. **Implementar los endpoints que falten** según la especificación: mismos métodos, rutas, cuerpos de request y formato de respuesta.

3. **Mantener actualizado** `BACKEND-ESTADO-PARA-FRONTEND.md` con todas las rutas nuevas o modificadas.

4. **CORS:** Mantener permitidos `https://virgen-del-carmen-frontend.vercel.app` y `http://localhost:3000` (y puertos de desarrollo que use Vite).

5. **Multi-tenant:** Seguir usando `get_db(request)` (base de datos según Origin) en las rutas que correspondan.

---

## Referencias en este repositorio

- **API actual:** `BACKEND-ESTADO-PARA-FRONTEND.md` (raíz)
- **Panel admin (guía frontend):** `docs/PANEL-ADMIN-PARA-FRONTEND.md`
- **Instrucciones generales backend:** `docs/INSTRUCCIONES-PARA-IA-BACKEND.md`

Cuando el contenido completo de `INSTRUCCIONES-IA-BACKEND-COMPLETAS.md` del frontend se copie aquí o se enlace, la IA del backend debe usarlo como fuente de verdad para implementar o completar la API.
