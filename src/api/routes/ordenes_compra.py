"""Órdenes de compra: CRUD y totalizar (sumar al inventario)."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pymongo.database import Database
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from ..database import get_db
from ..models.models import OrdenCompraCreate

router = APIRouter()
COL = "ORDENES_COMPRA"


def _serialize(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("/ordenes-compra/")
async def listar(db: Database = Depends(get_db)):
    col = db[COL]
    proveedores = db["PROVEEDORES"]
    items = list(col.find({}).sort("fecha", -1))
    for o in items:
        o["_id"] = str(o["_id"])
        prov = proveedores.find_one({"_id": ObjectId(o.get("proveedor_id", ""))}) if o.get("proveedor_id") else None
        if not prov and o.get("proveedor_id"):
            try:
                prov = proveedores.find_one({"_id": ObjectId(o["proveedor_id"])})
            except Exception:
                pass
        if prov:
            o["proveedor_empresa"] = prov.get("empresa")
            o["proveedor_rif"] = prov.get("rif")
    return items


@router.post("/ordenes-compra/")
async def crear(body: OrdenCompraCreate, db: Database = Depends(get_db)):
    col = db[COL]
    proveedores = db["PROVEEDORES"]
    try:
        prov = proveedores.find_one({"_id": ObjectId(body.proveedor_id)})
    except Exception:
        prov = proveedores.find_one({"rif": body.proveedor_rif}) if body.proveedor_rif else None
    doc = {
        "proveedor_id": body.proveedor_id,
        "proveedor_rif": body.proveedor_rif or (prov.get("rif") if prov else None),
        "proveedor_empresa": prov.get("empresa") if prov else None,
        "productos": [p.dict() for p in body.productos],
        "total": body.total,
        "totalizada": False,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    r = col.insert_one(doc)
    doc["_id"] = str(r.inserted_id)
    return JSONResponse(content=doc, status_code=201)


@router.get("/ordenes-compra/{id}")
async def detalle(id: str, db: Database = Depends(get_db)):
    try:
        oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")
    col = db[COL]
    doc = col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return _serialize(doc)


@router.put("/ordenes-compra/{id}")
async def actualizar(id: str, body: OrdenCompraCreate, db: Database = Depends(get_db)):
    try:
        oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")
    col = db[COL]
    doc = col.find_one({"_id": oid})
    if not doc or doc.get("totalizada"):
        raise HTTPException(status_code=404, detail="Orden no encontrada o ya totalizada")
    col.update_one(
        {"_id": oid},
        {"$set": {"productos": [p.dict() for p in body.productos], "total": body.total}}
    )
    return {"message": "Orden actualizada"}


@router.post("/ordenes-compra/{id}/totalizar")
async def totalizar(id: str, db: Database = Depends(get_db)):
    try:
        oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")
    col = db[COL]
    doc = col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if doc.get("totalizada"):
        return {"message": "Orden ya estaba totalizada"}
    inv = db["INVENTARIO_MAESTRO"]
    for p in doc.get("productos", []):
        codigo = p.get("codigo")
        cantidad = int(p.get("cantidad", 0))
        if codigo and cantidad > 0:
            inv.update_one({"codigo": codigo}, {"$inc": {"existencia": cantidad, "cantidad": cantidad}})
    col.update_one({"_id": oid}, {"$set": {"totalizada": True}})
    return {"message": "Orden totalizada e inventario actualizado"}
