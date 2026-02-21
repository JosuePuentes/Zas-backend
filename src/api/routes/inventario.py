# Importa tu modelo Pydantic
from bson import ObjectId

# Endpoint para modificar un producto de inventario maestro
from fastapi import Request, status, Depends
from pymongo.database import Database
from ..database import get_db
from ..auth.auth_utils import verify_admin_token
from typing import List, Optional
# Endpoint para consultar inventario maestro
from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from fastapi.responses import JSONResponse
from ..models.models import ConvenioCarga, Convenio
import math
from fastapi.encoders import jsonable_encoder
import pandas as pd
from io import BytesIO
from datetime import datetime
import traceback
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from utils.inventario_utils import calcular_precio_con_utilidad_40



router = APIRouter()


def _get_admin_from_request(request: Request) -> dict:
    """Exige Authorization: Bearer <admin_token>. Para uso en inventario_maestro."""
    auth = request.headers.get("Authorization") or ""
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta token de administrador")
    return verify_admin_token(auth[7:].strip())


def _normalize_product_for_response(prod: dict) -> dict:
    """Devuelve producto con campos _id, codigo, descripcion, marca, costo, utilidad, precio, existencia, stock_minimo, stock_maximo."""
    raw_id = prod.get("_id", "")
    prod_id = str(raw_id) if raw_id else ""
    costo = prod.get("costo") if "costo" in prod else prod.get("precio_costo")
    if costo is None:
        costo = 0.0
    try:
        costo = float(costo)
    except (TypeError, ValueError):
        costo = 0.0
    precio = prod.get("precio")
    if precio is None:
        precio = 0.0
    try:
        precio = float(precio)
    except (TypeError, ValueError):
        precio = 0.0
    utilidad = prod.get("utilidad")
    if utilidad is None and costo and costo > 0:
        utilidad = round((precio / costo - 1) * 100, 2)
    if utilidad is None:
        utilidad = 0.0
    marca = prod.get("marca") if prod.get("marca") is not None else prod.get("laboratorio", "") or ""
    return {
        "_id": prod_id,
        "id": prod_id,
        "codigo": prod.get("codigo", ""),
        "descripcion": prod.get("descripcion", ""),
        "marca": marca,
        "costo": round(costo, 2),
        "utilidad": round(float(utilidad), 2),
        "precio": round(precio, 2),
        "existencia": int(prod.get("existencia", 0)),
        "stock_minimo": prod.get("stock_minimo"),
        "stock_maximo": prod.get("stock_maximo"),
    }

@router.get("/inventario/")
async def obtener_inventario(db: Database = Depends(get_db)):
    try:
        inventario_collection = db["INVENTARIO_MAESTRO"]
        # Buscar todos los productos en la colección INVENTARIO_MAESTRO
        productos = list(inventario_collection.find({}))
        
        if not productos:
            return JSONResponse(content={"message": "No se encontró inventario"}, status_code=404)
        
        # Procesar cada producto
        inventario_list = []
        for producto in productos:
            producto["_id"] = str(producto["_id"])
            
            # Limpiar valores NaN e infinitos
            for key, value in producto.items():
                if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                    producto[key] = None
                elif key == "precio" and isinstance(value, str):
                    value = value.replace(",", ".")
                    try:
                        producto[key] = float(value)
                    except ValueError:
                        producto[key] = 0.0
            
            inventario_list.append(producto)
        
        return JSONResponse(content={"inventario": jsonable_encoder(inventario_list)})
        
    except Exception as e:
        print(f"Error al obtener inventario: {e}")
        return JSONResponse(content={"message": "Error interno del servidor"}, status_code=500)

@router.get("/inventario_maestro/")
async def obtener_inventario_maestro(request: Request, db: Database = Depends(get_db)):
    """Listar productos. Requiere Authorization: Bearer <admin_token>. Devuelve { productos: [...] } con _id, codigo, descripcion, marca, costo, utilidad, precio, existencia, stock_minimo, stock_maximo."""
    _get_admin_from_request(request)
    coll = db["INVENTARIO_MAESTRO"]
    # Excluir documentos que sean "inventario embebido" (nombre_productos + inventario)
    cursor = coll.find({"codigo": {"$exists": True}})
    productos = []
    for prod in cursor:
        if isinstance(prod.get("_id"), ObjectId):
            prod["_id"] = str(prod["_id"])
        if "fv" in prod and isinstance(prod.get("fv"), float) and math.isnan(prod["fv"]):
            prod["fv"] = None
        productos.append(_normalize_product_for_response(prod))
    return JSONResponse(content={"productos": productos})


@router.post("/inventario_maestro/", status_code=201)
async def crear_producto_maestro(request: Request, body: dict = Body(...), db: Database = Depends(get_db)):
    """
    Crear producto. Requiere Authorization: Bearer <admin_token>.
    Campos: codigo (requerido), descripcion, marca, costo, utilidad, precio, existencia, stock_minimo, stock_maximo.
    Si se envían costo y utilidad, precio se calcula: precio = costo * (1 + utilidad/100). Devuelve el producto creado con _id e id.
    """
    _get_admin_from_request(request)
    codigo = body.get("codigo")
    if not codigo:
        raise HTTPException(status_code=400, detail="El campo codigo es requerido")
    inventario_collection = db["INVENTARIO_MAESTRO"]
    if inventario_collection.find_one({"codigo": str(codigo)}):
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese código")
    costo = body.get("costo")
    utilidad = body.get("utilidad")
    precio = body.get("precio")
    try:
        costo_val = float(costo) if costo is not None else 0.0
    except (TypeError, ValueError):
        costo_val = 0.0
    try:
        utilidad_val = float(utilidad) if utilidad is not None else 0.0
    except (TypeError, ValueError):
        utilidad_val = 0.0
    if costo is not None and utilidad is not None and costo_val > 0:
        precio = costo_val * (1 + utilidad_val / 100)
    if precio is None:
        precio = 0.0
    try:
        precio = float(precio)
    except (TypeError, ValueError):
        precio = 0.0
    producto = {
        "codigo": str(codigo),
        "descripcion": body.get("descripcion", ""),
        "marca": body.get("marca", ""),
        "costo": costo_val,
        "utilidad": utilidad_val,
        "precio": precio,
        "existencia": int(body.get("existencia", 0)),
        "dpto": body.get("dpto", ""),
        "nacional": body.get("nacional", ""),
        "laboratorio": body.get("marca", "") or body.get("laboratorio", ""),
        "fv": body.get("fv", ""),
        "descuento1": float(body.get("descuento1", 0)),
        "descuento2": float(body.get("descuento2", 0)),
        "descuento3": float(body.get("descuento3", 0)),
        "precio_costo": costo_val,
    }
    if "stock_minimo" in body and body["stock_minimo"] is not None:
        producto["stock_minimo"] = int(body["stock_minimo"])
    if "stock_maximo" in body and body["stock_maximo"] is not None:
        producto["stock_maximo"] = int(body["stock_maximo"])
    resultado = inventario_collection.insert_one(producto)
    inserted = inventario_collection.find_one({"_id": resultado.inserted_id})
    inserted["_id"] = str(inserted["_id"])
    inserted["id"] = inserted["_id"]
    return JSONResponse(content=_normalize_product_for_response(inserted), status_code=201)


@router.post("/subir_inventario/")
async def subir_inventario(file: UploadFile = File(...), db: Database = Depends(get_db)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel (.xlsx o .xls)")
    try:
        inventario_collection = db["INVENTARIO_MAESTRO"]
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        columnas_requeridas = ["codigo", "descripcion", "dpto", "nacional", "laboratorio", "f.v.", "existencia", "precio","descuento1","descuento2","descuento3"]
        if not all(col in df.columns for col in columnas_requeridas):
            raise HTTPException(status_code=400, detail="Faltan columnas requeridas.")

        df = df.rename(columns={"f.v.": "fv"})
        # Columnas opcionales para stock mínimo/máximo (acepta Stock_minimo, Stock_maximo, etc.)
        rename_stock = {}
        for col in list(df.columns):
            c = str(col).strip().lower().replace(" ", "_")
            if c in ("stock_minimo", "stockmínimo", "stockminimo"):
                rename_stock[col] = "stock_minimo"
            elif c in ("stock_maximo", "stockmáximo", "stockmaximo"):
                rename_stock[col] = "stock_maximo"
        if rename_stock:
            df = df.rename(columns=rename_stock)

        # Limpieza y transformación de datos
        df["fv"] = pd.to_datetime(df["fv"], errors="coerce").dt.strftime('%d/%m/%Y')
        df["codigo"] = df["codigo"].astype(str).str.strip()
        
        # Reemplaza NaN por None para compatibilidad con JSON/MongoDB
        df = df.where(pd.notna(df), None)
        
        productos = df.to_dict(orient="records")

        # --- INICIO DE CAMBIOS ---
        # Aplicar utilidad del 40% a cada producto
        for producto in productos:
            precio_costo = producto.get("precio")
            if precio_costo is not None:
                try:
                    # Convertir a float si es string
                    if isinstance(precio_costo, str):
                        precio_costo = float(precio_costo.replace(",", "."))
                    elif isinstance(precio_costo, (int, float)):
                        precio_costo = float(precio_costo)
                    else:
                        precio_costo = 0.0
                    
                    # Calcular precio con utilidad del 40%
                    if precio_costo > 0:
                        precio_venta = calcular_precio_con_utilidad_40(precio_costo)
                        producto["precio"] = precio_venta
                        producto["precio_costo"] = precio_costo  # Guardar precio de costo original
                except (ValueError, TypeError):
                    producto["precio"] = 0.0
                    producto["precio_costo"] = 0.0
            # Incluir stock_minimo y stock_maximo si vienen en el Excel
            if "stock_minimo" in producto and producto["stock_minimo"] is not None:
                try:
                    producto["stock_minimo"] = int(float(producto["stock_minimo"]))
                except (ValueError, TypeError):
                    producto["stock_minimo"] = None
            if "stock_maximo" in producto and producto["stock_maximo"] is not None:
                try:
                    producto["stock_maximo"] = int(float(producto["stock_maximo"]))
                except (ValueError, TypeError):
                    producto["stock_maximo"] = None

        # 1. Borra el inventario anterior (esto se mantiene)
        if productos: # Solo borrar si hay nuevos productos para cargar
            inventario_collection.delete_many({})
        else:
            return {"message": "El archivo no contiene productos para cargar."}

        # 2. Inserta cada producto como un documento individual
        #    La variable 'productos' ya es una lista de diccionarios, perfecta para insert_many.
        resultado = inventario_collection.insert_many(productos)

        # --- FIN DE CAMBIOS ---

        # 3. Actualiza el mensaje de éxito
        num_insertados = len(resultado.inserted_ids)
        return {"message": f"{num_insertados} productos cargados correctamente como documentos individuales."}
        
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Archivo Excel no válido o corrupto.")
    except Exception as e:
        print(f"Error inesperado: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ocurrió un error inesperado en el servidor: {e}")


@router.post("/convenios/cargar", tags=["Convenios"])
async def cargar_convenio(convenio: ConvenioCarga, db: Database = Depends(get_db)):
    """
    Recibe los datos de un nuevo convenio y lo carga en la base de datos.
    """
    try:
        convenios_collection = db["CONVENIOS"]
        # Convierte el modelo de Pydantic a un diccionario de Python
        # para poder insertarlo en MongoDB.
        datos_convenio = convenio.model_dump()

        # Opcional: Añadir un campo con la fecha de carga del documento
        datos_convenio["fecha_carga_utc"] = datetime.utcnow()

        # Inserta el nuevo documento en la colección 'CONVENIOS'
        resultado = convenios_collection.insert_one(datos_convenio)
        
        # Confirma que la inserción fue exitosa
        if not resultado.acknowledged:
            # Esta línea se ha revisado para asegurar que la cadena de texto esté completa y limpia.
            raise HTTPException(status_code=500, detail="El convenio no pudo ser guardado en la base de datos.")

        # Devuelve una respuesta de éxito
        return JSONResponse(
            status_code=201, # 201 Created es el código apropiado para un POST exitoso
            content={
                "message": "Convenio cargado exitosamente.",
                "convenio_id": str(resultado.inserted_id)
            }
        )

    except Exception as e:
        print(f"Error inesperado al cargar convenio: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Ocurrió un error inesperado en el servidor: {e}"
        )


@router.post("/subir_inventario2/")
async def subir_inventario2(file: UploadFile = File(...), db: Database = Depends(get_db)): # Se renombró la función para evitar duplicados
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel (.xlsx o .xls)")
    try:
        inventario_collection = db["INVENTARIO_MAESTRO"]
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        columnas_requeridas = ["codigo", "descripcion", "dpto", "nacional", "laboratorio", "f.v.", "existencia", "precio","descuento1","descuento2","descuento3"]
        if not all(col in df.columns for col in columnas_requeridas):
            raise HTTPException(status_code=400, detail="Faltan columnas requeridas.")

        df = df.rename(columns={
            "codigo": "codigo",
            "descripcion": "descripcion",
            "dpto": "dpto",
            "nacional": "nacional",
            "laboratorio": "laboratorio",
            "f.v.": "fv",
            "existencia": "existencia",
            "precio": "precio",
            "descuento1": "descuento1",
            "descuento2": "descuento2",
            "descuento3": "descuento3",
        })

        df["fv"] = pd.to_datetime(df["fv"], errors="coerce").dt.strftime('%d/%m/%Y')
        # df["cantidad"] = 0
        # df["descuento1"] = 0
        # df["descuento2"] = 0
        df["codigo"] = df["codigo"].astype(str).str.strip()
        productos = df.to_dict(orient="records")

        fecha_subida = datetime.now().strftime("%d-%m-%Y")
        nombre_productos = f"inventario_{fecha_subida}"
        inventario1 = {"nombre_productos":nombre_productos, "inventario": productos}

        inventario_collection.delete_many({})
        inventario_collection.insert_one(inventario1)

        return {"message": f"{len(productos)} productos cargados correctamente dentro de {nombre_productos}."}
    except pd.errors.ClosedFileError:
        raise HTTPException(status_code=400, detail="Archivo Excel no válido.")
    except Exception as e:
        print(f"Error inesperado: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para obtener un producto completo de inventario maestro por ObjectId
@router.get("/inventario_maestro/{id}")
async def obtener_producto_maestro(request: Request, id: str, db: Database = Depends(get_db)):
    _get_admin_from_request(request)
    prod = db["INVENTARIO_MAESTRO"].find_one({"_id": ObjectId(id)})
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    prod["_id"] = str(prod["_id"])
    return JSONResponse(content=_normalize_product_for_response(prod))

@router.put("/inventario_maestro/{id}")
async def modificar_inventario_maestro(request: Request, id: str, body: dict = Body(...), db: Database = Depends(get_db)):
    """Actualizar producto. Requiere Authorization: Bearer <admin_token>. Acepta marca, costo, utilidad, precio, existencia, stock_minimo, stock_maximo, etc."""
    _get_admin_from_request(request)
    campos_permitidos = {"codigo", "descripcion", "existencia", "precio", "dpto", "nacional", "laboratorio", "fv", "descuento1", "descuento2", "descuento3", "stock_minimo", "stock_maximo", "marca", "costo", "utilidad", "precio_costo"}
    update_data = {k: v for k, v in body.items() if k in campos_permitidos}
    if "costo" in update_data and "utilidad" in update_data:
        try:
            c, u = float(update_data["costo"]), float(update_data["utilidad"])
            if c > 0:
                update_data["precio"] = c * (1 + u / 100)
                update_data["precio_costo"] = c
        except (TypeError, ValueError):
            pass
    result = db["INVENTARIO_MAESTRO"].update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    updated = db["INVENTARIO_MAESTRO"].find_one({"_id": ObjectId(id)})
    updated["_id"] = str(updated["_id"])
    return JSONResponse(content=_normalize_product_for_response(updated))

@router.get(
    "/convenios", 
    response_model=List[Convenio], 
    summary="Obtener todos los convenios"
)
async def get_all_convenios(db: Database = Depends(get_db)):
    """
    Obtiene una lista de todos los convenios almacenados en la base de datos.
    El modelo de respuesta se encarga de la correcta serialización.
    """
    try:
        convenios_collection = db["CONVENIOS"]
        convenios_list = list(convenios_collection.find({}))
        # Simplemente retornas la lista, FastAPI y Pydantic hacen el resto.
        return convenios_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al consultar los convenios: {e}"
        )


# ===============================================
# ENDPOINTS CON UTILIDAD DEL 40% Y DESCUENTO DE INVENTARIO
# ===============================================

@router.post("/inventarios/upload-excel")
async def upload_excel_inventario(file: UploadFile = File(...), db: Database = Depends(get_db)):
    """
    Endpoint para subir inventario desde Excel con aplicación automática de utilidad del 40%.
    Este endpoint es un alias de /subir_inventario/ con la misma funcionalidad.
    """
    return await subir_inventario(file, db)


@router.post("/inventarios/cargar-existencia")
async def cargar_existencia_inventario(body: dict = Body(...), db: Database = Depends(get_db)):
    """
    Endpoint para cargar existencia de productos en inventario.
    Aplica utilidad del 40% al precio si se proporciona precio_costo.
    
    Body esperado:
    {
        "productos": [
            {
                "codigo": "string",
                "existencia": int,
                "precio_costo": float (opcional),
                "precio": float (opcional, se calculará si se proporciona precio_costo)
            }
        ]
    }
    """
    try:
        productos = body.get("productos", [])
        
        if not productos:
            raise HTTPException(status_code=400, detail="No se proporcionaron productos")
        
        resultados = []
        productos_actualizados = []
        
        for producto_data in productos:
            codigo = producto_data.get("codigo")
            existencia = producto_data.get("existencia")
            precio_costo = producto_data.get("precio_costo")
            precio = producto_data.get("precio")
            
            if not codigo:
                resultados.append({
                    "codigo": codigo,
                    "error": "Código de producto requerido"
                })
                continue
            
            # Buscar producto existente
            producto = db["INVENTARIO_MAESTRO"].find_one({"codigo": str(codigo)})
            
            if not producto:
                resultados.append({
                    "codigo": codigo,
                    "error": "Producto no encontrado"
                })
                continue
            
            # Actualizar existencia
            update_data = {}
            if existencia is not None:
                update_data["existencia"] = int(existencia)
            
            # Calcular precio con utilidad del 40% si se proporciona precio_costo
            if precio_costo is not None:
                try:
                    precio_costo_float = float(precio_costo)
                    if precio_costo_float > 0:
                        precio_calculado = calcular_precio_con_utilidad_40(precio_costo_float)
                        update_data["precio"] = precio_calculado
                        update_data["precio_costo"] = precio_costo_float
                except (ValueError, TypeError):
                    resultados.append({
                        "codigo": codigo,
                        "error": "Precio de costo inválido"
                    })
                    continue
            elif precio is not None:
                # Si se proporciona precio directamente, usarlo
                try:
                    update_data["precio"] = float(precio)
                except (ValueError, TypeError):
                    resultados.append({
                        "codigo": codigo,
                        "error": "Precio inválido"
                    })
                    continue
            
            if update_data:
                db["INVENTARIO_MAESTRO"].update_one(
                    {"codigo": str(codigo)},
                    {"$set": update_data}
                )
                productos_actualizados.append({
                    "codigo": codigo,
                    "actualizado": True,
                    "campos": list(update_data.keys())
                })
            else:
                resultados.append({
                    "codigo": codigo,
                    "error": "No se proporcionaron datos para actualizar"
                })
        
        return {
            "message": f"Procesados {len(productos)} productos",
            "actualizados": len(productos_actualizados),
            "detalles": productos_actualizados,
            "errores": [r for r in resultados if "error" in r]
        }
        
    except Exception as e:
        print(f"Error al cargar existencia: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")


@router.post("/inventarios/{inventario_id}/items")
async def agregar_items_inventario(inventario_id: str, body: dict = Body(...), db: Database = Depends(get_db)):
    """
    Endpoint para agregar items a un inventario específico.
    Aplica utilidad del 40% al precio si se proporciona precio_costo.
    
    Body esperado:
    {
        "items": [
            {
                "codigo": "string",
                "descripcion": "string",
                "existencia": int,
                "precio_costo": float (opcional),
                "precio": float (opcional),
                "dpto": "string" (opcional),
                "nacional": "string" (opcional),
                "laboratorio": "string" (opcional),
                "fv": "string" (opcional),
                "descuento1": float (opcional),
                "descuento2": float (opcional),
                "descuento3": float (opcional)
            }
        ]
    }
    """
    try:
        items = body.get("items", [])
        
        if not items:
            raise HTTPException(status_code=400, detail="No se proporcionaron items")
        
        resultados = []
        items_insertados = []
        
        for item_data in items:
            codigo = item_data.get("codigo")
            if not codigo:
                resultados.append({
                    "codigo": None,
                    "error": "Código de producto requerido"
                })
                continue
            
            # Preparar datos del producto
            producto = {
                "codigo": str(codigo),
                "descripcion": item_data.get("descripcion", ""),
                "existencia": int(item_data.get("existencia", 0)),
                "dpto": item_data.get("dpto", ""),
                "nacional": item_data.get("nacional", ""),
                "laboratorio": item_data.get("laboratorio", ""),
                "fv": item_data.get("fv", ""),
                "descuento1": item_data.get("descuento1", 0.0),
                "descuento2": item_data.get("descuento2", 0.0),
                "descuento3": item_data.get("descuento3", 0.0),
            }
            if "stock_minimo" in item_data and item_data["stock_minimo"] is not None:
                producto["stock_minimo"] = int(item_data["stock_minimo"])
            if "stock_maximo" in item_data and item_data["stock_maximo"] is not None:
                producto["stock_maximo"] = int(item_data["stock_maximo"])
            
            # Calcular precio con utilidad del 40% si se proporciona precio_costo
            precio_costo = item_data.get("precio_costo")
            precio = item_data.get("precio")
            
            if precio_costo is not None:
                try:
                    precio_costo_float = float(precio_costo)
                    if precio_costo_float > 0:
                        precio_calculado = calcular_precio_con_utilidad_40(precio_costo_float)
                        producto["precio"] = precio_calculado
                        producto["precio_costo"] = precio_costo_float
                    else:
                        producto["precio"] = 0.0
                        producto["precio_costo"] = 0.0
                except (ValueError, TypeError):
                    resultados.append({
                        "codigo": codigo,
                        "error": "Precio de costo inválido"
                    })
                    continue
            elif precio is not None:
                try:
                    producto["precio"] = float(precio)
                except (ValueError, TypeError):
                    resultados.append({
                        "codigo": codigo,
                        "error": "Precio inválido"
                    })
                    continue
            else:
                producto["precio"] = 0.0
            
            # Verificar si el producto ya existe
            producto_existente = db["INVENTARIO_MAESTRO"].find_one({"codigo": str(codigo)})
            
            if producto_existente:
                # Actualizar producto existente
                db["INVENTARIO_MAESTRO"].update_one(
                    {"codigo": str(codigo)},
                    {"$set": producto}
                )
                items_insertados.append({
                    "codigo": codigo,
                    "accion": "actualizado"
                })
            else:
                # Insertar nuevo producto
                db["INVENTARIO_MAESTRO"].insert_one(producto)
                items_insertados.append({
                    "codigo": codigo,
                    "accion": "insertado"
                })
        
        return {
            "message": f"Procesados {len(items)} items",
            "items_procesados": len(items_insertados),
            "detalles": items_insertados,
            "errores": [r for r in resultados if "error" in r]
        }
        
    except Exception as e:
        print(f"Error al agregar items: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")
