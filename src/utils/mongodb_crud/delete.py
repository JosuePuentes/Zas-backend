from .connection import get_collection
from typing import Dict, Any
from bson import ObjectId

def delete_one(collection_name: str, id: str) -> int:
    collection = get_collection(collection_name)
    result = collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count


def delete_many(collection_name: str, query: Dict[str, Any]) -> int:
    collection = get_collection(collection_name)
    result = collection.delete_many(query)
    return result.deleted_count
