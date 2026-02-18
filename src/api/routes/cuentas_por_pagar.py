"""
Cuentas por pagar: obligaciones con proveedores.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.database import Database
from ..database import get_db

router = APIRouter()


def _get_obligaciones(db: Database):
    if "CUENTAS_POR_PAGAR" in db.list_collection_names():
        col = db["CUENTAS_POR_PAGAR"]
        items = list(col.find({"pagado": {"$ne": True}}))
        items = list(col.find({"pagado": {"$ne": True}}))
        return [{"_id": str(x["_id"]), "proveedor_empresa": x.get("proveedor_empresa"), "proveedor_rif": x.get("proveedor_rif"),
                 "concepto": x.get("concepto"), "monto": float(x.get("monto", 0)), "fecha_vencimiento": x.get("fecha_vencimiento"),
                 "dias_credito": x.get("dias_credito")} for x in items]
    if "ORDENES_COMPRA" not in db.list_collection_names():
        return []
    col_oc = db["ORDENES_COMPRA"]
    if not col_oc:
        return []
    ordenes = list(col_oc.find({"totalizada": True, "pagado": {"$ne": True}}))
    return [{"_id": str(o["_id"]), "proveedor_empresa": o.get("proveedor_empresa"), "proveedor_rif": o.get("proveedor_rif"),
             "concepto": "Orden de compra", "monto": float(o.get("total", 0)), "fecha_vencimiento": o.get("fecha_vencimiento"),
             "dias_credito": o.get("dias_credito")} for o in ordenes]


@router.get("/cuentas-por-pagar/")
async def listar(db: Database = Depends(get_db)):
    items = _get_obligaciones(db)
    return JSONResponse(content=items, status_code=200)


@router.get("/cuentas-por-pagar/total")
async def total(db: Database = Depends(get_db)):
    items = _get_obligaciones(db)
    total_pagar = sum(x.get("monto", 0) for x in items)
    return JSONResponse(content={"total": round(total_pagar, 2)}, status_code=200)
