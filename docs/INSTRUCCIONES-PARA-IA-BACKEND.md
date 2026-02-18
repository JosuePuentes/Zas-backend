# Instrucciones para la IA del backend

Copia y pega este contexto cuando trabajes con la IA del backend.

---

## Contexto

El frontend **Virgen del Carmen** (Vite + React) está conectado al backend FastAPI en Render.

---

## Tareas para la IA del backend

1. **Mantener actualizado** el archivo `BACKEND-ESTADO-PARA-FRONTEND.md` en la raíz del backend. Es la referencia de rutas, métodos y cuerpos para el frontend.

2. **CORS:** Permitir peticiones desde:
   - El dominio del frontend en Vercel: `https://virgen-del-carmen-frontend.vercel.app`
   - Localhost en desarrollo: `http://localhost:3000` (y el puerto que use Vite si es otro)

3. **Rutas usadas por el frontend:**
   - `POST /login/` — Login cliente (puede devolver 403 si pendiente de aprobación o rechazado)
   - `POST /register/` — Registro cliente (queda estado_aprobacion: pendiente)
   - `POST /contacto` — Formulario de contacto
   - `POST /api/chat` — Chatbot
   - `GET /inventario_maestro/` — Catálogo
   - `GET /pedidos/por_cliente/{rif}` — Pedidos del cliente
   - `POST /reclamos/cliente` — Crear reclamo
   - `GET /reclamos/cliente/{rif}` — Listar reclamos
   - `GET /clientes/solicitudes/pendientes` — (Admin) Solicitudes de nuevos clientes
   - `PATCH /clientes/{rif}/aprobar` — (Admin) Aprobar cliente
   - `PATCH /clientes/{rif}/rechazar` — (Admin) Rechazar cliente

4. **Formato de respuestas:**
   - **Login cliente:** `{ "access_token": "...", "rif": "...", "role": "client" }` (y los demás campos que ya devuelve el backend)
   - **Login admin:** `{ "access_token": "...", "usuario": "...", "role": "admin", "rol": "...", "modulos": [] }` — incluir siempre **role: "admin"** para que el frontend sepa que es administrador.
   - **Errores:** usar `detail` (string o lista)
   - **IDs de MongoDB:** devolver `_id` como string

5. **Al añadir o cambiar rutas:** Actualizar `BACKEND-ESTADO-PARA-FRONTEND.md` y avisar si el frontend debe adaptarse.

---

## Referencia

- Documento completo de la API: **`BACKEND-ESTADO-PARA-FRONTEND.md`** (en la raíz del backend).
- En el repositorio del frontend también puede existir una copia de estas instrucciones en: `docs/INSTRUCCIONES-PARA-IA-BACKEND.md` (para que la IA del frontend sepa qué esperar del backend).
