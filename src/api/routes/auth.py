from fastapi import APIRouter, HTTPException, Body, Depends
from pymongo.database import Database
from ..database import get_db
from ..auth.auth_utils import get_password_hash, verify_password, create_access_token, create_admin_access_token
from ..models.models import UserRegister, UserLogin, UserAdminRegister, AdminLogin, Client, UserAdmin

router = APIRouter()

@router.post("/register/")
async def register(client: Client, db: Database = Depends(get_db)):
    """Registro público: email y password son obligatorios."""
    if not client.email:
        raise HTTPException(status_code=400, detail="El correo es obligatorio")
    if not client.password:
        raise HTTPException(status_code=400, detail="La contraseña es obligatoria")
    clients_collection = db["CLIENTES"]
    if clients_collection.find_one({"email": client.email}):
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    hashed_password = get_password_hash(client.password)
    new_client = client.dict(exclude_none=True)
    new_client["password"] = hashed_password
    new_client["estado_aprobacion"] = "pendiente"  # Hasta que un admin apruebe
    result = clients_collection.insert_one(new_client)
    if result.inserted_id:
        return {"message": "Cliente registrado exitosamente. Su cuenta está pendiente de aprobación."}
    raise HTTPException(status_code=500, detail="Error al registrar el cliente")

@router.post("/login/")
async def login(user: UserLogin, db: Database = Depends(get_db)):
    clients_collection = db["CLIENTES"]
    db_client = clients_collection.find_one({"email": user.email})
    if not db_client:
        raise HTTPException(status_code=401, detail="Cliente no encontrado")
    if not verify_password(user.password, db_client["password"]):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    estado = db_client.get("estado_aprobacion", "aprobado")  # Clientes antiguos sin campo = aprobado
    if estado == "pendiente":
        raise HTTPException(status_code=403, detail="Pendiente de aprobación. Su solicitud está en revisión.")
    if estado == "rechazado":
        raise HTTPException(status_code=403, detail="Solicitud rechazada. Contacte al administrador.")
    # Usar el objeto completo para el token
    access_token = create_access_token(db_client)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": db_client.get("email", ""),
        "modules": [],
        "role": "client",
        "rif": db_client["rif"]
    }

@router.post("/register/admin/")
async def register_admin(user: UserAdminRegister, db: Database = Depends(get_db)):
    usuarios_admin_collection = db["usuarios_admin"]
    if usuarios_admin_collection.find_one({"usuario": user.usuario}):
        raise HTTPException(status_code=400, detail="Usuario ya registrado")
    hashed_password = get_password_hash(user.password)
    new_admin = user.dict()
    new_admin["password"] = hashed_password
    result = usuarios_admin_collection.insert_one(new_admin)
    if result.inserted_id:
        return {"message": "Usuario administrativo registrado exitosamente"}
    raise HTTPException(status_code=500, detail="Error al registrar el usuario administrativo")

@router.post("/login/admin/")
async def admin_login(admin: AdminLogin, db: Database = Depends(get_db)):
    usuarios_admin_collection = db["usuarios_admin"]
    db_admin = usuarios_admin_collection.find_one({"usuario": admin.usuario})
    if not db_admin:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not verify_password(admin.password, db_admin["password"]):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    access_token = create_admin_access_token(db_admin)
    modulos = db_admin.get("modulos", [])
    # Si el usuario tiene modulos: ["master"] o ["*"], devolverlo tal cual para que el frontend muestre todos los módulos
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": "admin",
        "rol": db_admin.get("rol", "admin"),
        "modulos": modulos,
        "usuario": db_admin["usuario"]
    }

@router.get("/usuarios/admin/")
async def listar_usuarios_admin(db: Database = Depends(get_db)):
    """Listar todos los usuarios admin. Cada item: _id, usuario, nombre, rol, modulos (sin password)."""
    usuarios_admin_collection = db["usuarios_admin"]
    usuarios = list(usuarios_admin_collection.find({}, {"password": 0}))
    for u in usuarios:
        u["_id"] = str(u["_id"])
    return usuarios

@router.patch("/usuarios/admin/{id}")
async def actualizar_usuario_admin(id: str, update: UserAdmin, db: Database = Depends(get_db)):
    """Actualizar permisos y datos del usuario admin por _id. Body: modulos, rol?, nombre?, telefono?, password?."""
    from bson import ObjectId
    from bson.errors import InvalidId
    try:
        oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")
    usuarios_admin_collection = db["usuarios_admin"]
    existing = usuarios_admin_collection.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Usuario administrativo no encontrado")
    update_data = update.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password"] = get_password_hash(update_data["password"])
    usuarios_admin_collection.update_one({"_id": oid}, {"$set": update_data})
    return {"message": "Usuario actualizado correctamente"}

@router.put("/admin/usuarios/{usuario}")
async def update_admin_user(usuario: str, update: UserAdmin, db: Database = Depends(get_db)):
    usuarios_admin_collection = db["usuarios_admin"]
    existing_user = usuarios_admin_collection.find_one({"usuario": usuario})
    if not existing_user:
        raise HTTPException(status_code=404, detail="Usuario administrativo no encontrado")
    update_data = update.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password"] = get_password_hash(update_data["password"])
    result = usuarios_admin_collection.update_one({"usuario": usuario}, {"$set": update_data})
    if result.modified_count:
        return {"message": "Usuario administrativo actualizado correctamente"}
    return {"message": "No se realizaron cambios"}

