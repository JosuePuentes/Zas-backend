"""
Tasa BCV (Banco Central de Venezuela). Valores en USD; tasa para mostrar equivalente en Bs (Bs = $ × BCV).
GET /bcv/ — público, devuelve tasa actual.
PUT /bcv/ — admin (Bearer token), actualiza la tasa.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pymongo.database import Database
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..auth.auth_utils import verify_admin_token

router = APIRouter()
DOC_ID = "bcv_tasa"
DEFAULT_TASA = 36.50


class BCVTasaUpdate(BaseModel):
    tasa: Optional[float] = None
    rate: Optional[float] = None
    valor: Optional[float] = None


def get_admin_from_token(request: Request) -> dict:
    auth = request.headers.get("Authorization") or ""
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta token de administrador")
    token = auth[7:].strip()
    return verify_admin_token(token)


@router.get("/bcv/")
async def get_tasa(db: Database = Depends(get_db)):
    """Devuelve la tasa BCV actual. Público. Respuesta: { "tasa": number } (también aceptan rate/valor en frontend)."""
    col = db["CONFIG"]
    doc = col.find_one({"_id": DOC_ID})
    tasa = float(doc["tasa"]) if doc and "tasa" in doc else DEFAULT_TASA
    return JSONResponse(content={"tasa": round(tasa, 2)}, status_code=200)


@router.put("/bcv/")
async def put_tasa(
    body: BCVTasaUpdate,
    request: Request,
    db: Database = Depends(get_db),
):
    """Actualiza la tasa BCV. Requiere Authorization: Bearer <admin_token>. Respuesta: { "ok": true, "message": "Tasa BCV actualizada" }."""
    get_admin_from_token(request)
    tasa = body.tasa if body.tasa is not None else body.rate if body.rate is not None else body.valor
    if tasa is None or tasa <= 0:
        raise HTTPException(status_code=400, detail="tasa, rate o valor debe ser un número positivo")
    col = db["CONFIG"]
    col.update_one(
        {"_id": DOC_ID},
        {"$set": {"tasa": round(float(tasa), 2)}},
        upsert=True,
    )
    return JSONResponse(content={"ok": True, "message": "Tasa BCV actualizada"}, status_code=200)
