# Instrucciones para el frontend: Módulo "Mi cuenta" / "Datos del cliente" (área cliente)

Cuando el usuario inicia sesión como **cliente** (`POST /login/` → `role: "client"`), debe tener acceso a un módulo donde ver y editar **sus propios datos** (empresa, encargado, dirección, teléfono, email, etc.). Este módulo no depende de `modulos` (esa lista solo existe en el login **admin**).

---

## 1. Dónde mostrar el módulo

- **Área cliente:** Tras login con `role === "client"`, el menú/lateral debe incluir **siempre** una entrada para los datos del cliente, por ejemplo:
  - **"Mi cuenta"**, o
  - **"Datos del cliente"**, o
  - **"Perfil"**, o
  - **"Clientes"** (referido a “mis datos como cliente”).

- No usar el array `modulos` para decidir si mostrar esta entrada: `modulos` solo viene en la respuesta de `POST /login/admin/`. En el login cliente la respuesta no incluye `modulos`, por tanto el frontend debe definir de forma fija las secciones del área cliente (p. ej. Catálogo, Pedidos, Reclamos, **Mi cuenta**).

---

## 2. Datos disponibles tras el login cliente

Tras **POST /login/** con éxito, la respuesta incluye:

```json
{
  "access_token": "string",
  "token_type": "bearer",
  "username": "email",
  "role": "client",
  "rif": "string"
}
```

- Guardar **`rif`** en estado global (Vue/React context, store, sessionStorage, etc.) para usarlo en todas las llamadas que requieran el RIF del cliente.
- Enviar **`Authorization: Bearer <access_token>`** en las peticiones al backend cuando corresponda.

---

## 3. Endpoints a usar en "Mi cuenta" / "Datos del cliente"

| Acción | Método | Ruta | Notas |
|--------|--------|------|--------|
| Ver mis datos | GET | `/clientes/{rif}` | Sustituir `{rif}` por el `rif` guardado del login. |
| Actualizar mis datos | PATCH | `/clientes/{rif}` | Body parcial con los campos que el cliente pueda editar (ver más abajo). |

### GET `/clientes/{rif}`

- **Path:** `rif` = valor de `rif` del usuario logueado (cliente).
- **Respuesta 200:** Objeto con `_id`, `email`, `rif`, `empresa`, `encargado`, `direccion`, `telefono`, `activo`, `descuento1`, `descuento2`, `descuento3`, `limite_credito`, `limite_consumido`, `dias_credito`, `facturas_vencidas`.
- Usar esta respuesta para rellenar el formulario de "Mi cuenta".

### PATCH `/clientes/{rif}`

- **Path:** mismo `rif` del cliente logueado.
- **Body (todos opcionales):** solo enviar los campos que el usuario puede modificar, por ejemplo:
  - `encargado`
  - `direccion`
  - `telefono`
  - `email`
  - `password` (si se implementa cambio de contraseña)
- **Ejemplo:**  
  `PATCH /clientes/J-12345678-9` con body  
  `{ "encargado": "Juan Pérez", "telefono": "04141234567" }`
- El backend actualiza solo los campos enviados. El cliente **solo** debe poder enviar su propio `rif` (el que tiene en sesión), nunca el de otro cliente.

---

## 4. Resumen para el frontend

1. **Tras login cliente** (`role === "client"`): guardar `access_token` y **`rif`**.
2. **Menú del área cliente:** Incluir siempre una opción tipo **"Mi cuenta"** o **"Datos del cliente"** (sin depender de `modulos`).
3. **Pantalla "Mi cuenta":**
   - Al entrar, llamar a **GET** `/clientes/{rif}` usando el `rif` de la sesión.
   - Mostrar formulario con los datos (empresa, encargado, dirección, teléfono, email, etc.). Decidir qué campos son solo lectura (p. ej. `rif`, `empresa`, descuentos) y cuáles editables (encargado, dirección, teléfono, email, contraseña).
   - Al guardar, enviar **PATCH** `/clientes/{rif}` con el body parcial de los campos editados.
4. En las peticiones GET y PATCH enviar el header **`Authorization: Bearer <access_token>`** si el backend lo requiere.

Con esto, el cliente tendrá acceso al módulo de sus propios datos desde el área cliente.
