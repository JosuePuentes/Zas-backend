"""Cierre diario: resumen por fecha o rango."""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from pymongo.database import Database
from ..database import get_db
from datetime import datetime, time

router = APIRouter()


def _parse_fecha(s: str):
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except Exception:
        return None


@router.get("/cierre-diario/")
async def cierre(
    fecha: str = Query(None),
    desde: str = Query(None),
    hasta: str = Query(None),
    db: Database = Depends(get_db),
):
    """fecha=YYYY-MM-DD para un día; o desde y hasta para rango."""
    pedidos_collection = db["PEDIDOS"]
    gastos_collection = db["GASTOS"] if "GASTOS" in db.list_collection_names() else None
    if fecha:
        f = _parse_fecha(fecha)
        if not f:
            return JSONResponse(content={"error": "fecha inválida"}, status_code=400)
        start = datetime.combine(f, datetime.min.time())
        end = datetime.combine(f, time(23, 59, 59))
        q = {"fecha_creacion": {"$gte": start.isoformat()[:19], "$lte": end.isoformat()[:19]}}
        q_alt = {"fecha": {"$gte": fecha, "$lte": fecha}}
    elif desde and hasta:
        q = {"fecha_creacion": {"$gte": desde[:10], "$lte": hasta[:10]}}
        q_alt = {"fecha": {"$gte": desde[:10], "$lte": hasta[:10]}}
    else:
        hoy = datetime.now().strftime("%Y-%m-%d")
        q = {"fecha_creacion": {"$gte": hoy, "$lte": hoy}}
        q_alt = {"fecha": {"$gte": hoy, "$lte": hoy}}
    pedidos = list(pedidos_collection.find({"estado": {"$in": ["entregado", "enviado"]}}))
    pedidos = [p for p in pedidos if (p.get("fecha_creacion") or p.get("fecha") or "")[:10] >= (desde or fecha or "")[:10] and (p.get("fecha_creacion") or p.get("fecha") or "")[:10] <= (hasta or fecha or "")[:10]]
    monto_total = sum(float(p.get("total", 0)) for p in pedidos)
    clientes_unicos = len(set(p.get("rif", "") for p in pedidos))
    productos_vendidos = sum(int(prod.get("cantidad_pedida") or prod.get("cantidad", 0)) for p in pedidos for prod in p.get("productos", []))
    costo = sum(float(prod.get("costo", 0) or 0) * int(prod.get("cantidad_pedida") or prod.get("cantidad", 0)) for p in pedidos for prod in p.get("productos", []))
    utilidad = monto_total - costo
    gastos_dia = 0
    if gastos_collection:
        if fecha:
            g = list(gastos_collection.find({"fecha": fecha[:10]}))
        elif desde and hasta:
            g = list(gastos_collection.find({"fecha": {"$gte": desde[:10], "$lte": hasta[:10]}}))
        else:
            g = list(gastos_collection.find({"fecha": datetime.now().strftime("%Y-%m-%d")}))
        gastos_dia = sum(float(x.get("monto", 0)) for x in g)
    return JSONResponse(content={
        "productos_vendidos": productos_vendidos,
        "cantidad_clientes": clientes_unicos,
        "monto_total": round(monto_total, 2),
        "gastos": round(gastos_dia, 2),
        "utilidad": round(utilidad - gastos_dia, 2),
    }, status_code=200)
