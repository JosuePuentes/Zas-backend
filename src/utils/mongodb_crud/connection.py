import os
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Any

MONGO_URI ="mongodb+srv://master:30780142@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
if not MONGO_URI:
    raise RuntimeError("La variable de entorno MONGO_URI no está definida.")

def get_db(db_name: str = "DROCOLVEN") -> Any:
    client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
    return client[db_name]

def get_collection(collection_name: str, db_name: str = "DROCOLVEN") -> Collection:
    db = get_db(db_name)
    return db[collection_name]
