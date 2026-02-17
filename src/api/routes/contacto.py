from fastapi import APIRouter, HTTPException, Depends
from pymongo.database import Database
from ..database import get_db
from ..models.models import ContactForm

router = APIRouter()

@router.post("/contacto")
def enviar_contacto(form: ContactForm, db: Database = Depends(get_db)):
    try:
        db["formularios"].insert_one({
            "nombre": form.nombre,
            "email": form.email,
            "telefono": form.telefono,
            "mensaje": form.mensaje
        })
        return {"message": "Mensaje recibido correctamente"}
    except Exception as e:
        print(f"Error al guardar el formulario de contacto: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar el mensaje de contacto.")
