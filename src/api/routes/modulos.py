from fastapi import APIRouter, HTTPException, Depends
from pymongo.database import Database
from ..database import get_db
from bson import ObjectId

router = APIRouter(
    prefix="/modulos",
    tags=["modulos"]
)

@router.get("/", summary="Obtener todos los módulos")
def get_modulos(db: Database = Depends(get_db)):
    modulos_collection = db["modulos"]
    modulos = list(modulos_collection.find())
    for m in modulos:
        m["_id"] = str(m["_id"])
    return modulos

@router.get("/{modulo_id}", summary="Obtener un módulo por ID")
def get_modulo_by_id(modulo_id: str, db: Database = Depends(get_db)):
    modulos_collection = db["modulos"]
    modulo = modulos_collection.find_one({"_id": ObjectId(modulo_id)})
    if not modulo:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")
    modulo["_id"] = str(modulo["_id"])
    return modulo
