# Cuentas por cobrar
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.database import Database
from ..database import get_db
from datetime import datetime, timedelta

router = APIRouter()

def _get_facturas_cobrar(db: Database):
    pedidos = list(db["PEDIDOS"].find({"estado": {"$in": ["entregado", "facturando", "enviado"]}, "total": {"$exists": True}}))
    facturas = []
    for p in pedidos:
        rif = p.get("rif", "")
        cli = db["CLIENTES"].find_one({"rif": rif}) or {}
        dias_credito = int(cli.get("dias_credito", 0))
        fp = p.get("fecha_creacion") or p.get("fecha") or datetime.now()
        if isinstance(fp, str):
            try: fp = datetime.strptime(fp[:10], "%Y-%m-%d")
            except: fp = datetime.now()
        fv = fp + timedelta(days=dias_credito) if dias_credito else fp
        facturas.append({
            "numero": p.get("numero_factura") or str(p.get("_id", "")),
            "cliente": p.get("cliente", ""), "rif": rif, "total": float(p.get("total", 0)),
            "fecha_emision": fp.strftime("%Y-%m-%d") if hasattr(fp, "strftime") else str(fp)[:10],
            "fecha_vencimiento": fv.strftime("%Y-%m-%d") if hasattr(fv, "strftime") else str(fv)[:10],
            "fecha_pago": p.get("fecha_pago"),
        })
    return facturas

@router.get("/cuentas-por-cobrar/vigentes")
async def vigentes(db: Database = Depends(get_db)):
    hoy = datetime.now().date()
    out = []
    for f in _get_facturas_cobrar(db):
        if f.get("fecha_pago"): continue
        try: fv_dt = datetime.strptime(f["fecha_vencimiento"][:10], "%Y-%m-%d").date()
        except: continue
        if fv_dt >= hoy:
            out.append({**f, "dias_restantes": (fv_dt - hoy).days})
    return JSONResponse(content=out, status_code=200)

@router.get("/cuentas-por-cobrar/vencidas")
async def vencidas(db: Database = Depends(get_db)):
    hoy = datetime.now().date()
    out = []
    for f in _get_facturas_cobrar(db):
        if f.get("fecha_pago"): continue
        try: fv_dt = datetime.strptime(f["fecha_vencimiento"][:10], "%Y-%m-%d").date()
        except: continue
        if fv_dt < hoy:
            out.append({**f, "dias_vencidos": (hoy - fv_dt).days})
    return JSONResponse(content=out, status_code=200)

@router.get("/cuentas-por-cobrar/total")
async def total(db: Database = Depends(get_db)):
    t = sum(f["total"] for f in _get_facturas_cobrar(db) if not f.get("fecha_pago"))
    return JSONResponse(content={"total": round(t, 2)}, status_code=200)


@router.get("/cuentas-por-cobrar/cliente/{rif}")
async def cuentas_por_cobrar_cliente(rif: str, db: Database = Depends(get_db)):
    """Facturas pendientes de pago del cliente (área cliente). Authorization: Bearer <token_cliente> recomendado."""
    hoy = datetime.now().date()
    out = []
    for f in _get_facturas_cobrar(db):
        if f.get("rif") != rif or f.get("fecha_pago"):
            continue
        try:
            fv_dt = datetime.strptime(f["fecha_vencimiento"][:10], "%Y-%m-%d").date()
            dias_restantes = (fv_dt - hoy).days
            f["dias_restantes"] = dias_restantes
            if fv_dt < hoy:
                f["dias_vencidos"] = (hoy - fv_dt).days
        except Exception:
            pass
        out.append(f)
    return JSONResponse(content=out, status_code=200)
