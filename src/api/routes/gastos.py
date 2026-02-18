"""Gastos: POST, GET con filtro fecha, DELETE."""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pymongo.database import Database
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from ..database import get_db
from ..models.models import GastoCreate

router = APIRouter()
COL = "GASTOS"


@router.post("/gastos/")
async def crear(body: GastoCreate, db: Database = Depends(get_db)):
    col = db[COL]
    doc = body.dict()
    doc["fecha"] = doc.get("fecha") or datetime.now().strftime("%Y-%m-%d")
    r = col.insert_one(doc)
    doc["_id"] = str(r.inserted_id)
    return JSONResponse(content={"message": "Gasto registrado", "gasto": doc}, status_code=201)


@router.get("/gastos/")
async def listar(desde: str = Query(None), hasta: str = Query(None), db: Database = Depends(get_db)):
    col = db[COL]
    q = {}
    if desde:
        q["fecha"] = {"$gte": desde[:10]}
    if hasta:
        q.setdefault("fecha", {})["$lte"] = hasta[:10]
    items = list(col.find(q))
    for x in items:
        x["_id"] = str(x["_id"])
    return items


@router.delete("/gastos/{id}")
async def eliminar(id: str, db: Database = Depends(get_db)):
    try:
        oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")
    col = db[COL]
    result = col.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return {"message": "Gasto eliminado"}
