from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from pymongo.database import Database
from typing import List, Optional
from ..models.models import KardexMovimiento, TipoMovimiento, ProductoInventario
from ..database import get_db
import datetime

class AnularTransaccionRequest(BaseModel):
    movimiento_id: str
    usuario: str

router = APIRouter()

class ProductoTransaccion(BaseModel):
    producto_codigo: str
    cantidad: int

class TransaccionRequest(BaseModel):
    tipo_movimiento: TipoMovimiento
    usuario: str
    observaciones: Optional[str] = None
    documento_origen: Optional[dict] | Optional[str] = None
    productos: List[ProductoTransaccion]

@router.post("/transaccion")
def registrar_transaccion(request: TransaccionRequest, db: Database = Depends(get_db)):
    movimiento_doc = {
        "fecha": datetime.datetime.now().isoformat(),
        "usuario": request.usuario,
        "tipo": request.tipo_movimiento,
        "observaciones": request.observaciones,
        "documento_origen": request.documento_origen,
        "productos": [p.producto_codigo for p in request.productos]
    }
    # Validar existencia de todos los productos
    productos_no_encontrados = []
    for prod in request.productos:
        # <-- CORRECCIÓN: Búsqueda directa por el campo 'codigo'
        producto = db["INVENTARIO_MAESTRO"].find_one({"codigo": prod.producto_codigo})
        if not producto:
            productos_no_encontrados.append({"codigo": prod.producto_codigo, "error": "Producto no encontrado"})
    
    if productos_no_encontrados:
        return {"error": "Uno o más productos no existen. Transacción cancelada.", "detalles": productos_no_encontrados}

    movimiento_id = db["MOVIMIENTOS"].insert_one(movimiento_doc).inserted_id
    resultados = []
    for prod in request.productos:
        # <-- CORRECCIÓN: Búsqueda directa, ya no se necesita el bucle 'next()'
        producto = db["INVENTARIO_MAESTRO"].find_one({"codigo": prod.producto_codigo})
        
        saldo_previo = producto["existencia"]
        
        if request.tipo_movimiento == "descargo":
            saldo_posterior = saldo_previo - prod.cantidad
        if request.tipo_movimiento == "pedido":
            saldo_posterior = saldo_previo - prod.cantidad
        elif request.tipo_movimiento == "cargo":
            saldo_posterior = saldo_previo + prod.cantidad
        elif request.tipo_movimiento == "apartado":
            saldo_posterior = saldo_previo - prod.cantidad
        elif request.tipo_movimiento == "ajuste":
            saldo_posterior = prod.cantidad
        else:
            saldo_posterior = saldo_previo

        # <-- CORRECCIÓN: Actualización directa del campo 'existencia'
        db["INVENTARIO_MAESTRO"].update_one(
            {"codigo": prod.producto_codigo},
            {"$set": {"existencia": saldo_posterior}}
        )
        
        kardex_data = {
            "fecha": datetime.datetime.now().isoformat(),
            "usuario": request.usuario,
            "tipo_movimiento": request.tipo_movimiento,
            "producto": producto,
            "cantidad": prod.cantidad,
            "precio": producto.get("precio", 0),
            "saldo_previo": saldo_previo,
            "saldo_posterior": saldo_posterior,
            "movimiento_id": str(movimiento_id),
            "estado": "activo"
        }
        db["KARDEX"].insert_one(kardex_data)
        resultados.append({"codigo": prod.producto_codigo, "msg": "Transacción registrada", "saldo_previo": saldo_previo, "saldo_posterior": saldo_posterior, "movimiento_id": str(movimiento_id)})
    
    return {"resultados": resultados, "movimiento_id": str(movimiento_id)}


@router.post("/anular-transaccion")
def anular_transaccion(request: AnularTransaccionRequest, db: Database = Depends(get_db)):
    kardex_movimientos = list(db["KARDEX"].find({"movimiento_id": request.movimiento_id, "estado": "activo"}))
    if not kardex_movimientos:
        raise HTTPException(status_code=404, detail="No se encontraron movimientos activos para el ID proporcionado.")

    productos_afectados = []
    for kardex in kardex_movimientos:
        producto_codigo = kardex["producto"]["codigo"]
        cantidad = kardex["cantidad"]
        tipo_movimiento = kardex["tipo_movimiento"]
        
        producto = db["INVENTARIO_MAESTRO"].find_one({"codigo": producto_codigo})
        if not producto:
            continue 

        # Revertir el movimiento
        nueva_existencia = producto["existencia"]
        if tipo_movimiento == "DESCARGO" or tipo_movimiento == "APARTADO":
            nueva_existencia += cantidad
        elif tipo_movimiento == "CARGO":
            nueva_existencia -= cantidad
        
        db["INVENTARIO_MAESTRO"].update_one(
            {"codigo": producto_codigo},
            {"$set": {"existencia": nueva_existencia}}
        )

        db["KARDEX"].update_one({"_id": kardex["_id"]}, {"$set": {"estado": "anulado", "usuario_anulacion": request.usuario, "fecha_anulacion": datetime.datetime.now().isoformat()}})
        productos_afectados.append({"producto_codigo": producto_codigo, "cantidad": cantidad, "tipo_movimiento": tipo_movimiento})

    db["MOVIMIENTOS"].update_one({"_id": db["MOVIMIENTOS"].find_one({"_id": request.movimiento_id})["_id"]}, {"$set": {"estado": "anulado", "usuario_anulacion": request.usuario, "fecha_anulacion": datetime.datetime.now().isoformat()}})
    
    movimiento_anulacion = {
        "fecha": datetime.datetime.now().isoformat(),
        "usuario": request.usuario,
        "tipo": "ANULACION",
        "observaciones": f"Anulación de movimiento {request.movimiento_id}",
        "productos": [p["producto_codigo"] for p in productos_afectados],
        "movimiento_anulado": request.movimiento_id,
        "productos_detalle": productos_afectados
    }
    movimiento_anulacion_id = db["MOVIMIENTOS"].insert_one(movimiento_anulacion).inserted_id
    
    return {"msg": "Transacción anulada y ajustes realizados.", "movimiento_id": request.movimiento_id, "anulacion_id": str(movimiento_anulacion_id)}