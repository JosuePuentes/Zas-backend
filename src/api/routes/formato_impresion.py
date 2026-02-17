from fastapi import APIRouter, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.database import Database
from ..database import get_db
from ..models.formato_impresion import FormatoImpresion, FormatoImpresionCreate, FormatoImpresionUpdate, FacturaPreliminarData
from datetime import datetime
from typing import Optional, List
import json

# Función helper para serializar fechas
def serializar_formato(formato):
    """Convertir formato de MongoDB a formato JSON serializable."""
    if not formato:
        return None
    
    # Convertir ObjectId a string
    if "_id" in formato:
        formato["_id"] = str(formato["_id"])
    
    # Convertir datetime a string para JSON
    if "fecha_creacion" in formato and formato["fecha_creacion"]:
        formato["fecha_creacion"] = formato["fecha_creacion"].strftime("%Y-%m-%d %H:%M:%S")
    
    if "fecha_actualizacion" in formato and formato["fecha_actualizacion"]:
        formato["fecha_actualizacion"] = formato["fecha_actualizacion"].strftime("%Y-%m-%d %H:%M:%S")
    
    return formato

router = APIRouter()

@router.get("/")
async def obtener_formatos(
    activo: Optional[bool] = Query(default=None, description="Filtrar por estado activo"),
    tipo: Optional[str] = Query(default=None, description="Filtrar por tipo de formato"),
    db: Database = Depends(get_db),
):
    """
    Obtener todos los formatos de impresión con filtros opcionales.
    """
    try:
        formatos_collection = db["formatos_impresion"]
        # Construir filtro de consulta
        query_filter = {}
        
        if activo is not None:
            query_filter["activo"] = activo
        
        if tipo:
            query_filter["tipo"] = tipo
        
        # Obtener formatos
        formatos = list(formatos_collection.find(query_filter))
        
        # Serializar cada formato
        formatos_serializados = [serializar_formato(formato) for formato in formatos]
        
        return JSONResponse(
            content={
                "formatos": formatos_serializados,
                "total": len(formatos_serializados)
            },
            status_code=200
        )
        
    except Exception as e:
        print(f"Error al obtener formatos de impresión: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/{tipo}")
async def obtener_formato_por_tipo(tipo: str, db: Database = Depends(get_db)):
    """
    Obtener formato específico por tipo (ej: "factura_preliminar").
    """
    try:
        formatos_collection = db["formatos_impresion"]
        formato = formatos_collection.find_one({"tipo": tipo, "activo": True})
        
        if not formato:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró formato activo para el tipo '{tipo}'"
            )
        
        # Serializar formato
        formato_serializado = serializar_formato(formato)
        
        return JSONResponse(content=formato_serializado, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al obtener formato por tipo: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/")
async def crear_formato(formato_data: FormatoImpresionCreate, db: Database = Depends(get_db)):
    """
    Crear nuevo formato de impresión.
    """
    try:
        formatos_collection = db["formatos_impresion"]
        # Verificar que no exista un formato activo del mismo tipo
        formato_existente = formatos_collection.find_one({
            "tipo": formato_data.tipo,
            "activo": True
        })
        
        if formato_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un formato activo para el tipo '{formato_data.tipo}'"
            )
        
        # Crear el formato
        formato_dict = formato_data.dict()
        formato_dict["fecha_creacion"] = datetime.now()
        formato_dict["fecha_actualizacion"] = datetime.now()
        
        # Usar valores por defecto si no se proporcionan
        if not formato_dict.get("datos_empresa"):
            formato_dict["datos_empresa"] = {
                "nombre": "FARMA AMERICA (DANIEL)",
                "rif": "J-12345678-9",
                "telefono": "+58 212 123-4567",
                "email": "info@farmaamerica.com",
                "web": "www.farmaamerica.com",
                "direccion": "Av. Principal, Edificio Farma, Piso 3, Caracas, Venezuela",
                "ciudad": "Caracas",
                "estado": "Distrito Capital",
                "codigo_postal": "1010"
            }
        
        if not formato_dict.get("configuracion_diseno"):
            formato_dict["configuracion_diseno"] = {
                "mostrar_logo": True,
                "mostrar_direccion": True,
                "mostrar_telefono": True,
                "mostrar_email": True,
                "mostrar_web": False,
                "color_principal": "#1e40af",
                "color_secundario": "#64748b",
                "fuente_titulo": "bold",
                "fuente_texto": "normal",
                "tamaño_fuente": "12px",
                "espaciado": "normal",
                "margen_superior": "20px",
                "margen_inferior": "20px",
                "margen_izquierdo": "20px",
                "margen_derecho": "20px"
            }
        
        if not formato_dict.get("campos_dinamicos"):
            formato_dict["campos_dinamicos"] = {
                "mostrar_fecha": True,
                "mostrar_numero_factura": True,
                "mostrar_cliente": True,
                "mostrar_productos": True,
                "mostrar_totales": True,
                "mostrar_observaciones": True,
                "formato_fecha": "DD/MM/YYYY",
                "formato_moneda": "Bs.",
                "decimales": 2
            }
        
        # Insertar en la base de datos
        result = formatos_collection.insert_one(formato_dict)
        
        if result.inserted_id:
            # Obtener el formato creado
            formato_creado = formatos_collection.find_one({"_id": result.inserted_id})
            formato_serializado = serializar_formato(formato_creado)
            
            return JSONResponse(
                content={
                    "message": f"Formato '{formato_data.tipo}' creado exitosamente",
                    "formato": formato_serializado
                },
                status_code=201
            )
        else:
            raise HTTPException(status_code=500, detail="Error al crear el formato")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al crear formato: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/{tipo}")
async def actualizar_formato(tipo: str, formato_data: FormatoImpresionUpdate, db: Database = Depends(get_db)):
    """
    Actualizar formato específico por tipo.
    """
    try:
        formatos_collection = db["formatos_impresion"]
        # Buscar el formato existente
        formato_existente = formatos_collection.find_one({"tipo": tipo})
        
        if not formato_existente:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró formato para el tipo '{tipo}'"
            )
        
        # Preparar datos de actualización
        update_data = {}
        
        if formato_data.datos_empresa is not None:
            update_data["datos_empresa"] = formato_data.datos_empresa
        
        if formato_data.configuracion_diseno is not None:
            update_data["configuracion_diseno"] = formato_data.configuracion_diseno
        
        if formato_data.plantilla_html is not None:
            update_data["plantilla_html"] = formato_data.plantilla_html
        
        if formato_data.campos_dinamicos is not None:
            update_data["campos_dinamicos"] = formato_data.campos_dinamicos
        
        if formato_data.activo is not None:
            update_data["activo"] = formato_data.activo
        
        # Siempre actualizar fecha y usuario
        update_data["fecha_actualizacion"] = datetime.now()
        if formato_data.usuario_actualizacion:
            update_data["usuario_actualizacion"] = formato_data.usuario_actualizacion
        
        # Actualizar en la base de datos
        result = formatos_collection.update_one(
            {"tipo": tipo},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            # Obtener el formato actualizado
            formato_actualizado = formatos_collection.find_one({"tipo": tipo})
            formato_serializado = serializar_formato(formato_actualizado)
            
            return JSONResponse(
                content={
                    "message": f"Formato '{tipo}' actualizado exitosamente",
                    "formato": formato_serializado
                },
                status_code=200
            )
        else:
            raise HTTPException(status_code=500, detail="No se pudo actualizar el formato")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar formato: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/{tipo}")
async def desactivar_formato(tipo: str, db: Database = Depends(get_db)):
    """
    Desactivar formato específico (soft delete).
    """
    try:
        formatos_collection = db["formatos_impresion"]
        # Buscar el formato existente
        formato_existente = formatos_collection.find_one({"tipo": tipo})
        
        if not formato_existente:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró formato para el tipo '{tipo}'"
            )
        
        # Desactivar el formato
        result = formatos_collection.update_one(
            {"tipo": tipo},
            {"$set": {
                "activo": False,
                "fecha_actualizacion": datetime.now()
            }}
        )
        
        if result.modified_count > 0:
            return JSONResponse(
                content={
                    "message": f"Formato '{tipo}' desactivado exitosamente"
                },
                status_code=200
            )
        else:
            raise HTTPException(status_code=500, detail="No se pudo desactivar el formato")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al desactivar formato: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/id/{id}")
async def eliminar_formato_por_id(id: str, db: Database = Depends(get_db)):
    """
    Eliminar formato específico por ID (hard delete).
    """
    try:
        formatos_collection = db["formatos_impresion"]
        from bson import ObjectId
        
        # Convertir string a ObjectId
        try:
            object_id = ObjectId(id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID de formato inválido")
        
        # Buscar el formato existente
        formato_existente = formatos_collection.find_one({"_id": object_id})
        
        if not formato_existente:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró formato con ID '{id}'"
            )
        
        # Eliminar el formato
        result = formatos_collection.delete_one({"_id": object_id})
        
        if result.deleted_count > 0:
            return JSONResponse(
                content={
                    "message": f"Formato con ID '{id}' eliminado exitosamente"
                },
                status_code=200
            )
        else:
            raise HTTPException(status_code=500, detail="No se pudo eliminar el formato")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al eliminar formato por ID: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/{tipo}/preview")
async def preview_formato(tipo: str, db: Database = Depends(get_db)):
    """
    Obtener preview del formato con datos de ejemplo.
    """
    try:
        formatos_collection = db["formatos_impresion"]
        formato = formatos_collection.find_one({"tipo": tipo, "activo": True})
        
        if not formato:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró formato activo para el tipo '{tipo}'"
            )
        
        # Generar HTML de preview con datos de ejemplo
        html_preview = generar_html_preview(formato)
        
        return JSONResponse(
            content={
                "tipo": tipo,
                "html_preview": html_preview,
                "datos_empresa": formato["datos_empresa"],
                "configuracion_diseno": formato["configuracion_diseno"]
            },
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al generar preview: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

def generar_html_preview(formato: dict) -> str:
    """
    Generar HTML de preview con datos de ejemplo.
    """
    datos_empresa = formato["datos_empresa"]
    config = formato["configuracion_diseno"]
    
    # Datos de ejemplo para preview
    datos_ejemplo = {
        "numero_factura": "FAC-2025-001",
        "fecha": "23/01/2025",
        "cliente": {
            "nombre": "Cliente Ejemplo",
            "rif": "J-98765432-1",
            "direccion": "Av. Ejemplo, Edificio Test, Caracas"
        },
        "productos": [
            {"nombre": "Producto A", "cantidad": 2, "precio": 25.50, "total": 51.00},
            {"nombre": "Producto B", "cantidad": 1, "precio": 15.75, "total": 15.75}
        ],
        "subtotal": 66.75,
        "iva": 10.68,
        "total": 77.43,
        "observaciones": "Pedido de ejemplo para preview"
    }
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Preview - {formato['tipo']}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: {config.get('tamaño_fuente', '12px')};
                margin: {config.get('margen_superior', '20px')} {config.get('margen_derecho', '20px')} {config.get('margen_inferior', '20px')} {config.get('margen_izquierdo', '20px')};
                color: {config.get('color_secundario', '#64748b')};
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid {config.get('color_principal', '#1e40af')};
                padding-bottom: 20px;
            }}
            .empresa-nombre {{
                font-size: 24px;
                font-weight: {config.get('fuente_titulo', 'bold')};
                color: {config.get('color_principal', '#1e40af')};
                margin-bottom: 10px;
            }}
            .empresa-info {{
                font-size: 14px;
                line-height: 1.4;
            }}
            .factura-info {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 30px;
            }}
            .cliente-info {{
                margin-bottom: 30px;
            }}
            .productos-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .productos-table th,
            .productos-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .productos-table th {{
                background-color: {config.get('color_principal', '#1e40af')};
                color: white;
            }}
            .totales {{
                text-align: right;
                margin-top: 20px;
            }}
            .total-final {{
                font-size: 18px;
                font-weight: bold;
                color: {config.get('color_principal', '#1e40af')};
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="empresa-nombre">{datos_empresa.get('nombre', 'Empresa')}</div>
            <div class="empresa-info">
                {f"<div>RIF: {datos_empresa.get('rif', '')}</div>" if config.get('mostrar_rif', True) else ""}
                {f"<div>{datos_empresa.get('direccion', '')}</div>" if config.get('mostrar_direccion', True) else ""}
                {f"<div>{datos_empresa.get('telefono', '')}</div>" if config.get('mostrar_telefono', True) else ""}
                {f"<div>{datos_empresa.get('email', '')}</div>" if config.get('mostrar_email', True) else ""}
            </div>
        </div>
        
        <div class="factura-info">
            <div>
                <strong>Factura:</strong> {datos_ejemplo['numero_factura']}<br>
                <strong>Fecha:</strong> {datos_ejemplo['fecha']}
            </div>
        </div>
        
        <div class="cliente-info">
            <h3>Cliente:</h3>
            <div><strong>Nombre:</strong> {datos_ejemplo['cliente']['nombre']}</div>
            <div><strong>RIF:</strong> {datos_ejemplo['cliente']['rif']}</div>
            <div><strong>Dirección:</strong> {datos_ejemplo['cliente']['direccion']}</div>
        </div>
        
        <table class="productos-table">
            <thead>
                <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td>{p['nombre']}</td><td>{p['cantidad']}</td><td>{p['precio']}</td><td>{p['total']}</td></tr>" for p in datos_ejemplo['productos']])}
            </tbody>
        </table>
        
        <div class="totales">
            <div>Subtotal: {datos_ejemplo['subtotal']}</div>
            <div>IVA (16%): {datos_ejemplo['iva']}</div>
            <div class="total-final">Total: {datos_ejemplo['total']}</div>
        </div>
        
        {f"<div style='margin-top: 30px;'><strong>Observaciones:</strong> {datos_ejemplo['observaciones']}</div>" if config.get('mostrar_observaciones', True) else ""}
    </body>
    </html>
    """
    
    return html

