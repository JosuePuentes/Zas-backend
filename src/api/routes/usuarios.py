from fastapi import APIRouter, HTTPException
from ..database import clients_collection
from ..auth.auth_utils import get_password_hash
from ..models.models import Client

router = APIRouter()

@router.put("/clientes/{email}")
async def update_client(email: str, update: Client):
    existing_client = clients_collection.find_one({"email": email})
    if not existing_client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    update_data = update.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password"] = get_password_hash(update_data["password"])
    result = clients_collection.update_one({"email": email}, {"$set": update_data})
    if result.modified_count:
        return {"message": "Cliente actualizado correctamente"}
    return {"message": "No se realizaron cambios"}
