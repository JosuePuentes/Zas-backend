"""
Rutas para punto de venta
Incluye endpoint para registrar ventas con descuento automático de inventario
"""
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId
from pymongo.errors import OperationFailure
import traceback

from ..database import db, ventas_collection, client as mongo_client
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from utils.inventario_utils import (
    validar_stock_suficiente,
    calcular_nuevo_stock
)

router = APIRouter()


class ProductoVenta(BaseModel):
    codigo: str
    descripcion: Optional[str] = None
    cantidad: int
    precio_unitario: float
    descuento: Optional[float] = 0.0
    subtotal: Optional[float] = None


class VentaRequest(BaseModel):
    usuario: str
    cliente_rif: Optional[str] = None
    cliente_nombre: Optional[str] = None
    productos: List[ProductoVenta]
    total: float
    metodo_pago: Optional[str] = "efectivo"
    observaciones: Optional[str] = None


@router.post("/punto-venta/ventas")
async def registrar_venta(venta: VentaRequest):
    """
    Endpoint para registrar una venta y descontar automáticamente el inventario.
    
    Características:
    - Valida stock antes de procesar la venta
    - Usa transacciones para garantizar atomicidad
    - No permite stock negativo
    - Registra movimientos en KARDEX
    - Maneja errores y rollback en caso de fallo
    
    Args:
        venta: Datos de la venta incluyendo productos
        
    Returns:
        Información de la venta registrada y productos procesados
    """
    try:
        # Validar que hay productos
        if not venta.productos or len(venta.productos) == 0:
            raise HTTPException(status_code=400, detail="La venta debe incluir al menos un producto")
        
        # PASO 1: Validar stock de todos los productos ANTES de procesar
        productos_validacion = []
        productos_no_validos = []
        
        for producto_venta in venta.productos:
            codigo = producto_venta.codigo
            
            # Buscar producto en inventario
            producto_inventario = db["INVENTARIO_MAESTRO"].find_one({"codigo": str(codigo)})
            
            if not producto_inventario:
                productos_no_validos.append({
                    "codigo": codigo,
                    "error": "Producto no encontrado en inventario"
                })
                continue
            
            existencia_actual = producto_inventario.get("existencia", 0)
            cantidad_solicitada = producto_venta.cantidad
            
            # Validar stock suficiente
            es_valido, mensaje_error = validar_stock_suficiente(
                existencia_actual,
                cantidad_solicitada
            )
            
            if not es_valido:
                productos_no_validos.append({
                    "codigo": codigo,
                    "descripcion": producto_inventario.get("descripcion", ""),
                    "error": mensaje_error,
                    "existencia_actual": existencia_actual,
                    "cantidad_solicitada": cantidad_solicitada
                })
            else:
                productos_validacion.append({
                    "producto": producto_inventario,
                    "producto_venta": producto_venta,
                    "existencia_previo": existencia_actual
                })
        
        # Si hay productos sin stock suficiente, rechazar toda la venta
        if productos_no_validos:
            raise HTTPException(
                status_code=400,
                detail="No se puede procesar la venta debido a stock insuficiente",
                extra={
                    "productos_con_error": productos_no_validos
                }
            )
        
        # PASO 2: Procesar la venta usando transacciones de MongoDB
        # Iniciar sesión para transacción
        session = mongo_client.start_session()
        
        try:
            with session.start_transaction():
                # Crear documento de venta
                venta_doc = {
                    "fecha": datetime.now().isoformat(),
                    "usuario": venta.usuario,
                    "cliente_rif": venta.cliente_rif,
                    "cliente_nombre": venta.cliente_nombre,
                    "productos": [p.dict() for p in venta.productos],
                    "total": venta.total,
                    "metodo_pago": venta.metodo_pago,
                    "observaciones": venta.observaciones,
                    "estado": "completada"
                }
                
                # Insertar venta
                resultado_venta = ventas_collection.insert_one(venta_doc, session=session)
                venta_id = resultado_venta.inserted_id
                
                # Procesar cada producto: descontar inventario y registrar en KARDEX
                productos_procesados = []
                
                for item_validacion in productos_validacion:
                    producto_inventario = item_validacion["producto"]
                    producto_venta = item_validacion["producto_venta"]
                    existencia_previo = item_validacion["existencia_previo"]
                    
                    codigo = producto_venta.codigo
                    cantidad = producto_venta.cantidad
                    
                    # Calcular nuevo stock
                    existencia_posterior = calcular_nuevo_stock(
                        existencia_previo,
                        cantidad,
                        "descontar"
                    )
                    
                    # Actualizar inventario
                    db["INVENTARIO_MAESTRO"].update_one(
                        {"codigo": str(codigo)},
                        {"$set": {"existencia": existencia_posterior}},
                        session=session
                    )
                    
                    # Registrar movimiento en KARDEX
                    kardex_data = {
                        "fecha": datetime.now().isoformat(),
                        "usuario": venta.usuario,
                        "tipo_movimiento": "venta",
                        "producto": producto_inventario,
                        "cantidad": cantidad,
                        "precio": producto_venta.precio_unitario,
                        "saldo_previo": existencia_previo,
                        "saldo_posterior": existencia_posterior,
                        "documento_origen": {
                            "tipo": "venta",
                            "id": str(venta_id)
                        },
                        "estado": "activo"
                    }
                    
                    db["KARDEX"].insert_one(kardex_data, session=session)
                    
                    productos_procesados.append({
                        "codigo": codigo,
                        "descripcion": producto_inventario.get("descripcion", ""),
                        "cantidad": cantidad,
                        "existencia_previo": existencia_previo,
                        "existencia_posterior": existencia_posterior,
                        "precio_unitario": producto_venta.precio_unitario
                    })
                
                # Confirmar transacción
                session.commit_transaction()
                
                return {
                    "message": "Venta registrada exitosamente",
                    "venta_id": str(venta_id),
                    "fecha": venta_doc["fecha"],
                    "total": venta.total,
                    "productos_procesados": len(productos_procesados),
                    "detalles_productos": productos_procesados
                }
                
        except Exception as e:
            # Rollback en caso de error
            session.abort_transaction()
            print(f"Error en transacción de venta: {e}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar la venta: {str(e)}"
            )
        finally:
            session.end_session()
            
    except HTTPException:
        # Re-lanzar HTTPException sin modificar
        raise
    except Exception as e:
        print(f"Error inesperado al registrar venta: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/punto-venta/ventas")
async def obtener_ventas(
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    usuario: Optional[str] = None,
    cliente_rif: Optional[str] = None
):
    """
    Endpoint para obtener ventas con filtros opcionales.
    """
    try:
        query = {}
        
        if fecha_desde or fecha_hasta:
            query["fecha"] = {}
            if fecha_desde:
                query["fecha"]["$gte"] = fecha_desde
            if fecha_hasta:
                query["fecha"]["$lte"] = fecha_hasta
        
        if usuario:
            query["usuario"] = usuario
        
        if cliente_rif:
            query["cliente_rif"] = cliente_rif
        
        ventas = list(ventas_collection.find(query).sort("fecha", -1).limit(100))
        
        for venta in ventas:
            venta["_id"] = str(venta["_id"])
        
        return {
            "total": len(ventas),
            "ventas": ventas
        }
        
    except Exception as e:
        print(f"Error al obtener ventas: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/punto-venta/ventas/{venta_id}")
async def obtener_venta_por_id(venta_id: str):
    """
    Endpoint para obtener una venta específica por ID.
    """
    try:
        venta = ventas_collection.find_one({"_id": ObjectId(venta_id)})
        
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        
        venta["_id"] = str(venta["_id"])
        
        return {"venta": venta}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        print(f"Error al obtener venta: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

