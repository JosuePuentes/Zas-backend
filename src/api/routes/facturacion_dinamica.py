from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse
from bson import ObjectId
from bson.errors import InvalidId
from ..database import db, pedidos_collection
from ..models.formato_impresion import FacturaPreliminarData
from datetime import datetime
from typing import Optional, Dict, Any

router = APIRouter()

# Colección para formatos de impresión
formatos_collection = db["formatos_impresion"]

@router.get("/pedidos/{pedido_id}/factura-preliminar")
async def generar_factura_preliminar(pedido_id: str):
    """
    Generar factura preliminar con formato dinámico.
    """
    try:
        # Convertir ID a ObjectId
        try:
            pedido_object_id = ObjectId(pedido_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="ID de pedido inválido")
        
        # Obtener datos del pedido
        pedido = pedidos_collection.find_one({"_id": pedido_object_id})
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Obtener formato de impresión dinámico
        formato = formatos_collection.find_one({
            "tipo": "factura_preliminar",
            "activo": True
        })
        
        if not formato:
            # Si no existe formato específico, usar formato por defecto
            formato = crear_formato_por_defecto("factura_preliminar")
        
        # Generar HTML con datos dinámicos
        html_factura = generar_html_factura(pedido, formato)
        
        return JSONResponse(
            content={
                "html": html_factura,
                "datos_empresa": formato["datos_empresa"],
                "configuracion_diseno": formato["configuracion_diseno"],
                "pedido_id": pedido_id,
                "numero_factura": generar_numero_factura(pedido),
                "fecha_factura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al generar factura preliminar: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/pedidos/{pedido_id}/factura-final")
async def generar_factura_final(pedido_id: str):
    """
    Generar factura final con formato dinámico.
    """
    try:
        # Convertir ID a ObjectId
        try:
            pedido_object_id = ObjectId(pedido_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="ID de pedido inválido")
        
        # Obtener datos del pedido
        pedido = pedidos_collection.find_one({"_id": pedido_object_id})
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Obtener formato de impresión dinámico
        formato = formatos_collection.find_one({
            "tipo": "factura_final",
            "activo": True
        })
        
        if not formato:
            # Si no existe formato específico, usar formato por defecto
            formato = crear_formato_por_defecto("factura_final")
        
        # Generar HTML con datos dinámicos
        html_factura = generar_html_factura(pedido, formato)
        
        return JSONResponse(
            content={
                "html": html_factura,
                "datos_empresa": formato["datos_empresa"],
                "configuracion_diseno": formato["configuracion_diseno"],
                "pedido_id": pedido_id,
                "numero_factura": generar_numero_factura(pedido),
                "fecha_factura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al generar factura final: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/pedidos/{pedido_id}/etiqueta-envio")
async def generar_etiqueta_envio(pedido_id: str):
    """
    Generar etiqueta de envío con formato dinámico.
    """
    try:
        # Convertir ID a ObjectId
        try:
            pedido_object_id = ObjectId(pedido_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="ID de pedido inválido")
        
        # Obtener datos del pedido
        pedido = pedidos_collection.find_one({"_id": pedido_object_id})
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Obtener formato de impresión dinámico
        formato = formatos_collection.find_one({
            "tipo": "etiqueta_envio",
            "activo": True
        })
        
        if not formato:
            # Si no existe formato específico, usar formato por defecto
            formato = crear_formato_por_defecto("etiqueta_envio")
        
        # Generar HTML con datos dinámicos
        html_etiqueta = generar_html_etiqueta_envio(pedido, formato)
        
        return JSONResponse(
            content={
                "html": html_etiqueta,
                "datos_empresa": formato["datos_empresa"],
                "configuracion_diseno": formato["configuracion_diseno"],
                "pedido_id": pedido_id,
                "numero_envio": generar_numero_envio(pedido),
                "fecha_envio": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al generar etiqueta de envío: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

def crear_formato_por_defecto(tipo: str) -> Dict[str, Any]:
    """
    Crear formato por defecto si no existe uno específico.
    """
    return {
        "tipo": tipo,
        "datos_empresa": {
            "nombre": "FARMA AMERICA (DANIEL)",
            "rif": "J-12345678-9",
            "telefono": "+58 212 123-4567",
            "email": "info@farmaamerica.com",
            "web": "www.farmaamerica.com",
            "direccion": "Av. Principal, Edificio Farma, Piso 3, Caracas, Venezuela",
            "ciudad": "Caracas",
            "estado": "Distrito Capital",
            "codigo_postal": "1010"
        },
        "configuracion_diseno": {
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
        },
        "campos_dinamicos": {
            "mostrar_fecha": True,
            "mostrar_numero_factura": True,
            "mostrar_cliente": True,
            "mostrar_productos": True,
            "mostrar_totales": True,
            "mostrar_observaciones": True,
            "formato_fecha": "DD/MM/YYYY",
            "formato_moneda": "Bs.",
            "decimales": 2
        },
        "plantilla_html": ""
    }

def generar_html_factura(pedido: Dict[str, Any], formato: Dict[str, Any]) -> str:
    """
    Generar HTML de factura con datos dinámicos.
    """
    datos_empresa = formato["datos_empresa"]
    config = formato["configuracion_diseno"]
    campos = formato["campos_dinamicos"]
    
    # Procesar datos del pedido
    cliente = pedido.get("cliente", {})
    productos = pedido.get("productos", [])
    total = pedido.get("total", 0)
    subtotal = pedido.get("subtotal", 0)
    observaciones = pedido.get("observacion", "")
    
    # Calcular IVA
    iva = total - subtotal if total > subtotal else total * 0.16
    
    # Formatear fecha
    fecha_pedido = pedido.get("fecha", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if isinstance(fecha_pedido, str):
        try:
            fecha_obj = datetime.strptime(fecha_pedido, "%Y-%m-%d %H:%M:%S")
            fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
        except:
            fecha_formateada = fecha_pedido
    else:
        fecha_formateada = fecha_pedido.strftime("%d/%m/%Y")
    
    # Generar número de factura
    numero_factura = generar_numero_factura(pedido)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Factura {numero_factura}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: {config.get('tamaño_fuente', '12px')};
                margin: {config.get('margen_superior', '20px')} {config.get('margen_derecho', '20px')} {config.get('margen_inferior', '20px')} {config.get('margen_izquierdo', '20px')};
                color: {config.get('color_secundario', '#64748b')};
                line-height: 1.4;
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
            }}
            .factura-info {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 30px;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
            }}
            .cliente-info {{
                margin-bottom: 30px;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
            }}
            .productos-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .productos-table th,
            .productos-table td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
            }}
            .productos-table th {{
                background-color: {config.get('color_principal', '#1e40af')};
                color: white;
                font-weight: bold;
            }}
            .productos-table tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            .totales {{
                text-align: right;
                margin-top: 20px;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
            }}
            .total-final {{
                font-size: 18px;
                font-weight: bold;
                color: {config.get('color_principal', '#1e40af')};
                border-top: 2px solid {config.get('color_principal', '#1e40af')};
                padding-top: 10px;
                margin-top: 10px;
            }}
            .observaciones {{
                margin-top: 30px;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
            }}
            @media print {{
                body {{ margin: 0; }}
                .no-print {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="empresa-nombre">{datos_empresa.get('nombre', 'Empresa')}</div>
            <div class="empresa-info">
                {f"<div><strong>RIF:</strong> {datos_empresa.get('rif', '')}</div>" if config.get('mostrar_rif', True) else ""}
                {f"<div>{datos_empresa.get('direccion', '')}</div>" if config.get('mostrar_direccion', True) else ""}
                {f"<div>{datos_empresa.get('ciudad', '')}, {datos_empresa.get('estado', '')}</div>" if config.get('mostrar_direccion', True) else ""}
                {f"<div>{datos_empresa.get('telefono', '')}</div>" if config.get('mostrar_telefono', True) else ""}
                {f"<div>{datos_empresa.get('email', '')}</div>" if config.get('mostrar_email', True) else ""}
                {f"<div>{datos_empresa.get('web', '')}</div>" if config.get('mostrar_web', True) else ""}
            </div>
        </div>
        
        <div class="factura-info">
            <div>
                <strong>Factura:</strong> {numero_factura}<br>
                {f"<strong>Fecha:</strong> {fecha_formateada}" if campos.get('mostrar_fecha', True) else ""}
            </div>
            <div>
                <strong>Pedido ID:</strong> {str(pedido.get('_id', ''))}<br>
                <strong>Estado:</strong> {pedido.get('estado', 'N/A')}
            </div>
        </div>
        
        {"<div class='cliente-info'><h3>Datos del Cliente:</h3><div><strong>Nombre:</strong> " + cliente.get('nombre', 'N/A') + "</div><div><strong>RIF:</strong> " + pedido.get('rif', 'N/A') + "</div>" + (f"<div><strong>Dirección:</strong> {cliente.get('direccion', 'N/A')}</div>" if cliente.get('direccion') else "") + (f"<div><strong>Teléfono:</strong> {cliente.get('telefono', 'N/A')}</div>" if cliente.get('telefono') else "") + (f"<div><strong>Email:</strong> {cliente.get('email', 'N/A')}</div>" if cliente.get('email') else "") + "</div>" if campos.get('mostrar_cliente', True) else ""}
        
        {"<table class='productos-table'><thead><tr><th>Producto</th><th>Cantidad</th><th>Precio Unit.</th><th>Total</th></tr></thead><tbody>" + ''.join([f"<tr><td>{p.get('nombre', 'N/A')}</td><td>{p.get('cantidad', 0)}</td><td>{campos.get('formato_moneda', 'Bs.')} {p.get('precio', 0):.2f}</td><td>{campos.get('formato_moneda', 'Bs.')} {(p.get('cantidad', 0) * p.get('precio', 0)):.2f}</td></tr>" for p in productos]) + "</tbody></table>" if campos.get('mostrar_productos', True) else ""}
        
        {"<div class='totales'><div><strong>Subtotal:</strong> " + campos.get('formato_moneda', 'Bs.') + f" {subtotal:.2f}</div><div><strong>IVA (16%):</strong> " + campos.get('formato_moneda', 'Bs.') + f" {iva:.2f}</div><div class='total-final'><strong>TOTAL:</strong> " + campos.get('formato_moneda', 'Bs.') + f" {total:.2f}</div></div>" if campos.get('mostrar_totales', True) else ""}
        
        {"<div class='observaciones'><h3>Observaciones:</h3><div>" + (observaciones if observaciones else 'Ninguna') + "</div></div>" if campos.get('mostrar_observaciones', True) and observaciones else ""}
        
        <div style="margin-top: 50px; text-align: center; font-size: 10px; color: #999;">
            <p>Factura generada el {datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")}</p>
            <p>Gracias por su compra</p>
        </div>
    </body>
    </html>
    """
    
    return html

def generar_html_etiqueta_envio(pedido: Dict[str, Any], formato: Dict[str, Any]) -> str:
    """
    Generar HTML de etiqueta de envío con datos dinámicos.
    """
    datos_empresa = formato["datos_empresa"]
    config = formato["configuracion_diseno"]
    campos = formato.get("campos_dinamicos", {})
    
    cliente = pedido.get("cliente", {})
    numero_envio = generar_numero_envio(pedido)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Etiqueta de Envío {numero_envio}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 14px;
                margin: 10px;
                color: {config.get('color_secundario', '#64748b')};
            }}
            .etiqueta {{
                border: 2px solid {config.get('color_principal', '#1e40af')};
                padding: 20px;
                max-width: 400px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
                border-bottom: 1px solid {config.get('color_principal', '#1e40af')};
                padding-bottom: 10px;
            }}
            .empresa-nombre {{
                font-size: 18px;
                font-weight: bold;
                color: {config.get('color_principal', '#1e40af')};
            }}
            .destinatario {{
                margin-bottom: 20px;
            }}
            .destinatario h3 {{
                color: {config.get('color_principal', '#1e40af')};
                margin-bottom: 10px;
            }}
            .info-envio {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .codigo-barras {{
                text-align: center;
                margin-top: 20px;
                font-family: monospace;
                font-size: 16px;
                letter-spacing: 2px;
            }}
        </style>
    </head>
    <body>
        <div class="etiqueta">
            <div class="header">
                <div class="empresa-nombre">{datos_empresa.get('nombre', 'Empresa')}</div>
                <div>{datos_empresa.get('direccion', '')}</div>
                <div>{datos_empresa.get('telefono', '')}</div>
            </div>
            
            <div class="destinatario">
                <h3>DESTINATARIO:</h3>
                <div><strong>{cliente.get('nombre', 'N/A')}</strong></div>
                <div>RIF: {pedido.get('rif', 'N/A')}</div>
                {f"<div>{cliente.get('direccion', 'N/A')}</div>" if cliente.get('direccion') else ""}
                {f"<div>{cliente.get('ciudad', 'N/A')}, {cliente.get('estado', 'N/A')}</div>" if cliente.get('ciudad') else ""}
                {f"<div>Tel: {cliente.get('telefono', 'N/A')}</div>" if cliente.get('telefono') else ""}
            </div>
            
            <div class="info-envio">
                <div><strong>Número de Envío:</strong> {numero_envio}</div>
                <div><strong>Pedido ID:</strong> {str(pedido.get('_id', ''))}</div>
                <div><strong>Fecha:</strong> {datetime.now().strftime("%d/%m/%Y")}</div>
                <div><strong>Peso:</strong> {pedido.get('peso', 'N/A')} kg</div>
                <div><strong>Valor Declarado:</strong> {campos.get('formato_moneda', 'Bs.')} {pedido.get('total', 0):.2f}</div>
            </div>
            
            <div class="codigo-barras">
                <div>||| {numero_envio} |||</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def generar_numero_factura(pedido: Dict[str, Any]) -> str:
    """
    Generar número de factura único.
    """
    pedido_id = str(pedido.get('_id', ''))[-6:]  # Últimos 6 caracteres del ID
    fecha = datetime.now().strftime("%Y%m%d")
    return f"FAC-{fecha}-{pedido_id}"

def generar_numero_envio(pedido: Dict[str, Any]) -> str:
    """
    Generar número de envío único.
    """
    pedido_id = str(pedido.get('_id', ''))[-6:]  # Últimos 6 caracteres del ID
    fecha = datetime.now().strftime("%Y%m%d")
    return f"ENV-{fecha}-{pedido_id}"

