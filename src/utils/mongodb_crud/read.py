from .connection import get_collection
from typing import Dict, Any, Optional
from bson import ObjectId

def find_one(collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    collection = get_collection(collection_name)
    return collection.find_one(query)


def find_by_id(collection_name: str, id: str) -> Optional[Dict[str, Any]]:
    collection = get_collection(collection_name)
    return collection.find_one({"_id": ObjectId(id)})


def find_many(collection_name: str, query: Dict[str, Any] = {}) -> list[Dict[str, Any]]:
    collection = get_collection(collection_name)
    return list(collection.find(query))
