from fastapi import APIRouter, HTTPException, Body, Path, Query
from fastapi.responses import JSONResponse
from bson import ObjectId
from bson.errors import InvalidId
from ..database import db, pedidos_collection
from ..models.models import PedidoResumen, PedidoArmado, EstadoPedido, CantidadesEncontradas, PickingInfo, PackingInfo, EnvioInfo, FacturacionInfo, ValidacionPedido, CheckPickingData, ActualizarEstadoPedido, FinalizarCheckPicking
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from typing import Optional, List
from datetime import datetime, timedelta

router = APIRouter()

# Estados válidos para pedidos
ESTADOS_PEDIDO = [
    "nuevo",
    "picking", 
    "check_picking",  # ← NUEVO ESTADO
    "packing",
    "para_facturar",
    "facturando", 
    "enviado",
    "entregado",
    "cancelado"
]

@router.post("/pedidos/")
async def registrar_pedido(resumen: PedidoResumen):
    try:
        pedido = resumen.dict()
        pedido["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Solo asignar 'nuevo' si no viene estado en el resumen
        if not pedido.get("estado"):
            pedido["estado"] = "nuevo"
        
        # Inicializar campos de validación, cancelación y check picking
        pedido["validado"] = False
        pedido["fecha_validacion"] = None
        pedido["usuario_validacion"] = None
        pedido["fecha_cancelacion"] = None
        pedido["usuario_cancelacion"] = None
        pedido["verificaciones_check_picking"] = None
        pedido["fecha_check_picking"] = None
        pedido["usuario_check_picking"] = None
        pedido["estado_check_picking"] = "pendiente"
        
        result = db["PEDIDOS"].insert_one(pedido)
        if result.inserted_id:
            return {
                "message": "Pedido registrado exitosamente",
                "pedido_id": str(result.inserted_id),
                "estado": pedido["estado"],
                "validado": pedido["validado"]
            }
        else:
            raise HTTPException(status_code=500, detail="Error al registrar el pedido")
    except Exception as e:
        print(f"Error al registrar el pedido: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/obtener_pedidos/")
async def obtener_pedidos_optimizado(
    estados: Optional[List[str]] = Query(default=None),
    fecha_desde: Optional[str] = Query(default=None, description="Fecha desde en formato YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(default=None, description="Fecha hasta en formato YYYY-MM-DD")
):
    try:
        # Si no se proporcionan estados, obtener todos los pedidos
        query_filter = {}
        
        # Filtrar por estados si se proporcionan
        if estados and len(estados) > 0 and estados != [""]:
            # Filtrar estados vacíos
            estados_validos = [estado for estado in estados if estado and estado.strip()]
            if estados_validos:
                query_filter["estado"] = {"$in": estados_validos}

        # Filtro de fecha - usar fecha en lugar de fecha_creacion
        if fecha_desde or fecha_hasta:
            fecha_query = {}
            if fecha_desde:
                fecha_query["$gte"] = fecha_desde
            if fecha_hasta:
                fecha_query["$lte"] = fecha_hasta
            query_filter["fecha"] = fecha_query

        print(f"Query filter: {query_filter}")  # Debug

        pedidos = []
        for p in pedidos_collection.find(query_filter):
            pedido = {**p, "_id": str(p["_id"])}
            pedidos.append(pedido)

        print(f"Pedidos encontrados: {len(pedidos)}")  # Debug
        return pedidos

    except Exception as e:
        print(f"Error al obtener pedidos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener la lista de pedidos: {str(e)}")

# Nuevo endpoint: obtener pedidos por estado
@router.get("/pedidos/administracion/")
async def obtener_pedidos_administracion():
    """
    Devuelve todos los pedidos que necesitan validación en Administración.
    Solo muestra pedidos en estado 'nuevo' que NO han sido validados.
    """
    try:
        # Filtrar pedidos que estén en estado 'nuevo' y NO validados
        pedidos = list(pedidos_collection.find({
            "estado": "nuevo",
            "$or": [
                {"validado": {"$exists": False}},
                {"validado": False}
            ]
        }))
        
        for pedido in pedidos:
            pedido["_id"] = str(pedido["_id"])
        
        return JSONResponse(content=pedidos, status_code=200)
    except Exception as e:
        print(f"Error al obtener pedidos para administración: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener los pedidos para administración")

@router.get("/pedidos/picking/")
async def obtener_pedidos_picking():
    """
    Devuelve todos los pedidos que están listos para picking (validados y en estado 'nuevo').
    Solo muestra pedidos que han sido validados en Administración.
    """
    try:
        # Filtrar pedidos que estén validados y en estado 'nuevo'
        pedidos = list(pedidos_collection.find({
            "estado": "nuevo",
            "validado": True
        }))
        
        for pedido in pedidos:
            pedido["_id"] = str(pedido["_id"])
        
        return JSONResponse(content=pedidos, status_code=200)
    except Exception as e:
        print(f"Error al obtener pedidos para picking: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener los pedidos para picking")

@router.get("/pedidos/por_estado/{estado}")
async def obtener_pedidos_por_estado(estado: str):
    """
    Devuelve todos los pedidos con el estado especificado.
    """
    try:
        pedidos = list(pedidos_collection.find({"estado": estado}))
        for pedido in pedidos:
            pedido["_id"] = str(pedido["_id"])
        return JSONResponse(content=pedidos, status_code=200)
    except Exception as e:
        print(f"Error al obtener pedidos por estado: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener los pedidos por estado")
@router.post("/pedidos/armados/")
async def registrar_pedido_armado(resumen: PedidoArmado):
    """
    Endpoint para registrar un pedido armado en la colección PEDIDOS_ARMADOS.
    """
    try:
        pedido = resumen.dict()
        pedido["fecha_armado"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = db["PEDIDOS_ARMADOS"].insert_one(pedido)
        if result.inserted_id:
            return {
                "message": "Pedido armado registrado exitosamente",
                "pedido_id": str(result.inserted_id),
                "cliente": resumen.cliente,
                "total": resumen.total,
            }
        else:
            raise HTTPException(status_code=500, detail="Error al registrar el pedido armado")
    except Exception as e:
        print(f"Error al registrar el pedido armado: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/pedidos/actualizar_estado/{pedido_id}")
async def actualizar_estado_pedido(pedido_id: str, datos: ActualizarEstadoPedido):
    """
    Endpoint mejorado para actualizar el estado de un pedido con soporte completo para check_picking.
    Maneja todas las transiciones de estado con validaciones específicas.
    """
    try:
        # Convertir ID a ObjectId
        try:
            pedido_object_id = ObjectId(pedido_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="ID de pedido inválido")
        
        # Validar que el estado sea válido
        if datos.nuevo_estado not in ESTADOS_PEDIDO:
            raise HTTPException(status_code=400, detail="Estado no válido")
        
        # Buscar el pedido
        pedido = pedidos_collection.find_one({"_id": pedido_object_id})
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        estado_actual = pedido.get("estado", "")
        nuevo_estado = datos.nuevo_estado
        
        # Validaciones específicas por estado
        if nuevo_estado == "check_picking":
            # Solo pedidos en estado "picking" pueden ir a "check_picking"
            if estado_actual != "picking":
                raise HTTPException(
                    status_code=400, 
                    detail="Solo pedidos en estado 'picking' pueden ir a 'check_picking'"
                )
            
            # Marcar como en proceso de check picking
            update_fields = {
                "estado": nuevo_estado,
                "estado_check_picking": "en_proceso",
                "fecha_check_picking": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if datos.usuario:
                update_fields["usuario_check_picking"] = datos.usuario
        
        elif nuevo_estado == "packing":
            # Solo pedidos en estado "check_picking" pueden ir a "packing"
            if estado_actual != "check_picking":
                raise HTTPException(
                    status_code=400,
                    detail="Solo pedidos en estado 'check_picking' pueden ir a 'packing'"
                )
            
            # Guardar las verificaciones si se proporcionan
            update_fields = {"estado": nuevo_estado}
            if datos.verificaciones:
                update_fields["verificaciones_check_picking"] = datos.verificaciones
                update_fields["estado_check_picking"] = "completado"
                update_fields["fecha_check_picking"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if datos.usuario:
                    update_fields["usuario_check_picking"] = datos.usuario
        
        else:
            # Para otros estados, solo actualizar el estado principal
            update_fields = {"estado": nuevo_estado}
        
        # Actualizar el pedido
        resultado = pedidos_collection.update_one(
            {"_id": pedido_object_id},
            {"$set": update_fields}
        )
        
        if resultado.modified_count == 0:
            raise HTTPException(status_code=500, detail="No se pudo actualizar el pedido")
        
        # Obtener el pedido actualizado
        pedido_actualizado = pedidos_collection.find_one({"_id": pedido_object_id})
        pedido_actualizado["_id"] = str(pedido_actualizado["_id"])
        
        # Respuesta específica según el estado
        response_data = {
            "message": f"Estado actualizado a {nuevo_estado} exitosamente",
            "pedido_id": pedido_id,
            "nuevo_estado": nuevo_estado,
            "estado_anterior": estado_actual
        }
        
        if nuevo_estado == "packing" and datos.verificaciones:
            response_data["verificaciones_guardadas"] = True
            response_data["fecha_check_picking"] = update_fields.get("fecha_check_picking")
        
        return JSONResponse(content=response_data, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar el estado del pedido: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/pedidos/{pedido_id}/finalizar_check_picking")
async def finalizar_check_picking(pedido_id: str, datos: FinalizarCheckPicking):
    """
    Finaliza el proceso de Check Picking para un pedido.
    Valida todas las verificaciones y cambia el estado a 'packing'.
    """
    try:
        # Convertir ID a ObjectId
        try:
            pedido_object_id = ObjectId(pedido_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="ID de pedido inválido")
        
        # Buscar el pedido
        pedido = pedidos_collection.find_one({"_id": pedido_object_id})
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Validar que esté en check_picking
        if pedido.get("estado") != "check_picking":
            raise HTTPException(
                status_code=400,
                detail="El pedido debe estar en estado 'check_picking'"
            )
        
        # Validar que todas las verificaciones estén completas
        productos_pedido = pedido.get("productos", [])
        verificaciones = datos.verificaciones
        
        for producto in productos_pedido:
            codigo = producto.get("codigo") or producto.get("nombre")  # Usar código o nombre como identificador
            if codigo not in verificaciones:
                raise HTTPException(
                    status_code=400,
                    detail=f"Falta verificación para el producto {codigo}"
                )
            
            verif = verificaciones[codigo]
            if not all(key in verif for key in ['cantidadVerificada', 'fechaVencimiento', 'estado']):
                raise HTTPException(
                    status_code=400,
                    detail=f"Verificación incompleta para el producto {codigo}"
                )
        
        # Actualizar el pedido
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resultado = pedidos_collection.update_one(
            {"_id": pedido_object_id},
            {"$set": {
                "verificaciones_check_picking": verificaciones,
                "estado_check_picking": "completado",
                "fecha_check_picking": fecha_actual,
                "usuario_check_picking": datos.usuario,
                "estado": "packing"
            }}
        )
        
        if resultado.modified_count == 0:
            raise HTTPException(status_code=500, detail="No se pudo finalizar Check Picking")
        
        return JSONResponse(
            content={
                "message": "Check Picking completado exitosamente",
                "pedido_id": pedido_id,
                "nuevo_estado": "packing",
                "verificaciones_guardadas": len(verificaciones),
                "fecha_check_picking": fecha_actual,
                "usuario_check_picking": datos.usuario
            },
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al finalizar Check Picking: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/pedidos/{pedido_id}/cancelar")
async def cancelar_pedido(pedido_id: str):
    """
    Cancela un pedido cambiando su estado a 'cancelado'.
    Solo permite cancelar pedidos que NO estén en estado 'entregado'.
    """
    try:
        # Convertir ID a ObjectId
        try:
            pedido_object_id = ObjectId(pedido_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="ID de pedido inválido")
        
        # Buscar el pedido
        pedido = pedidos_collection.find_one({"_id": pedido_object_id})
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Verificar que el pedido no esté entregado
        estado_actual = pedido.get("estado", "")
        if estado_actual == "entregado":
            raise HTTPException(
                status_code=400, 
                detail="No se puede cancelar un pedido que ya ha sido entregado"
            )
        
        # Verificar que el pedido no esté ya cancelado
        if estado_actual == "cancelado":
            raise HTTPException(
                status_code=400, 
                detail="El pedido ya está cancelado"
            )
        
        # Actualizar el pedido con estado cancelado y campos de auditoría
        fecha_cancelacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resultado = pedidos_collection.update_one(
            {"_id": pedido_object_id},
            {"$set": {
                "estado": "cancelado",
                "fecha_cancelacion": fecha_cancelacion,
                "usuario_cancelacion": "admin"  # Por ahora fijo, después se puede obtener del token
            }}
        )
        
        if resultado.modified_count == 0:
            raise HTTPException(status_code=500, detail="No se pudo cancelar el pedido")
        
        # Obtener el pedido actualizado
        pedido_actualizado = pedidos_collection.find_one({"_id": pedido_object_id})
        pedido_actualizado["_id"] = str(pedido_actualizado["_id"])
        
        return JSONResponse(
            content={
                "message": "Pedido cancelado exitosamente",
                "pedido": pedido_actualizado,
                "estado_anterior": estado_actual,
                "estado_nuevo": "cancelado",
                "fecha_cancelacion": fecha_cancelacion,
                "usuario_cancelacion": "admin"
            },
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al cancelar pedido: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/pedidos/actualizar/{id}")
async def actualizar_pedido(id: str, pedido_actualizado: dict):
    """
    Endpoint para actualizar un pedido en la colección PEDIDOS.
    """
    try:
        try:
            pedido_object_id = ObjectId(id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="ID inválido")
        if "_id" in pedido_actualizado:
            del pedido_actualizado["_id"]
        resultado = db["PEDIDOS"].find_one_and_update(
            {"_id": pedido_object_id},
            {"$set": pedido_actualizado},
            return_document=True
        )
        if resultado:
            resultado["_id"] = str(resultado["_id"])
            return JSONResponse(content=jsonable_encoder(resultado), status_code=200)
        else:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el pedido: {error}")

@router.patch("/pedidos/actualizar_cantidades/{pedido_id}")
async def actualizar_cantidades_encontradas(pedido_id: str = Path(...), body: CantidadesEncontradas = Body(...)):
    """
    Actualiza las cantidades encontradas de los productos de un pedido.
    El body debe ser: { "cantidades": { "<pedidoid>_<productoid>": cantidad, ... } }
    """
    try:
        pedido_object_id = ObjectId(pedido_id)
        pedido = db["PEDIDOS"].find_one({"_id": pedido_object_id})
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        productos = pedido.get("productos", [])
        cantidades = body.cantidades
        for prod in productos:
            key = f"{pedido_id}_{prod['id']}"
            if key in cantidades:
                prod["cantidad_encontrada"] = cantidades[key]
        db["PEDIDOS"].update_one({"_id": pedido_object_id}, {"$set": {"productos": productos}})
        return {"message": "Cantidades encontradas actualizadas"}
    except Exception as e:
        print(f"Error al actualizar cantidades encontradas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/pedidos/por_cliente/{rif}")
async def obtener_pedidos_por_cliente(rif: str):
    """
    Devuelve todos los pedidos asociados a un RIF de cliente.
    """
    try:
        pedidos = list(pedidos_collection.find({"rif": rif}))
        for pedido in pedidos:
            pedido["_id"] = str(pedido["_id"])
        return JSONResponse(content=pedidos, status_code=200)
    except Exception as e:
        print(f"Error al obtener pedidos por cliente: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener los pedidos del cliente")

@router.patch("/pedidos/actualizar_picking/{pedido_id}")
async def actualizar_picking_info(
    pedido_id: str = Path(...),
    picking: PickingInfo = Body(...)
):
    """
    Actualiza los campos de picking (almacenista, fechainicio_picking, fechafin_picking, estado_picking) en un pedido,
    agrupados bajo el objeto 'picking'.
    """
    try:
        pedido_object_id = ObjectId(pedido_id)
        picking_data = picking.dict()
        update_fields = {f"picking.{k}": v for k, v in picking_data.items()}
        if not update_fields:
            update_fields["picking"] = {}
        if not update_fields:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar picking.")
        result = db["PEDIDOS"].update_one(
            {"_id": pedido_object_id},
            {"$set": update_fields}
        )
        if result.matched_count:
            return {"message": "Información de picking actualizada"}
        else:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
    except Exception as e:
        print(f"Error al actualizar picking: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.patch("/pedidos/actualizar_packing/{pedido_id}")
async def actualizar_packing_info(
    pedido_id: str = Path(...),
    packing: PackingInfo = Body(...)
):
    """
    Actualiza el objeto packing (usuario, estado_packing, fechainicio, fechafin) en un pedido.
    """
    try:
        pedido_object_id = ObjectId(pedido_id)
        update_fields = {f"packing.{k}": v for k, v in packing.dict().items() if v is not None}
        if not update_fields:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar packing.")
        result = db["PEDIDOS"].update_one(
            {"_id": pedido_object_id},
            {"$set": update_fields}
        )
        if result.matched_count:
            return {"message": "Información de packing actualizada"}
        else:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
    except Exception as e:
        print(f"Error al actualizar packing: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.patch("/pedidos/actualizar_envio/{pedido_id}")
async def actualizar_envio_info(
    pedido_id: str = Path(...),
    envio: EnvioInfo = Body(...)
):
    """
    Actualiza el objeto envio (usuario, chofer, estadoenvio, fechaini, fechafin) en un pedido.
    """
    try:
        pedido_object_id = ObjectId(pedido_id)
        update_fields = {f"envio.{k}": v for k, v in envio.dict().items() if v is not None}
        if not update_fields:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar envio.")
        result = db["PEDIDOS"].update_one(
            {"_id": pedido_object_id},
            {"$set": update_fields}
        )
        if result.matched_count:
            return {"message": "Información de envio actualizada"}
        else:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
    except Exception as e:
        print(f"Error al actualizar envio: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/pedido/{pedido_id}")
async def obtener_pedido_por_id(pedido_id: str):
    """
    Devuelve un pedido por su ID, asegurando que los objetos picking, packing y envio siempre estén presentes (aunque vacíos).
    """
    try:
        pedido_object_id = ObjectId(pedido_id)
        pedido = db["PEDIDOS"].find_one({"_id": pedido_object_id})
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        pedido["_id"] = str(pedido["_id"])
        # Asegurar que los objetos picking, packing y envio existan aunque estén vacíos
        if "picking" not in pedido:
            pedido["picking"] = {}
        if "packing" not in pedido:
            pedido["packing"] = {}
        if "envio" not in pedido:
            pedido["envio"] = {}
        return JSONResponse(content=pedido, status_code=200)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
    except Exception as e:
        print(f"Error al obtener pedido por id: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/conductores/")
async def obtener_conductores():
    """
    Devuelve todos los conductores registrados en la colección CONDUCTORES.
    """
    try:
        conductores = list(db["CONDUCTORES"].find({}))
        for conductor in conductores:
            conductor["_id"] = str(conductor["_id"])
        return JSONResponse(content=conductores, status_code=200)
    except Exception as e:
        print(f"Error al obtener conductores: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener la lista de conductores")

@router.get("/pedidos/para_facturar/")
async def obtener_pedidos_para_facturar():
    """
    Devuelve todos los pedidos en estado 'para_facturar' o 'facturando'.
    """
    try:
        pedidos = list(pedidos_collection.find({"estado": {"$in": ["para_facturar", "facturando"]}}))
        for pedido in pedidos:
            pedido["_id"] = str(pedido["_id"])
        return JSONResponse(content=pedidos, status_code=200)
    except Exception as e:
        print(f"Error al obtener pedidos para facturación: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener los pedidos para facturación")

# Nuevo endpoint: consultar todos los pedidos con el estatus 'checkpicking'

@router.put("/pedidos/actualizar_facturacion/{pedido_id}")
async def actualizar_estado_facturacion(pedido_id: str, facturacion: FacturacionInfo = Body(...)):
    """
    Cambia el estado de un pedido a 'facturando' y actualiza el objeto facturacion.
    """
    try:
        pedido_object_id = ObjectId(pedido_id)
        update_fields = {
            "estado": "facturando",
            "facturacion": facturacion.dict()
        }
        result = db["PEDIDOS"].update_one({"_id": pedido_object_id}, {"$set": update_fields})
        if result.modified_count:
            return {"message": "Estado y facturación actualizados"}
        else:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar la facturación: {e}")

@router.put("/pedidos/finalizar_facturacion/{pedido_id}")
async def finalizar_facturacion(pedido_id: str, facturacion: FacturacionInfo = Body(...)):
    """
    Cambia el estado de un pedido de 'facturando' a 'enviado' y actualiza el objeto facturacion.
    """
    try:
        pedido_object_id = ObjectId(pedido_id)
        update_fields = {
            "estado": "enviado",
            "facturacion": facturacion.dict()
        }
        result = db["PEDIDOS"].update_one({"_id": pedido_object_id}, {"$set": update_fields})
        if result.modified_count:
            return {"message": "Facturación finalizada y pedido enviado"}
        else:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al finalizar la facturación: {e}")

@router.get("/pedidos/checkpicking/")
async def obtener_pedidos_checkpicking():
    """
    Devuelve todos los pedidos con el estado 'checkpicking'.
    """
    try:
        pedidos = list(pedidos_collection.find({"estado": "checkpicking"}))
        for pedido in pedidos:
            pedido["_id"] = str(pedido["_id"])
        return JSONResponse(content=pedidos, status_code=200)
    except Exception as e:
        print(f"Error al obtener pedidos con estado checkpicking: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener los pedidos con estado checkpicking")

@router.post("/pedidos/{pedido_id}/validar")
async def validar_pedido(pedido_id: str, validacion: ValidacionPedido):
    """
    Valida un pedido con PIN y cambia su estado de 'nuevo' a 'picking'.
    
    Args:
        pedido_id: ID del pedido a validar
        validacion: Objeto con el PIN de validación
    
    Returns:
        Confirmación de éxito con el pedido actualizado
    """
    try:
        # PIN fijo para validación (puedes cambiarlo después)
        PIN_VALIDO = "1234"
        
        # Verificar que el PIN sea correcto
        if validacion.pin != PIN_VALIDO:
            raise HTTPException(
                status_code=401, 
                detail="PIN incorrecto. Acceso denegado."
            )
        
        # Buscar el pedido por ID
        from bson import ObjectId
        try:
            pedido_object_id = ObjectId(pedido_id)
        except:
            raise HTTPException(status_code=400, detail="ID de pedido inválido")
        
        pedido = pedidos_collection.find_one({"_id": pedido_object_id})
        
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Verificar que el pedido esté en estado 'nuevo'
        if pedido.get("estado") != "nuevo":
            raise HTTPException(
                status_code=400, 
                detail=f"El pedido no está en estado 'nuevo'. Estado actual: {pedido.get('estado')}"
            )
        
        # Actualizar el pedido con campos de validación (NO cambiar estado)
        fecha_validacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resultado = pedidos_collection.update_one(
            {"_id": pedido_object_id},
            {"$set": {
                "validado": True,
                "fecha_validacion": fecha_validacion,
                "usuario_validacion": "admin"  # Por ahora fijo, después se puede obtener del token
            }}
        )
        
        if resultado.modified_count == 0:
            raise HTTPException(status_code=500, detail="No se pudo validar el pedido")
        
        # Obtener el pedido actualizado
        pedido_actualizado = pedidos_collection.find_one({"_id": pedido_object_id})
        pedido_actualizado["_id"] = str(pedido_actualizado["_id"])
        
        return JSONResponse(
            content={
                "message": "Pedido validado exitosamente",
                "pedido": pedido_actualizado,
                "validado": True,
                "fecha_validacion": fecha_validacion,
                "usuario_validacion": "admin"
            },
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al validar pedido: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
