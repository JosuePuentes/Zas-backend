"""
Facturas finalizadas: top clientes, clientes poco frecuentes, facturas pagadas.
Se derivan de pedidos (entregados/facturados) y clientes.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.database import Database
from ..database import get_db
from datetime import datetime, timedelta
from collections import defaultdict

router = APIRouter()


@router.get("/facturas/top-clientes")
async def top_clientes(db: Database = Depends(get_db)):
    """Top 10 mejores clientes por total y cantidad de pedidos."""
    pedidos_collection = db["PEDIDOS"]
    pedidos = list(pedidos_collection.find({"estado": {"$in": ["entregado", "enviado"]}, "total": {"$exists": True}}))
    by_rif = defaultdict(lambda: {"total": 0, "cantidad_pedidos": 0, "cliente": ""})
    for p in pedidos:
        rif = p.get("rif", "")
        by_rif[rif]["total"] += float(p.get("total", 0))
        by_rif[rif]["cantidad_pedidos"] += 1
        by_rif[rif]["cliente"] = p.get("cliente", "")
    items = [{"cliente": v["cliente"], "rif": rif, "total": round(v["total"], 2), "cantidad_pedidos": v["cantidad_pedidos"]}
             for rif, v in by_rif.items()]
    items.sort(key=lambda x: x["total"], reverse=True)
    return JSONResponse(content=items[:10], status_code=200)


@router.get("/facturas/clientes-poco-frecuentes")
async def clientes_poco_frecuentes(db: Database = Depends(get_db)):
    """Clientes que no compran frecuentemente: último pedido y días sin comprar."""
    pedidos_collection = db["PEDIDOS"]
    clients_collection = db["CLIENTES"]
    pedidos = list(pedidos_collection.find({"estado": "entregado"}, {"rif": 1, "cliente": 1, "fecha_creacion": 1, "fecha": 1}))
    # Último pedido por RIF
    ultimo_por_rif = {}
    for p in pedidos:
        rif = p.get("rif", "")
        f = p.get("fecha_creacion") or p.get("fecha")
        if isinstance(f, str):
            f = f[:10]
        if rif not in ultimo_por_rif or (f and str(f) > str(ultimo_por_rif[rif].get("fecha", ""))):
            ultimo_por_rif[rif] = {"cliente": p.get("cliente"), "rif": rif, "ultimo_pedido": str(f)[:10] if f else None}
    hoy = datetime.now().date()
    items = []
    for rif, v in ultimo_por_rif.items():
        u = v.get("ultimo_pedido") or ""
        try:
            fecha_ult = datetime.strptime(u[:10], "%Y-%m-%d").date()
            dias_sin_comprar = (hoy - fecha_ult).days
        except Exception:
            dias_sin_comprar = 999
        items.append({
            "cliente": v["cliente"],
            "rif": rif,
            "ultimo_pedido": u,
            "dias_sin_comprar": dias_sin_comprar,
        })
    items.sort(key=lambda x: x["dias_sin_comprar"], reverse=True)
    return JSONResponse(content=items[:50], status_code=200)


@router.get("/facturas/pagadas")
async def facturas_pagadas(db: Database = Depends(get_db)):
    """Facturas ya pagadas (pedidos con fecha_pago)."""
    pedidos_collection = db["PEDIDOS"]
    pedidos = list(pedidos_collection.find({"fecha_pago": {"$exists": True, "$ne": None}}))
    items = []
    for p in pedidos:
        items.append({
            "numero": p.get("numero_factura") or str(p.get("_id", "")),
            "cliente": p.get("cliente", ""),
            "rif": p.get("rif", ""),
            "monto": float(p.get("total", 0)),
            "total": float(p.get("total", 0)),
            "fecha_pago": p.get("fecha_pago"),
        })
    return JSONResponse(content=items, status_code=200)
