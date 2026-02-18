from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class FormatoImpresion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tipo: str  # "factura_preliminar", "factura_final", "etiqueta_envio", etc.
    datos_empresa: Dict[str, Any] = Field(default={
        "nombre": "FARMA AMERICA (DANIEL)",
        "rif": "J-12345678-9",
        "telefono": "+58 212 123-4567",
        "email": "info@farmaamerica.com",
        "web": "www.farmaamerica.com",
        "direccion": "Av. Principal, Edificio Farma, Piso 3, Caracas, Venezuela",
        "ciudad": "Caracas",
        "estado": "Distrito Capital",
        "codigo_postal": "1010"
    })
    configuracion_diseno: Dict[str, Any] = Field(default={
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
    })
    plantilla_html: str = Field(default="")  # HTML personalizado
    campos_dinamicos: Dict[str, Any] = Field(default={
        "mostrar_fecha": True,
        "mostrar_numero_factura": True,
        "mostrar_cliente": True,
        "mostrar_productos": True,
        "mostrar_totales": True,
        "mostrar_observaciones": True,
        "formato_fecha": "DD/MM/YYYY",
        "formato_moneda": "Bs.",
        "decimales": 2
    })
    activo: bool = True
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)
    usuario_creacion: Optional[str] = None
    usuario_actualizacion: Optional[str] = None

class FormatoImpresionCreate(BaseModel):
    tipo: str
    datos_empresa: Optional[Dict[str, Any]] = None
    configuracion_diseno: Optional[Dict[str, Any]] = None
    plantilla_html: Optional[str] = ""
    campos_dinamicos: Optional[Dict[str, Any]] = None
    activo: bool = True
    usuario_creacion: Optional[str] = None

class FormatoImpresionUpdate(BaseModel):
    datos_empresa: Optional[Dict[str, Any]] = None
    configuracion_diseno: Optional[Dict[str, Any]] = None
    plantilla_html: Optional[str] = None
    campos_dinamicos: Optional[Dict[str, Any]] = None
    activo: Optional[bool] = None
    usuario_actualizacion: Optional[str] = None

class FacturaPreliminarData(BaseModel):
    pedido_id: str
    datos_empresa: Dict[str, Any]
    configuracion_diseno: Dict[str, Any]
    campos_dinamicos: Dict[str, Any]
    plantilla_html: Optional[str] = None

class FormatoImpresionSimplificado(BaseModel):
    """Formato simplificado para crear/actualizar formatos de impresión desde el frontend."""
    tipo: str
    logo_url: Optional[str] = None
    titulo: Optional[str] = None
    mostrar_rif: Optional[bool] = True
    mostrar_direccion: Optional[bool] = True
    mostrar_telefono: Optional[bool] = True
    campos_extra: Optional[Dict[str, Any]] = None
    layout: Optional[Dict[str, Any]] = None


