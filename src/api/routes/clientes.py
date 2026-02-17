from fastapi import APIRouter, HTTPException, Body, status, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
from pymongo.database import Database
from ..database import get_db
from ..models.models import Client, ClientUpdate
from ..auth.auth_utils import get_password_hash
import traceback

router = APIRouter()

@router.post("/clientes/", response_model=Client, status_code=201)
async def create_client(client: Client, db: Database = Depends(get_db)):
    try:
        clients_collection = db["CLIENTES"]
        client_dict = client.dict()
        client_dict["password"] = get_password_hash(client_dict["password"])
        if clients_collection.find_one({"rif": client.rif}):
            raise HTTPException(status_code=400, detail="El RIF ya está registrado")
        if clients_collection.find_one({"email": client.email}):
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
        client_dict["estado_aprobacion"] = "pendiente"
        clients_collection.insert_one(client_dict)
        return client
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
async def aprobar_cliente(rif: str, db: Database = Depends(get_db)):
    """Aprueba un cliente; podrá hacer login y tener acceso completo."""
    clients_collection = db["CLIENTES"]
    result = clients_collection.update_one(
        {"rif": rif, "estado_aprobacion": "pendiente"},
        {"$set": {"estado_aprobacion": "aprobado"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o ya no está pendiente")
    return {"message": "Cliente aprobado. Ya puede iniciar sesión."}


@router.patch("/clientes/{rif}/rechazar", summary="Rechazar solicitud de cliente (admin)")
async def rechazar_cliente(rif: str, db: Database = Depends(get_db)):
    """Rechaza un cliente; al intentar login verá mensaje de solicitud rechazada."""
    clients_collection = db["CLIENTES"]
    result = clients_collection.update_one(
        {"rif": rif, "estado_aprobacion": "pendiente"},
        {"$set": {"estado_aprobacion": "rechazado"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o ya no está pendiente")
    return {"message": "Solicitud rechazada."}


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

@router.get("/clientes/{rif}")
async def read_client(rif: str, db: Database = Depends(get_db)):
    clients_collection = db["CLIENTES"]
    client = clients_collection.find_one({"rif": rif})
    if client:
        client["_id"] = str(client["_id"])
        return client
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

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
    try:
        clients_collection = db["CLIENTES"]
        cliente = clients_collection.find_one({"rif": rif})
        if not cliente:
            return JSONResponse(content={"error": "Cliente no encontrado"}, status_code=404)
        cliente["_id"] = str(cliente["_id"])
        cliente = {
            "_id": cliente["_id"],
            "email": cliente.get("email", ""),
            "rif": cliente.get("rif", ""),
            "encargado": cliente.get("encargado", ""),
            "direccion": cliente.get("direccion", ""),
            "telefono": cliente.get("telefono", ""),
            "activo": cliente.get("activo", True),
            "descuento1": float(cliente.get("descuento1", 0)),
            "descuento2": float(cliente.get("descuento2", 0)),
            "descuento3": float(cliente.get("descuento3", 0))
        }
        return JSONResponse(content=cliente, status_code=200)
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
