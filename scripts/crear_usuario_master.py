"""
Script para crear el usuario administrativo 'master' en las bases DROCOLVEN y VIRGENCARMEN.
Ejecutar desde la raíz del proyecto:  python scripts/crear_usuario_master.py

Requisitos: .env en la raíz con MONGO_URI, o exportar MONGO_URI en la terminal.
"""
import os
import sys

# Añadir la raíz del proyecto al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from pymongo import MongoClient
from passlib.context import CryptContext

# Cargar .env desde la raíz del proyecto
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print("ERROR: No hay MONGO_URI. Crea un archivo .env en la raíz con MONGO_URI=tu_cadena")
    sys.exit(1)

USUARIO = "master"
PASSWORD_PLAIN = "Holaboba1."
ROL = "master"
MODULOS = ["solicitudes_clientes", "pedidos", "inventario", "clientes"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hash = pwd_context.hash(PASSWORD_PLAIN)

client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
bases = ["DROCOLVEN", "VIRGENCARMEN"]

for nombre_db in bases:
    db = client[nombre_db]
    col = db["usuarios_admin"]
    if col.find_one({"usuario": USUARIO}):
        print(f"  [{nombre_db}] Usuario 'master' ya existe, se omite.")
        continue
    col.insert_one({
        "usuario": USUARIO,
        "password": password_hash,
        "rol": ROL,
        "modulos": MODULOS,
    })
    print(f"  [{nombre_db}] Usuario 'master' creado correctamente.")

print("Listo. Puedes entrar al panel admin con usuario 'master' y tu contraseña en ambos frontends.")
