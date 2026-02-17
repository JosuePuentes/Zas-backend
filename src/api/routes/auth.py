from fastapi import APIRouter, HTTPException, Body, Depends
from pymongo.database import Database
from ..database import get_db
from ..auth.auth_utils import get_password_hash, verify_password, create_access_token, create_admin_access_token
from ..models.models import UserRegister, UserLogin, UserAdminRegister, AdminLogin, Client, UserAdmin

router = APIRouter()

@router.post("/register/")
async def register(client: Client, db: Database = Depends(get_db)):
    clients_collection = db["CLIENTES"]
    if clients_collection.find_one({"email": client.email}):
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    hashed_password = get_password_hash(client.password)
    new_client = client.dict()
    new_client["password"] = hashed_password
    result = clients_collection.insert_one(new_client)
    if result.inserted_id:
        return {"message": "Cliente registrado exitosamente"}
    raise HTTPException(status_code=500, detail="Error al registrar el cliente")

@router.post("/login/")
async def login(user: UserLogin, db: Database = Depends(get_db)):
    clients_collection = db["CLIENTES"]
    db_client = clients_collection.find_one({"email": user.email})
    if not db_client:
        raise HTTPException(status_code=401, detail="Cliente no encontrado")
    if not verify_password(user.password, db_client["password"]):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
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
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "modulos": db_admin["modulos"],
        "usuario": db_admin["usuario"]
    }

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

