"""
Control de fallas: productos con cantidad_pedida > cantidad_encontrada.
GET /fallas/ – listar; opcional ?pedido_id=...
PATCH /fallas/{id} – actualizar proveedor_id y precio_venta por item (id = pedido_id o item id según modelo).
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from pymongo.database import Database
from ..database import get_db
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class FallaUpdate(BaseModel):
    proveedor_id: Optional[str] = None
    precio_venta: Optional[float] = None


@router.get("/fallas/")
async def listar_fallas(
    pedido_id: Optional[str] = None,
    db: Database = Depends(get_db),
):
    """
    Listar productos faltantes (cantidad_pedida > cantidad_encontrada).
    Cada item: pedido_id, codigo, descripcion, cantidad_pedida, cantidad_encontrada, proveedor_id, proveedor_empresa, precio_venta.
    Query opcional: ?pedido_id=... para filtrar por pedido.
    """
    try:
        pedidos_collection = db["PEDIDOS"]
        query = {}
        if pedido_id:
            from bson import ObjectId
            from bson.errors import InvalidId
            try:
                query["_id"] = ObjectId(pedido_id)
            except InvalidId:
                query["_id"] = pedido_id
        pedidos = list(pedidos_collection.find(query))
        items = []
        for ped in pedidos:
            pid = str(ped["_id"])
            productos = ped.get("productos") or []
            for i, p in enumerate(productos):
                qty_pedida = int(p.get("cantidad_pedida", 0))
                qty_encontrada = int(p.get("cantidad_encontrada", 0))
                if qty_pedida > qty_encontrada:
                    item = {
                        "pedido_id": pid,
                        "item_index": i,
                        "codigo": p.get("codigo", ""),
                        "descripcion": p.get("descripcion", ""),
                        "cantidad_pedida": qty_pedida,
                        "cantidad_encontrada": qty_encontrada,
                        "proveedor_id": p.get("proveedor_id"),
                        "proveedor_empresa": p.get("proveedor_empresa"),
                        "precio_venta": p.get("precio_venta"),
                    }
                    items.append(item)
        return JSONResponse(content=items, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/fallas/{pedido_id}")
async def actualizar_falla(
    pedido_id: str,
    body: FallaUpdate,
    item_index: Optional[int] = Query(None, description="Índice del producto en el array productos"),
    db: Database = Depends(get_db),
):
    """
    Actualizar proveedor_id y precio_venta de un item faltante.
    Body: proveedor_id?, precio_venta?. Si hay varios items faltantes en el pedido, usar item_index (query) para indicar cuál.
    """
    from bson import ObjectId
    from bson.errors import InvalidId
    try:
        oid = ObjectId(pedido_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
    pedidos_collection = db["PEDIDOS"]
    ped = pedidos_collection.find_one({"_id": oid})
    if not ped:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    productos = ped.get("productos") or []
    if item_index is None:
        for i, p in enumerate(productos):
            if int(p.get("cantidad_pedida", 0)) > int(p.get("cantidad_encontrada", 0)):
                item_index = i
                break
        if item_index is None:
            raise HTTPException(status_code=404, detail="No hay items faltantes en este pedido")
    if item_index < 0 or item_index >= len(productos):
        raise HTTPException(status_code=400, detail="Índice de producto inválido")
    update = {}
    if body.proveedor_id is not None:
        update[f"productos.{item_index}.proveedor_id"] = body.proveedor_id
    if body.precio_venta is not None:
        update[f"productos.{item_index}.precio_venta"] = body.precio_venta
    if not update:
        return {"message": "Nada que actualizar"}
    pedidos_collection.update_one({"_id": oid}, {"$set": update})
    return {"message": "Falla actualizada"}
