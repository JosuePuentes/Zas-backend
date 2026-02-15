from fastapi import FastAPI, HTTPException, UploadFile, File, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
from datetime import datetime
import os
import traceback
from fastapi import FastAPI, HTTPException, Path
from pymongo import MongoClient
from pydantic import BaseModel
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta
from typing import List, Optional
import math
from bson import ObjectId
from bson.errors import InvalidId

# Cargar variables de entorno
load_dotenv()

# Configuración de conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI")
# MONGO_URI = "mongodb+srv://rapifarma:<db_password>@cluster0.9nirn5t.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)

# Acceso a las colecciones de la base de datos
db = client["DROCOLVEN"]
collection = db["mi_coleccion"]
inventario_collection = db["INVENTARIO"]
clients_collection = db["CLIENTES"]
usuarios_admin_collection = db["USUARIOSADMINISTRATIVOS"]
ventas_collection = db["VENTAS"]
pedidos_collection = db["PEDIDOS"]
# Configuración de cifrado de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Inicializar FastAPI
app = FastAPI()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir modelos de datos
class Item(BaseModel):
    name: str
    description: str
    price: float

class Client(BaseModel):
    rif: str
    encargado: str
    direccion: str
    telefono: str
    email: str
    password: str
    descripcion: str
    dias_credito: int
    limite_credito: float
    activo: bool = True
    descuento1: float = 0
    descuento2: float = 0
    descuento3: float = 0

class ProductoInventario(BaseModel):
    codigo: str
    descripcion: str
    dpto: str
    nacional: str
    laboratorio: str
    fv: str
    existencia: int
    precio: float
    cantidad: int
    descuento1: float
    descuento2: float
    descuento3: float

class UserRegister(BaseModel):
    email: str
    password: str
    rif: str
    direccion: str
    telefono: str
    encargado: str
    activo: bool = True
    descuento1: float = 0.0
    descuento2: float = 0.0
    descuento3: float = 0.0
# Modelo para el inicio de sesión
class UserLogin(BaseModel):
    email: str
    password: str

class UserAdminRegister(BaseModel):
    usuario: str
    password: str
    rol: str
    modulos: List[str]

class AdminLogin(BaseModel):
    usuario: str
    password: str

class ProductoPedido(BaseModel):
    id: str
    descripcion: str
    precio: float
    descuento1: float
    descuento2: float
    descuento3: float
    descuento4: float
    cantidad_pedida: int
    cantidad_encontrada: int
    subtotal: float

class PedidoResumen(BaseModel):
    cliente: str
    rif: str
    observacion: str
    total: float
    subtotal: float
    productos: list[ProductoPedido]

class PedidoArmado(BaseModel):
    cliente: str
    rif: str
    observacion: str
    total: float
    productos: list[ProductoPedido]

class EstadoPedido(BaseModel):
    nuevo_estado: str

class ContactForm(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    mensaje: str

class CantidadesEncontradas(BaseModel):
    cantidades: dict

class PickingInfo(BaseModel):
    usuario: Optional[str] = None
    fechainicio_picking: Optional[str] = None
    fechafin_picking: Optional[str] = None
    estado_picking: Optional[str] = None

class PackingInfo(BaseModel):
    usuario: Optional[str] = None
    estado_packing: Optional[str] = None
    fechainicio_packing: Optional[str] = None
    fechafin_packing: Optional[str] = None

class EnvioInfo(BaseModel):
    usuario: Optional[str] = None
    chofer: Optional[str] = None
    estado_envio: Optional[str] = None
    fechaini_envio: Optional[str] = None
    fechafin_envio: Optional[str] = None

class ReclamoCliente(BaseModel):
    pedido_id: str
    rif: str
    cliente: str
    productos: list[dict]  # [{id, descripcion, cantidad, motivo}]
    observacion: str = ""
    fecha: str = ""

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = {
        "id": str(user["_id"]),
        "name": user["rif"],
        "email": user["email"],
        "rif": user["rif"],  # Agregado para que el frontend reciba rif
        "exp": datetime.utcnow() + expires_delta,
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_admin_access_token(admin: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = {
        "id": str(admin["_id"]),
        "usuario": admin["usuario"],
        "rol": admin.get("rol", "admin"),
        "modulos": admin.get("modulos", []),
        "exp": datetime.utcnow() + expires_delta,
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Funciones de MongoDB
def insert_document(collection, document):
    result = collection.insert_one(document)
    if result.inserted_id:
        return True, document
    return False, "Error al insertar el documento"

def update_document(collection, filter_query, update_data):
    result = collection.update_one(filter_query, {"$set": update_data})
    if result.modified_count:
        return True, "Documento actualizado correctamente"
    return False, "Documento no encontrado o no se realizaron cambios"

def delete_document(collection, filter_query):
    result = collection.delete_one(filter_query)
    if result.deleted_count:
        return True, "Documento eliminado correctamente"
    return False, "Documento no encontrado"

# Rutas CRUD
@app.get("/")
async def root():
    return {"message": "Servidor conectado exitosamente"}

@app.post("/items/", response_model=Item, status_code=201)
async def create_item(item: Item):
    success, result = insert_document(collection, item.dict())
    if success:
        return result
    raise HTTPException(status_code=500, detail=result)

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    item = collection.find_one({"_id": item_id})
    if item:
        item["_id"] = str(item["_id"])
        return item
    raise HTTPException(status_code=404, detail="Ítem no encontrado")

@app.put("/items/{item_id}")
async def update_item(item_id: str, item: Item):
    success, result = update_document(collection, {"_id": item_id}, item.dict())
    if success:
        return {"message": result}
    raise HTTPException(status_code=404, detail=result)

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    success, result = delete_document(collection, {"_id": item_id})
    if success:
        return {"message": result}
    raise HTTPException(status_code=404, detail=result)

@app.post("/clientes/", response_model=Client, status_code=201)
async def create_client(client: Client):
    try:
        client_dict = client.dict()
        client_dict["password"] = get_password_hash(client_dict["password"])
        # Verificar si el cliente ya existe por RIF o email
        if clients_collection.find_one({"rif": client.rif}):
            raise HTTPException(status_code=400, detail="El RIF ya está registrado")
        if clients_collection.find_one({"email": client.email}):
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
        clients_collection.insert_one(client_dict)
        return client
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clientes/{rif}")
async def read_client(rif: str):
    client = clients_collection.find_one({"rif": rif})
    if client:
        client["_id"] = str(client["_id"])
        return client
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

@app.put("/clientes/{rif}")
async def update_client(rif: str, client: Client):
    success, result = update_document(clients_collection, {"rif": rif}, client.dict())
    if success:
        return {"message": result}
    raise HTTPException(status_code=404, detail=result)

@app.delete("/clientes/{rif}")
async def delete_client(rif: str):
    success, result = delete_document(clients_collection, {"rif": rif})
    if success:
        return {"message": result}
    raise HTTPException(status_code=404, detail=result)

# Endpoint para subir inventario
@app.post("/subir_inventario/")
async def subir_inventario(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel (.xlsx o .xls)")
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        columnas_requeridas = ["codigo", "descripcion", "dpto", "nacional", "laboratorio", "f.v.", "existencia", "precio","descuento1","descuento2","descuento3"]
        if not all(col in df.columns for col in columnas_requeridas):
            raise HTTPException(status_code=400, detail="Faltan columnas requeridas.")

        df = df.rename(columns={
            "codigo": "codigo",
            "descripcion": "descripcion",
            "dpto": "dpto",
            "nacional": "nacional",
            "laboratorio": "laboratorio",
            "f.v.": "fv",
            "existencia": "existencia",
            "precio": "precio",
            "descuento1": "descuento1",
            "descuento2": "descuento2",
            "descuento3": "descuento3",
        })

        df["fv"] = pd.to_datetime(df["fv"], errors="coerce").dt.strftime('%d/%m/%Y')
        # df["cantidad"] = 0
        # df["descuento1"] = 0
        # df["descuento2"] = 0
        df["codigo"] = df["codigo"].astype(str).str.strip()
        productos = df.to_dict(orient="records")

        fecha_subida = datetime.now().strftime("%d-%m-%Y")
        nombre_productos = f"inventario_{fecha_subida}"
        inventario1 = {"nombre_productos":nombre_productos, "inventario": productos}

        inventario_collection.delete_many({})
        inventario_collection.insert_one(inventario1)

        return {"message": f"{len(productos)} productos cargados correctamente dentro de {nombre_productos}."}
    except pd.errors.ExcelFileError:
        raise HTTPException(status_code=400, detail="Archivo Excel no válido.")
    except Exception as e:
        print(f"Error inesperado: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inventario/")
async def obtener_inventario():
    inventario = inventario_collection.find_one(sort=[('_id', -1)])
    print("Respuesta cruda de MongoDB:", inventario)

    if not inventario:
        return JSONResponse(content={"message": "No se encontró inventario"}, status_code=404)

    inventario["_id"] = str(inventario["_id"])


    inventario_list = inventario["inventario"]

    for producto in inventario_list:
        for key, value in producto.items():
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                producto[key] = None  # limpiar NaN

            # Extra: limpiar precios tipo string con coma
            if key == "precio" and isinstance(value, str):
                value = value.replace(",", ".")
                try:
                    producto[key] = float(value)
                except ValueError:
                    producto[key] = 0.0  # Si falla la conversión, poner 0


    return JSONResponse(content={"inventario":jsonable_encoder(inventario_list)})

@app.post("/register/")
async def register(client: Client):
    if clients_collection.find_one({"email": client.email}):
        raise HTTPException(status_code=400, detail="Correo ya registrado")

    hashed_password = get_password_hash(client.password)
    new_client = client.dict()
    new_client["password"] = hashed_password

    result = clients_collection.insert_one(new_client)
    if result.inserted_id:
        return {"message": "Cliente registrado exitosamente"}
    raise HTTPException(status_code=500, detail="Error al registrar el cliente")

@app.post("/login/")
async def login(user: UserLogin):
    db_client = clients_collection.find_one({"email": user.email})
    if not db_client:
        raise HTTPException(status_code=401, detail="Cliente no encontrado")

    if not verify_password(user.password, db_client["password"]):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    access_token = create_access_token(db_client)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register/admin/")
async def register_admin(user: UserAdminRegister):
    if usuarios_admin_collection.find_one({"usuario": user.usuario}):
        raise HTTPException(status_code=400, detail="Usuario ya registrado")

    hashed_password = get_password_hash(user.password)
    new_admin = user.dict()
    new_admin["password"] = hashed_password

    result = usuarios_admin_collection.insert_one(new_admin)
    if result.inserted_id:
        return {"message": "Usuario administrativo registrado exitosamente"}

    raise HTTPException(status_code=500, detail="Error al registrar el usuario administrativo")

@app.get("/modulos/admin/")
async def get_admin_modules():
    config = usuarios_admin_collection.find_one({"_id": "modulos_config"})
    if config and "modulos_disponibles" in config:
        return config["modulos_disponibles"]
    raise HTTPException(status_code=404, detail="No se encontraron módulos disponibles")

@app.post("/login/admin/")
async def admin_login(admin: AdminLogin):
    db_admin = usuarios_admin_collection.find_one({"usuario": admin.usuario})
    if not db_admin:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if not verify_password(admin.password, db_admin["password"]):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    access_token = create_admin_access_token(db_admin)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "modulos": db_admin["modulos"],
        "usuario": db_admin["usuario"]
    }

# Endpoint para obtener la lista de clientes
@app.get("/api/clientes/")
async def obtener_clientes():
    try:
        clientes = list(clients_collection.find({}, {"_id": 1, "email": 1, "rif": 1, "encargado": 1}))
        for cliente in clientes:
            cliente["_id"] = str(cliente["_id"])  # Convertir ObjectId a string
        return JSONResponse(content=clientes, status_code=200)
    except Exception as e:
        print(f"Error al obtener clientes: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener la lista de clientes")

# Endpoint para obtener los detalles de un cliente específico por su RIF
@app.get("/api/clientes/{rif}")
async def obtener_cliente_por_rif(rif: str):
    try:
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

@app.post("/pedidos/")
async def registrar_pedido(resumen: PedidoResumen):
    try:
        pedido = resumen.dict()
        pedido["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pedido["estado"] = "nuevo"

        result = db["PEDIDOS"].insert_one(pedido)
        if result.inserted_id:
            return {
                "message": "Pedido registrado exitosamente",
                "pedido_id": str(result.inserted_id),
                "estado": pedido["estado"],
            }
        else:
            raise HTTPException(status_code=500, detail="Error al registrar el pedido")
    except Exception as e:
        print(f"Error al registrar el pedido: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/obtener_pedidos/")
async def obetener_pedidos():
    try:
        pedidos = list(pedidos_collection.find(
            {}
        ))
        for pedido in pedidos:
            pedido["_id"] = str(pedido["_id"])  # Convertir ObjectId a string

        return JSONResponse(content=pedidos, status_code=200)
    except Exception as e:
        print(f"Error al obtener ventas: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener la lista de pedidos")

@app.post("/pedidos/armados/")
async def registrar_pedido_armado(resumen: PedidoArmado):
    """
    Endpoint para registrar un pedido armado en la colección PEDIDOS_ARMADOS.
    """
    try:
        # Preparar los datos del pedido
        pedido = resumen.dict()
        pedido["fecha_armado"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insertar el pedido en la colección PEDIDOS_ARMADOS
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

@app.put("/pedidos/actualizar_estado/{pedido_id}")
async def actualizar_estado_pedido(pedido_id: str, estado: EstadoPedido):
    """
    Endpoint para actualizar el estado de un pedido en la colección PEDIDOS.
    """
    try:
        # Convertir el ID del pedido a ObjectId
        pedido_object_id = ObjectId(pedido_id)

        # Modify the update logic to preserve `fechainicio` if not explicitly set to null
        update_fields = {"estado": estado.nuevo_estado}
        existing_pedido = db["PEDIDOS"].find_one({"_id": pedido_object_id})
        if existing_pedido and "fechainicio" in existing_pedido:
            update_fields["fechainicio"] = existing_pedido["fechainicio"]

        result = db["PEDIDOS"].update_one(
            {"_id": pedido_object_id},
            {"$set": update_fields}
        )

        if result.modified_count:
            return {"message": f"Estado del pedido actualizado a {estado.nuevo_estado}"}
        else:
            raise HTTPException(status_code=404, detail="Pedido no encontrado o no se realizaron cambios")
    except Exception as e:
        print(f"Error al actualizar el estado del pedido: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.put("/pedidos/actualizar/{id}")
async def actualizar_pedido(id: str, pedido_actualizado: dict):
    """
    Endpoint para actualizar un pedido en la colección PEDIDOS.
    """
    try:
        # Validar que el ID sea un ObjectId válido
        try:
            pedido_object_id = ObjectId(id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="ID inválido")

        # Eliminar el campo '_id' del objeto para evitar modificarlo
        if "_id" in pedido_actualizado:
            del pedido_actualizado["_id"]

        # Actualizar el pedido en la colección
        resultado = db["PEDIDOS"].find_one_and_update(
            {"_id": pedido_object_id},  # Filtro por ID
            {"$set": pedido_actualizado},  # Actualización de los datos
            return_document=True  # Retornar el documento actualizado
        )

        if resultado:
            # Convertir ObjectId a string antes de retornar
            resultado["_id"] = str(resultado["_id"])
            return JSONResponse(content=jsonable_encoder(resultado), status_code=200)
        else:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
    except Exception as error:
        print(f"Error al actualizar el pedido: {error}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar el pedido: {error}")

@app.patch("/pedidos/actualizar_cantidades/{pedido_id}")
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

@app.post("/contacto")
def enviar_contacto(form: ContactForm):
    """
    Recibe el formulario de contacto y lo guarda en la colección 'formularios' de MongoDB.
    """
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

@app.get("/pedidos/por_cliente/{rif}")
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

@app.patch("/pedidos/actualizar_picking/{pedido_id}")
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
        update_fields = {}

        # Siempre crear el objeto picking aunque no venga nada en el form
        update_fields = {f"picking.{k}": v for k, v in picking_data.items()}
        if not update_fields:
            # Si no se envió ningún campo, igual inicializa el objeto picking vacío
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

@app.patch("/pedidos/actualizar_packing/{pedido_id}")
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

@app.patch("/pedidos/actualizar_envio/{pedido_id}")
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

@app.post("/reclamos/cliente")
async def registrar_reclamo_cliente(reclamo: ReclamoCliente):
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

@app.get("/reclamos/cliente/{rif}")
async def obtener_reclamos_cliente(rif: str):
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