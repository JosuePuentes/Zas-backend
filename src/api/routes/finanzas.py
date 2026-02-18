"""Dashboard finanzas: resumen, top productos, gráficas, gastos."""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from pymongo.database import Database
from ..database import get_db
from datetime import datetime
from collections import defaultdict

router = APIRouter()


@router.get("/finanzas/resumen")
async def resumen(db: Database = Depends(get_db)):
    pedidos = list(db["PEDIDOS"].find({"estado": {"$in": ["entregado", "enviado"]}, "total": {"$exists": True}}))
    valor_vendido = sum(float(p.get("total", 0)) for p in pedidos)
    productos_vendidos = 0
    costo_total = 0
    for p in pedidos:
        for prod in p.get("productos", []):
            qty = int(prod.get("cantidad_pedida") or prod.get("cantidad", 0))
            productos_vendidos += qty
            costo_total += float(prod.get("costo", 0) or 0) * qty
    utilidad = valor_vendido - costo_total
    return JSONResponse(content={
        "productos_vendidos": productos_vendidos,
        "valor_vendido": round(valor_vendido, 2),
        "utilidad": round(utilidad, 2),
    }, status_code=200)


@router.get("/finanzas/top-productos")
async def top_productos(tipo: str = Query("mas"), db: Database = Depends(get_db)):
    pedidos = list(db["PEDIDOS"].find({"estado": {"$in": ["entregado", "enviado"]}}))
    by_codigo = defaultdict(lambda: {"cantidad": 0, "descripcion": ""})
    for p in pedidos:
        for prod in p.get("productos", []):
            cod = prod.get("codigo", "")
            qty = int(prod.get("cantidad_pedida") or prod.get("cantidad", 0))
            by_codigo[cod]["cantidad"] += qty
            by_codigo[cod]["descripcion"] = prod.get("descripcion", "")
    items = [{"codigo": c, "descripcion": v["descripcion"], "cantidad": v["cantidad"]} for c, v in by_codigo.items()]
    items.sort(key=lambda x: x["cantidad"], reverse=(tipo == "mas"))
    return JSONResponse(content=items[:10], status_code=200)


@router.get("/finanzas/graficas")
async def graficas(db: Database = Depends(get_db)):
    pedidos = list(db["PEDIDOS"].find({"estado": {"$in": ["entregado", "enviado"]}, "total": {"$exists": True}}))
    by_mes = defaultdict(float)
    for p in pedidos:
        f = p.get("fecha_creacion") or p.get("fecha") or ""
        if isinstance(f, str):
            mes = f[:7] if len(f) >= 7 else ""
        else:
            mes = f.strftime("%Y-%m") if hasattr(f, "strftime") else ""
        if mes:
            by_mes[mes] += float(p.get("total", 0))
    out = [{"mes": m, "valor": round(v, 2)} for m, v in sorted(by_mes.items())]
    return JSONResponse(content=out, status_code=200)


@router.get("/finanzas/gastos")
async def gastos_total(db: Database = Depends(get_db)):
    col = db.get("GASTOS")
    if not col:
        return JSONResponse(content={"total": 0}, status_code=200)
    cursor = col.aggregate([{"$group": {"_id": None, "total": {"$sum": "$monto"}}}])
    r = next(cursor, None)
    total = float(r["total"]) if r else 0
    return JSONResponse(content={"total": round(total, 2)}, status_code=200)
