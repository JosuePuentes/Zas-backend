from connection import get_collection
from typing import Dict, Any

def insert_one(collection_name: str, data: Dict[str, Any]) -> str:
    collection = get_collection(collection_name)
    result = collection.insert_one(data)
    return str(result.inserted_id)


def insert_many(collection_name: str, data_list: list[Dict[str, Any]]) -> list[str]:
    collection = get_collection(collection_name)
    result = collection.insert_many(data_list)
    return [str(_id) for _id in result.inserted_ids]


ids = insert_many("modulos", [
  {"name": "picking"},
  {"name": "packing"},
  {"name": "envio"},
])
