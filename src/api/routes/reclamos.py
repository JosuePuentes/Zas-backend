from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from pymongo.database import Database
from ..database import get_db
from ..models.models import ReclamoCliente

router = APIRouter()

@router.post("/reclamos/cliente")
async def registrar_reclamo_cliente(reclamo: ReclamoCliente, db: Database = Depends(get_db)):
    """
    Recibe un reclamo de cliente y lo guarda en la colección RECLAMOS_CLIENTE.
    """
    try:
        reclamo_dict = reclamo.dict()
        reclamo_dict["fecha"] = reclamo.fecha or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = db["RECLAMOS_CLIENTE"].insert_one(reclamo_dict)
        if result.inserted_id:
            return {"message": "Reclamo registrado exitosamente", "reclamo_id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Error al registrar el reclamo")
    except Exception as e:
        print(f"Error al registrar el reclamo: {e}")
        raise HTTPException(status_code=500, detail="Error interno al registrar el reclamo")

@router.get("/reclamos/cliente/{rif}")
async def obtener_reclamos_cliente(rif: str, db: Database = Depends(get_db)):
    """
    Devuelve todos los reclamos asociados a un RIF de cliente.
    """
    try:
        reclamos = list(db["RECLAMOS_CLIENTE"].find({"rif": rif}))
        for reclamo in reclamos:
            reclamo["_id"] = str(reclamo["_id"])
        return reclamos
    except Exception as e:
        print(f"Error al obtener reclamos del cliente: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener los reclamos del cliente")
