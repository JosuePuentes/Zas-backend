from connection import get_collection
from typing import Dict, Any
from bson import ObjectId

def update_one(collection_name: str, id: str, update_data: Dict[str, Any]) -> int:
    collection = get_collection(collection_name)
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return result.modified_count


def update_many(collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
    collection = get_collection(collection_name)
    result = collection.update_many(query, {"$set": update_data})
    return result.modified_count


update_many(
    "PEDIDOS",
    {"estado": "enviado"},
    {"estado": "entregado"}
)