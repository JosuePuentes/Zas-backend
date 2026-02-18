"""Proveedores: CRUD."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pymongo.database import Database
from bson import ObjectId
from bson.errors import InvalidId
from ..database import get_db
from ..models.models import Proveedor

router = APIRouter()
COL = "PROVEEDORES"


@router.get("/proveedores/")
async def listar(db: Database = Depends(get_db)):
    col = db[COL]
    items = list(col.find({}))
    for x in items:
        x["_id"] = str(x["_id"])
    return items


@router.post("/proveedores/")
async def crear(body: Proveedor, db: Database = Depends(get_db)):
    col = db[COL]
    if col.find_one({"rif": body.rif}):
        raise HTTPException(status_code=400, detail="RIF ya registrado")
    doc = body.dict()
    r = col.insert_one(doc)
    doc["_id"] = str(r.inserted_id)
    return JSONResponse(content={"message": "Proveedor creado", "proveedor": doc}, status_code=201)


@router.put("/proveedores/{id}")
async def actualizar(id: str, body: Proveedor, db: Database = Depends(get_db)):
    try:
        oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")
    col = db[COL]
    result = col.update_one({"_id": oid}, {"$set": body.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return {"message": "Proveedor actualizado"}


@router.delete("/proveedores/{id}")
async def eliminar(id: str, db: Database = Depends(get_db)):
    try:
        oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")
    col = db[COL]
    result = col.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return {"message": "Proveedor eliminado"}
