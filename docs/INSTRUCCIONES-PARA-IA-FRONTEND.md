# Instrucciones para la IA del frontend (Virgen del Carmen)

Copia y pega este documento (o su enlace) cuando trabajes en el frontend para que las llamadas al backend y las respuestas sean las correctas.

---

## 1. Contexto: qué hace ya el backend

El backend (FastAPI en Render) está desplegado y operativo. Ofrece:

- **Login unificado:** una sola pantalla de login con pestañas Cliente / Administrador. Según el tipo, se llama a `POST /login/` (cliente) o `POST /login/admin/` (admin) y se redirige según la respuesta.
- **Registro de clientes** con estado pendiente de aprobación; el admin aprueba o rechaza desde el panel.
- **Panel admin** con módulos según permisos (`modulos` en la respuesta del login admin): solicitudes de clientes, pedidos (administración, picking, packing, envíos), clientes, inventario.
- **Multi-tenant:** el backend elige la base de datos según el **Origin** de la petición (el dominio desde el que se llama). No hace falta cambiar nada en el frontend; solo llamar desde el mismo dominio (Vercel o localhost) que el usuario usa.

Las respuestas del backend siguen el formato indicado abajo. Úsalas tal cual para mostrar mensajes y redirigir.

---

## 2. Configuración base

| Concepto | Valor |
|----------|--------|
| **Base URL** | `import.meta.env.VITE_API_URL` (en Vercel: ej. `https://droclven-back.onrender.com`) |
| **Headers en POST/PUT/PATCH** | `Content-Type: application/json` |
| **Headers con auth** | Añadir `Authorization: Bearer <access_token>` (token devuelto por login) |
| **CORS** | El backend ya permite `https://virgen-del-carmen-frontend.vercel.app` y `http://localhost:3000` |

Todas las peticiones al backend deben ir a:  
`${import.meta.env.VITE_API_URL}/ruta`  
(p. ej. `${import.meta.env.VITE_API_URL}/login/`).

---

## 3. Login y respuestas correctas

### 3.1 Login cliente

- **Método y ruta:** `POST /login/`
- **Body:** `{ "email": "string", "password": "string" }`

**Respuesta 200 (éxito):**

```json
{
  "access_token": "string",
  "token_type": "bearer",
  "username": "email del usuario",
  "modules": [],
  "role": "client",
  "rif": "string"
}
```

- Guardar `access_token` (localStorage/sessionStorage o estado) y usarlo en `Authorization: Bearer <token>` en las rutas del área cliente.
- Usar `role === "client"` para redirigir al área de cliente (catálogo, pedidos, reclamos, etc.).
- Usar `rif` para llamadas que lo pidan (p. ej. pedidos del cliente).

**Respuestas de error (mostrar el mensaje al usuario y no dar acceso):**

- **403** con `detail: "Pendiente de aprobación. Su solicitud está en revisión."`  
  → Mostrar exactamente ese mensaje. No redirigir al catálogo ni al panel.
- **403** con `detail: "Solicitud rechazada. Contacte al administrador."`  
  → Mostrar exactamente ese mensaje. No dar acceso.
- **401** → Credenciales incorrectas (email o contraseña).

Siempre leer `detail` del JSON de error para mostrar el mensaje correcto.

---

### 3.2 Login administrador

- **Método y ruta:** `POST /login/admin/`
- **Body:** `{ "usuario": "string", "password": "string" }`  
  (claves `usuario` y `password`, no `username` ni `email`).

**Respuesta 200 (éxito):**

```json
{
  "access_token": "string",
  "token_type": "bearer",
  "role": "admin",
  "rol": "master",
  "modulos": ["solicitudes_clientes", "pedidos", "inventario", "clientes"],
  "usuario": "string"
}
```

- Guardar `access_token` y usarlo en **todas** las peticiones del panel admin: `Authorization: Bearer <token>`.
- **role** siempre es `"admin"` en login admin. Usar `role === "admin"` para redirigir al panel administrativo.
- **modulos** define qué secciones del menú mostrar (ver tabla más abajo).
- **rol** y **usuario** pueden usarse para mostrar nombre o rol en la cabecera.

**Respuestas de error:**

- **401** con `detail: "Usuario no encontrado"` o `"Contraseña incorrecta"` → Mostrar mensaje y no dar acceso.

---

## 4. Registro de cliente

- **Método y ruta:** `POST /register/`
- **Body (ejemplo):** incluir al menos `email`, `password`, `rif`, y opcionalmente `empresa`, `direccion`, `telefono`, `encargado`, `activo`, `descuento1`, `descuento2`, `descuento3`.

**Respuesta 200:**  
`{ "message": "Cliente registrado exitosamente. Su cuenta está pendiente de aprobación." }`

Tras el registro, el cliente queda con `estado_aprobacion: "pendiente"` hasta que un admin lo apruebe. El cliente no podrá hacer login con éxito hasta que un admin llame a `PATCH /clientes/{rif}/aprobar`.

---

## 5. Panel admin: menú según `modulos`

Mostrar en el menú **solo** las secciones cuyo valor esté en el array `modulos` de la respuesta del login admin:

| Valor en `modulos`        | Sección en el menú |
|---------------------------|---------------------|
| `solicitudes_clientes`    | Solicitudes de clientes (aprobar/rechazar) |
| `pedidos`                 | Pedidos: Dashboard, Administración, Picking, Packing, Envíos, Crear pedido |
| `inventario`              | Inventario |
| `clientes`                | Clientes (listar, crear, editar) |

Además se recomienda una entrada **Dashboard** (resumen con contadores) siempre visible para el admin.

En **todas** las peticiones del panel admin enviar el header:  
`Authorization: Bearer <access_token>`.

---

## 6. Rutas del panel admin (resumen)

Para que las respuestas sean correctas, usar estas rutas y métodos. Detalle completo en el documento **PANEL-ADMIN-PARA-FRONTEND.md** (mismo repo backend).

- **Dashboard:** `GET /clientes/solicitudes/pendientes`, `GET /pedidos/administracion/`, `GET /pedidos/picking/`, `GET /pedidos/por_estado/{estado}`.
- **Solicitudes de clientes:** `GET /clientes/solicitudes/pendientes`, `PATCH /clientes/{rif}/aprobar`, `PATCH /clientes/{rif}/rechazar`.
- **Pedidos – Administración:** `GET /pedidos/administracion/`, y para cambiar estado `PUT /pedidos/actualizar_estado/{pedido_id}`.
- **Picking:** `GET /pedidos/picking/`, `PATCH /pedidos/actualizar_cantidades/{pedido_id}`, `PATCH /pedidos/actualizar_picking/{pedido_id}`, etc.
- **Packing:** `GET /pedidos/por_estado/packing`, `PATCH /pedidos/actualizar_packing/{pedido_id}`.
- **Envíos:** `GET /pedidos/por_estado/enviado`, `PATCH /pedidos/actualizar_envio/{pedido_id}`, `GET /conductores/`.
- **Crear clientes:** `POST /clientes/`. Listar: `GET /clientes/all` o `GET /clientes/`. Editar: `PATCH /clientes/{rif}`.
- **Crear pedidos:** `POST /pedidos/` (body con cliente, rif, productos, total, etc.). Catálogo: `GET /inventario_maestro/`.
- **Inventario:** `GET /inventario_maestro/`, `GET /inventario_maestro/{id}`, `PUT /inventario_maestro/{id}`.

Los `_id` de MongoDB vienen como **string** en las respuestas.

---

## 7. Errores del backend

Las respuestas de error suelen tener un JSON con el campo **`detail`** (string o array de strings). Siempre:

- Comprobar `!response.ok` y leer `await response.json()`.
- Mostrar al usuario el contenido de `detail` (si es array, unir o mostrar el primer mensaje).
- No asumir mensajes propios; usar los que envía el backend para que las respuestas sean las correctas.

---

## 8. Dónde está la documentación completa

En el **repositorio del backend** (https://github.com/JosuePuentes/Zas-backend):

- **BACKEND-ESTADO-PARA-FRONTEND.md** (raíz): Todas las rutas, métodos, cuerpos y respuestas de la API.
- **docs/PANEL-ADMIN-PARA-FRONTEND.md**: Guía del panel admin: qué pantallas crear y qué rutas usar en cada una.

Puedes abrir esos archivos en GitHub o, si tienes acceso al repo del backend, leerlos desde ahí para que la IA del frontend use siempre las rutas y formatos correctos.
