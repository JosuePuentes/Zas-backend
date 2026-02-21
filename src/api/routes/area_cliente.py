"""
Endpoints opcionales del área cliente: promociones, precios reducidos, planificación de compra.
Documento: docs/BACKEND-AREA-CLIENTE.md
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.database import Database
from ..database import get_db

router = APIRouter()


@router.get("/promociones/")
async def promociones_vigentes(db: Database = Depends(get_db)):
    """Promociones vigentes. Opcional: filtrar por cliente. Por ahora devuelve lista vacía."""
    return JSONResponse(content=[], status_code=200)


@router.get("/promociones/cliente/{rif}")
async def promociones_cliente(rif: str, db: Database = Depends(get_db)):
    """Promociones vigentes para el cliente. Authorization: Bearer <token_cliente> recomendado."""
    return JSONResponse(content=[], status_code=200)


@router.get("/precios-bajaron/cliente/{rif}")
async def precios_bajaron_cliente(rif: str, db: Database = Depends(get_db)):
    """Productos con precio reducido para mostrar al cliente. Por ahora lista vacía."""
    return JSONResponse(content=[], status_code=200)


@router.get("/planificacion-compra/cliente/{rif}")
async def planificacion_compra_cliente(rif: str, db: Database = Depends(get_db)):
    """Sugerencias de compra para el cliente. Por ahora lista vacía."""
    return JSONResponse(content=[], status_code=200)
