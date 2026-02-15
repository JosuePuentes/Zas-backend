from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

# Configuración de conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI")

# Si no se encuentra MONGO_URI en variables de entorno, usar la correcta directamente
if not MONGO_URI:
    MONGO_URI = "mongodb+srv://master:go3DjrOJmczPNDNNz@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client["DROCOLVEN"]

collection = db["mi_coleccion"]
inventario_collection = db["INVENTARIO_MAESTRO"]
clients_collection = db["CLIENTES"]
usuarios_admin_collection = db["usuarios_admin"]
ventas_collection = db["VENTAS"]
pedidos_collection = db["PEDIDOS"]
modulos_collection = db["modulos"]
convenios_collection = db["CONVENIOS"]