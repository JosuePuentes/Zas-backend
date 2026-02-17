from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv
from fastapi import Request
import os

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

# Configuración de conexión a MongoDB (un solo cluster; varias bases de datos por tenant)
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    MONGO_URI = "mongodb+srv://master:go3DjrOJmczPNDNNz@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)

# Mapa origen (host) -> nombre de base de datos para multi-tenant
# Formato env: "virgen-del-carmen-frontend.vercel.app:VIRGENCARMEN,www.drocolven.com:DROCOLVEN,drocolven.com:DROCOLVEN,localhost:3000:DROCOLVEN"
TENANT_ORIGIN_DB_ENV = os.getenv("TENANT_ORIGIN_DB", "").strip()
DEFAULT_DB = os.getenv("DEFAULT_TENANT_DB", "DROCOLVEN")

_origin_to_db: dict[str, str] = {}
if TENANT_ORIGIN_DB_ENV:
    for part in TENANT_ORIGIN_DB_ENV.split(","):
        part = part.strip()
        if ":" in part:
            host, db_name = part.split(":", 1)
            _origin_to_db[host.strip().lower()] = db_name.strip()

def get_tenant_db_from_origin(origin: str) -> str:
    """Devuelve el nombre de la base de datos según el Origin (o Referer) del request."""
    if not origin:
        return DEFAULT_DB
    # origin puede ser "https://virgen-del-carmen-frontend.vercel.app" o solo el host
    origin = origin.strip().lower()
    if origin.startswith("http://") or origin.startswith("https://"):
        try:
            host = origin.split("//", 1)[1].split("/")[0]
        except IndexError:
            host = origin
    else:
        host = origin
    # Quitar puerto si existe (localhost:3000 -> localhost)
    if ":" in host:
        host = host.split(":")[0]
    return _origin_to_db.get(host, DEFAULT_DB)


def get_db(request: Request) -> Database:
    """Dependency: devuelve la base de datos del tenant según el Origin del request."""
    origin = request.headers.get("origin") or request.headers.get("referer") or ""
    tenant_db = get_tenant_db_from_origin(origin)
    return client[tenant_db]


# Compatibilidad: una base por defecto para imports que no usen Depends(get_db)
db = client[DEFAULT_DB]
collection = db["mi_coleccion"]
inventario_collection = db["INVENTARIO_MAESTRO"]
clients_collection = db["CLIENTES"]
usuarios_admin_collection = db["usuarios_admin"]
ventas_collection = db["VENTAS"]
pedidos_collection = db["PEDIDOS"]
modulos_collection = db["modulos"]
convenios_collection = db["CONVENIOS"]
