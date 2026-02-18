"""Compras: totalizar (sumar cantidades al inventario sin crear orden)."""
from fastapi import APIRouter, HTTPException, Depends
from pymongo.database import Database
from bson import ObjectId
from bson.errors import InvalidId
from ..database import get_db
from ..models.models import CompraTotalizar

router = APIRouter()


@router.post("/compras/totalizar")
async def totalizar(body: CompraTotalizar, db: Database = Depends(get_db)):
    """Suma cantidades al inventario por producto (proveedor_id opcional para registro)."""
    inv = db["INVENTARIO_MAESTRO"]
    for item in body.productos:
        codigo = item.get("codigo")
        cantidad = int(item.get("cantidad", 0))
        if not codigo or cantidad <= 0:
            continue
        inv.update_one(
            {"codigo": codigo},
            {"$inc": {"existencia": cantidad, "cantidad": cantidad}}
        )
    return {"message": "Inventario actualizado"}
