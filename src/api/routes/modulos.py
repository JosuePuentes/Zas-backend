from fastapi import APIRouter, HTTPException
from ..database import modulos_collection
from bson import ObjectId

router = APIRouter(
    prefix="/modulos",
    tags=["modulos"]
)

@router.get("/", summary="Obtener todos los módulos")
def get_modulos():
    modulos = list(modulos_collection.find())
    for m in modulos:
        m["_id"] = str(m["_id"])
    return modulos

@router.get("/{modulo_id}", summary="Obtener un módulo por ID")
def get_modulo_by_id(modulo_id: str):
    modulo = modulos_collection.find_one({"_id": ObjectId(modulo_id)})
    if not modulo:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
    modulo["_id"] = str(modulo["_id"])
    return modulo
