import os
from pymongo import MongoClient, errors

MONGO_URI = "mongodb+srv://master:30780142@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
if not MONGO_URI:
    raise RuntimeError("La variable de entorno MONGO_URI no está definida.")

try:
    client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
    db = client["DROCOLVEN"]

    # Leer el documento único de la colección INVENTARIO
    doc = db["INVENTARIO"].find_one()
    if not doc or "inventario" not in doc:
        print("No se encontró el campo 'inventario' en la colección.")
    else:
        productos = doc["inventario"]
        if productos:
            # Insertar todos los productos en la colección INVENTARIO_MAESTRO
            result = db["INVENTARIO_MAESTRO"].insert_many(productos)
            print(f"Insertados {len(result.inserted_ids)} productos en INVENTARIO_MAESTRO.")
        else:
            print("No hay productos para insertar.")
except errors.PyMongoError as e:
    print(f"Error de conexión o inserción: {e}")