# Instrucciones para la IA del frontend: Solicitudes de clientes y usuario admin

Copia y pega este bloque cuando trabajes con la IA del frontend para implementar el módulo de solicitudes y el primer usuario administrativo.

---

## 1. Cómo crear un usuario administrativo

El backend ya tiene el endpoint. Desde Postman, Thunder Client, curl o cualquier cliente HTTP (o un formulario interno que llame al API):

- **Método:** POST  
- **URL:** `{VITE_API_URL}/register/admin/`  
- **Headers:** `Content-Type: application/json`  
- **Body (JSON):**
```json
{
  "usuario": "admin",
  "password": "TuPasswordSeguro123",
  "rol": "admin",
  "modulos": ["solicitudes_clientes", "pedidos", "inventario", "clientes"]
}
```

Ajusta `usuario`, `password` y la lista `modulos` según necesites. Con eso el admin puede hacer login en **POST** `/login/admin/` con `usuario` y `password` (no email). El frontend debe tener una pantalla de login para el área administrativa que use `/login/admin/` y guarde el token para las peticiones del panel admin.

---

## 2. Módulo administrativo: Solicitudes de nuevos clientes

### Comportamiento esperado

- Cuando un cliente se registra por **POST** `/register/` (o por el formulario de registro del frontend), queda con estado **pendiente de aprobación**.
- En el **área administrativa** debe existir un módulo llamado tipo **"Solicitudes de nuevos clientes"** (o "Solicitudes de clientes").
- Ese módulo debe:
  - Listar las solicitudes pendientes.
  - Mostrar por cada una: **nombre de la empresa**, **RIF**, **teléfono** (y opcionalmente encargado, email, dirección).
  - Tener un botón **Aprobar** y un botón **Rechazar**.

### API a usar (base URL = `VITE_API_URL`)

| Acción | Método | Ruta | Descripción |
|--------|--------|------|-------------|
| Listar pendientes | GET | `/clientes/solicitudes/pendientes` | Devuelve array de objetos con `_id`, `empresa`, `rif`, `telefono`, `encargado`, `email`, `direccion`, `estado_aprobacion`. Solo aparecen los que están en estado pendiente. |
| Aprobar | PATCH | `/clientes/{rif}/aprobar` | Reemplaza `{rif}` por el RIF del cliente. Respuesta: `{ "message": "Cliente aprobado. Ya puede iniciar sesión." }`. |
| Rechazar | PATCH | `/clientes/{rif}/rechazar` | Reemplaza `{rif}` por el RIF del cliente. Respuesta: `{ "message": "Solicitud rechazada." }`. |

Las peticiones del área admin deben enviar el token: `Authorization: Bearer <access_token>` (el que devuelve **POST** `/login/admin/`).

### Flujo cliente (login público)

- **Login cliente:** **POST** `/login/` con `email` y `password`.
- Si el backend responde **403** con `detail`:
  - **"Pendiente de aprobación. Su solicitud está en revisión."** → Mostrar ese mensaje y no dar acceso al resto de la app (no redirigir al catálogo ni al área de cliente).
  - **"Solicitud rechazada. Contacte al administrador."** → Mostrar ese mensaje y no dar acceso.
- Si el login es **200** y devuelve `access_token`, entonces el cliente está aprobado y debe tener acceso completo al área de clientes (catálogo, pedidos, reclamos, etc.).

### Resumen para la IA del frontend

1. **Usuario admin:** Crear uno con **POST** `/register/admin/` (body: `usuario`, `password`, `rol`, `modulos`). El área administrativa debe tener login con **POST** `/login/admin/` (usuario + password) y usar el token en las peticiones del panel.
2. **Módulo "Solicitudes de nuevos clientes":**  
   - Pantalla en el panel admin que llame a **GET** `/clientes/solicitudes/pendientes` y muestre una tabla/lista con empresa, RIF, teléfono (y los demás campos que quieras).  
   - Botón **Aprobar** → **PATCH** `/clientes/{rif}/aprobar`.  
   - Botón **Rechazar** → **PATCH** `/clientes/{rif}/rechazar`.  
   - Tras aprobar o rechazar, refrescar la lista (volver a llamar a `/clientes/solicitudes/pendientes`).
3. **Login de clientes:** Si la respuesta es **403**, leer `detail` y mostrar el mensaje correspondiente (pendiente de aprobación o rechazada) y no permitir acceso al resto de la app hasta que esté aprobado.

Referencia completa de la API: archivo **BACKEND-ESTADO-PARA-FRONTEND.md** en la raíz del backend.
