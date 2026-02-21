from fastapi import APIRouter, HTTPException, Body, status, Depends
from typing import Optional
from fastapi.responses import JSONResponse
from bson import ObjectId
from pymongo.database import Database
from ..database import get_db
from ..models.models import Client, ClientUpdate, AprobarClienteBody, RechazarClienteBody
from ..auth.auth_utils import get_password_hash
import traceback

router = APIRouter()

@router.post("/clientes/", response_model=Client, status_code=201)
async def create_client(client: Client, db: Database = Depends(get_db)):
    """
    Crear cliente. Si no se envía email o password, se generan automáticamente.
    Email generado: {rif}@cliente.local (o similar)
    Password generado: {rif}123 (o similar)
    """
    try:
        clients_collection = db["CLIENTES"]
        if clients_collection.find_one({"rif": client.rif}):
            raise HTTPException(status_code=400, detail="El RIF ya está registrado")
        
        client_dict = client.dict(exclude_none=True)
        
        # Generar email si no se proporciona
        email_provided = client_dict.get("email")
        if not email_provided:
            # Email basado en RIF: quitar guiones y caracteres especiales, convertir a minúsculas
            email_base = client.rif.replace("-", "").replace(".", "").lower()
            client_dict["email"] = f"{email_base}@cliente.local"
        
        # Verificar que el email no esté duplicado
        if clients_collection.find_one({"email": client_dict["email"]}):
            if email_provided:
                raise HTTPException(status_code=400, detail="El correo ya está registrado")
            # Si el email generado ya existe, añadir sufijo
            counter = 1
            original_email = client_dict["email"]
            while clients_collection.find_one({"email": client_dict["email"]}):
                client_dict["email"] = f"{original_email.split('@')[0]}{counter}@cliente.local"
                counter += 1
        
        # Generar password si no se proporciona
        password_provided = client_dict.get("password")
        if not password_provided:
            # Password basado en RIF: primeros 6 caracteres del RIF sin guiones + "123"
            password_base = client.rif.replace("-", "").replace(".", "")[:6].upper()
            client_dict["password"] = f"{password_base}123"
        
        # Hashear la contraseña (tanto si se proporcionó como si se generó)
        client_dict["password"] = get_password_hash(client_dict["password"])
        
        # Estado de aprobación
        client_dict["estado_aprobacion"] = "pendiente"
        
        clients_collection.insert_one(client_dict)
        
        # Devolver el cliente creado (sin password hasheada en la respuesta)
        client_response = client_dict.copy()
        client_response["password"] = ""  # No devolver password
        return JSONResponse(content=client_response, status_code=201)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clientes/solicitudes/pendientes", summary="Listar solicitudes de nuevos clientes (admin)")
async def listar_solicitudes_pendientes(db: Database = Depends(get_db)):
    """
    Devuelve los clientes con estado_aprobacion = 'pendiente' para el módulo administrativo.
    Campos: _id, empresa, rif, telefono, encargado, email, direccion.
    """
    clients_collection = db["CLIENTES"]
    solicitudes = list(clients_collection.find(
        {"estado_aprobacion": "pendiente"},
        {"_id": 1, "empresa": 1, "rif": 1, "telefono": 1, "encargado": 1, "email": 1, "direccion": 1, "estado_aprobacion": 1}
    ))
    for s in solicitudes:
        s["_id"] = str(s["_id"])
    return JSONResponse(content=solicitudes, status_code=200)


@router.patch("/clientes/{rif}/aprobar", summary="Aprobar solicitud de cliente (admin)")
async def aprobar_cliente(rif: str, body: Optional[AprobarClienteBody] = Body(None), db: Database = Depends(get_db)):
    """Aprueba un cliente; podrá hacer login. Body opcional: limite_credito, dias_credito, monto."""
    clients_collection = db["CLIENTES"]
    update = {"estado_aprobacion": "aprobado"}
    if body:
        if body.limite_credito is not None:
            update["limite_credito"] = body.limite_credito
        if body.dias_credito is not None:
            update["dias_credito"] = body.dias_credito
        if body.monto is not None:
            update["limite_credito"] = body.monto
    result = clients_collection.update_one(
        {"rif": rif, "estado_aprobacion": "pendiente"},
        {"$set": update}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o ya no está pendiente")
    return {"message": "Cliente aprobado. Ya puede iniciar sesión."}


@router.patch("/clientes/{rif}/rechazar", summary="Rechazar solicitud de cliente (admin)")
async def rechazar_cliente(rif: str, body: RechazarClienteBody = Body(...), db: Database = Depends(get_db)):
    """Rechaza un cliente con motivo obligatorio; el motivo se guarda para informes."""
    clients_collection = db["CLIENTES"]
    result = clients_collection.update_one(
        {"rif": rif, "estado_aprobacion": "pendiente"},
        {"$set": {"estado_aprobacion": "rechazado", "motivo_rechazo": body.motivo.strip()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o ya no está pendiente")
    return {"message": "Solicitud rechazada."}


@router.get("/clientes/solicitudes/historial", summary="Historial de solicitudes aprobadas/rechazadas (admin)")
async def listar_solicitudes_historial(db: Database = Depends(get_db)):
    """
    Devuelve clientes con estado_aprobacion aprobado o rechazado, con motivo_rechazo cuando aplique.
    Para informes de solicitudes.
    """
    clients_collection = db["CLIENTES"]
    solicitudes = list(clients_collection.find(
        {"estado_aprobacion": {"$in": ["aprobado", "rechazado"]}},
        {"_id": 1, "empresa": 1, "rif": 1, "telefono": 1, "encargado": 1, "email": 1, "direccion": 1, "estado_aprobacion": 1, "motivo_rechazo": 1, "limite_credito": 1, "dias_credito": 1}
    ))
    for s in solicitudes:
        s["_id"] = str(s["_id"])
        s.setdefault("motivo_rechazo", None)
    return JSONResponse(content=solicitudes, status_code=200)


@router.get("/clientes/all", 
            summary="Obtener todos los clientes (conversión manual)")
async def get_all_clients_manual_conversion(db: Database = Depends(get_db)):
    """
    Obtiene una lista de clientes y convierte manualmente el campo _id
    de ObjectId a string antes de devolver el JSON.
    """
    clients_collection = db["CLIENTES"]
    clients_list = []
    
    # 1. Iteramos sobre cada documento que viene de la base de datos
    for client in clients_collection.find():
        # 2. Creamos un nuevo campo 'id' con el string del ObjectId
        client["id"] = str(client["_id"])
        
        # 3. Eliminamos el campo original '_id' que es un objeto
        del client["_id"]
        
        # 4. Agregamos el documento modificado a nuestra lista
        clients_list.append(client)
        
    # 5. Devolvemos la lista formateada usando JSONResponse
    return JSONResponse(content=clients_list, status_code=status.HTTP_200_OK)

@router.patch("/clientes/{rif}")
async def update_client(rif: str, client: ClientUpdate, db: Database = Depends(get_db)):
    clients_collection = db["CLIENTES"]
    # Requiere implementación de update_document
    success, result = update_document(clients_collection, {"rif": rif}, client.dict())
    if success:
        return {"message": result}
    raise HTTPException(status_code=404, detail=result)

@router.delete("/clientes/{rif}")
async def delete_client(rif: str, db: Database = Depends(get_db)):
    clients_collection = db["CLIENTES"]
    # Requiere implementación de delete_document
    success, result = delete_document(clients_collection, {"rif": rif})
    if success:
        return {"message": result}
    raise HTTPException(status_code=404, detail=result)

@router.get("/clientes/")
async def obtener_clientes(db: Database = Depends(get_db)):
    try:
        clients_collection = db["CLIENTES"]
        clientes = list(clients_collection.find({}, {"_id": 1, "email": 1, "rif": 1, "encargado": 1}))
        for cliente in clientes:
            cliente["_id"] = str(cliente["_id"])
        return JSONResponse(content=clientes, status_code=200)
    except Exception as e:
        print(f"Error al obtener clientes: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener la lista de clientes")

@router.get("/clientes/{rif}")
async def obtener_cliente_por_rif(rif: str, db: Database = Depends(get_db)):
    """Detalle del cliente. Incluye limite_credito, limite_consumido, facturas_vencidas para validación admin."""
    try:
        clients_collection = db["CLIENTES"]
        pedidos_collection = db.get("PEDIDOS") or db["PEDIDOS"]
        cliente = clients_collection.find_one({"rif": rif})
        if not cliente:
            return JSONResponse(content={"error": "Cliente no encontrado"}, status_code=404)
        cliente["_id"] = str(cliente["_id"])
        limite_credito = float(cliente.get("limite_credito", 0))
        # Limite consumido: suma de totales de pedidos facturados no pagados (simplificado: pedidos en estado para_facturar/facturando/enviado/entregado)
        limite_consumido = 0.0
        try:
            pedidos_cliente = list(pedidos_collection.find({"rif": rif, "estado": {"$in": ["para_facturar", "facturando", "enviado", "entregado"]}}))
            limite_consumido = sum(float(p.get("total", 0)) for p in pedidos_cliente)
        except Exception:
            pass
        # Facturas vencidas: si tiene dias_credito y pedidos antiguos sin pagar (simplificado: siempre False si no hay módulo facturas)
        tiene_facturas_vencidas = False
        dias_credito = cliente.get("dias_credito", 0)
        # Condiciones comerciales: texto para área cliente (BD o construido)
        condiciones_comerciales = cliente.get("condiciones_comerciales")
        if not condiciones_comerciales and (dias_credito or limite_credito):
            parts = []
            if dias_credito:
                parts.append(f"{dias_credito} días de crédito")
            if limite_credito:
                parts.append(f"Límite ${limite_credito:,.2f}")
            condiciones_comerciales = "; ".join(parts) if parts else ""
        if condiciones_comerciales is None:
            condiciones_comerciales = ""
        out = {
            "_id": cliente["_id"],
            "email": cliente.get("email", ""),
            "rif": cliente.get("rif", ""),
            "empresa": cliente.get("empresa", ""),
            "encargado": cliente.get("encargado", ""),
            "direccion": cliente.get("direccion", ""),
            "telefono": cliente.get("telefono", ""),
            "activo": cliente.get("activo", True),
            "descuento1": float(cliente.get("descuento1", 0)),
            "descuento2": float(cliente.get("descuento2", 0)),
            "descuento3": float(cliente.get("descuento3", 0)),
            "descuento_comercial": float(cliente.get("descuento_comercial", 0)),
            "descuento_pronto_pago": float(cliente.get("descuento_pronto_pago", 0)),
            "limite_credito": limite_credito,
            "limite_consumido": limite_consumido,
            "dias_credito": dias_credito,
            "condiciones_comerciales": condiciones_comerciales,
            "facturas_vencidas": tiene_facturas_vencidas,
        }
        return JSONResponse(content=out, status_code=200)
    except Exception as e:
        print(f"Error al obtener cliente por RIF: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(content={"error": f"Error al obtener el cliente: {str(e)}"}, status_code=500)

def update_document(collection, filter_query, update_data):
    result = collection.update_one(filter_query, {"$set": update_data})
    if result.modified_count:
        return True, "Documento actualizado correctamente"
    return False, "No se encontró el documento o no se realizaron cambios"

def delete_document(collection, filter_query):
    result = collection.delete_one(filter_query)
    if result.deleted_count:
        return True, "Documento eliminado correctamente"
    return False, "No se encontró el documento"
