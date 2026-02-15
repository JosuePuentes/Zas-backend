from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from typing import List, Optional, Dict
from datetime import date, datetime
from bson import ObjectId

class Client(BaseModel):
    rif: str
    encargado: str
    direccion: str
    telefono: str
    email: str
    password: str
    descripcion: str
    dias_credito: int
    limite_credito: float
    activo: bool = True
    descuento1: float = 0
    descuento2: float = 0
    descuento3: float = 0

class ClientUpdate(BaseModel):
    rif: Optional[str] = None
    encargado: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None # Para cambiarla opcionalmente
    descripcion: Optional[str] = None
    dias_credito: Optional[int] = None
    limite_credito: Optional[float] = None
    activo: Optional[bool] = None
    descuento1: Optional[float] = None
    descuento2: Optional[float] = None
    descuento3: Optional[float] = None

class ProductoInventario(BaseModel):
    codigo: str
    descripcion: str
    dpto: str
    nacional: str
    laboratorio: str
    fv: str
    existencia: int
    precio: float
    cantidad: int
    descuento1: float
    descuento2: float
    descuento3: float

class UserRegister(BaseModel):
    email: str
    password: str
    rif: str
    direccion: str
    telefono: str
    encargado: str
    activo: bool = True
    descuento1: float = 0.0
    descuento2: float = 0.0
    descuento3: float = 0.0

class UserLogin(BaseModel):
    email: str
    password: str

class UserAdminRegister(BaseModel):
    usuario: str
    password: str
    rol: str
    modulos: List[str]

class AdminLogin(BaseModel):
    usuario: str
    password: str

class LoteInfo(BaseModel):
    lote: str
    existencia: int
    fecha_vencimiento: str

class ProductoPedido(BaseModel):
    codigo: str
    descripcion: str
    precio: float
    descuento1: float
    descuento2: float
    descuento3: float
    descuento4: float
    cantidad_pedida: int
    cantidad_encontrada: int
    subtotal: float
    cantidad: int = 0
    cantidad_pendiente: int = 0
    existencia: Optional[int] = None
    laboratorio: Optional[str] = None
    fv: Optional[str] = None
    nacional: Optional[str] = None
    dpto: Optional[str] = None
    frio: Optional[bool] = None
    advertencia: Optional[bool] = None
    calendario: Optional[bool] = None
    lotes: Optional[List[LoteInfo]] = None
    limpieza: Optional[bool] = None
    
class PedidoResumen(BaseModel):
    cliente: str
    rif: str
    observacion: str
    total: float
    subtotal: float
    productos: list[ProductoPedido]
    estado: Optional[str] = None
    validado: Optional[bool] = False
    fecha_validacion: Optional[str] = None
    usuario_validacion: Optional[str] = None
    fecha_cancelacion: Optional[str] = None
    usuario_cancelacion: Optional[str] = None
    verificaciones_check_picking: Optional[dict] = None
    fecha_check_picking: Optional[str] = None
    usuario_check_picking: Optional[str] = None
    estado_check_picking: Optional[str] = None  # 'pendiente', 'en_proceso', 'completado'

class PedidoArmado(BaseModel):
    cliente: str
    rif: str
    observacion: str
    total: float
    productos: list[ProductoPedido]

class EstadoPedido(BaseModel):
    nuevo_estado: str

class ContactForm(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    mensaje: str

class CantidadesEncontradas(BaseModel):
    cantidades: dict

class PickingInfo(BaseModel):
    usuario: Optional[str] = None
    fechainicio_picking: Optional[str] = None
    fechafin_picking: Optional[str] = None
    estado_picking: Optional[str] = None

class PackingInfo(BaseModel):
    usuario: Optional[str] = None
    estado_packing: Optional[str] = None
    fechainicio_packing: Optional[str] = None
    fechafin_packing: Optional[str] = None

class EnvioInfo(BaseModel):
    usuario: Optional[str] = None
    chofer: Optional[str] = None
    estado_envio: Optional[str] = None
    fechaini_envio: Optional[str] = None
    fechafin_envio: Optional[str] = None

class ReclamoCliente(BaseModel):
    pedido_id: str
    rif: str
    cliente: str
    productos: list[dict]  # [{id, descripcion, cantidad, motivo}]
    observacion: str = ""
    fecha: str = ""

class UserAdmin(BaseModel):
    usuario: str
    password: Optional[str] = None
    rol: Optional[str] = None
    modulos: Optional[List[str]] = None
    nombreCompleto: str = None
    identificador: str = None

class FacturacionInfo(BaseModel):
    usuario: Optional[str] = None
    fechainicio_facturacion: Optional[str] = None
    fechafin_facturacion: Optional[str] = None
    estado_facturacion: Optional[str] = None


class TipoMovimiento(str, Enum):
    compra = "compra"
    descargo = "descargo"
    cargo = "cargo"
    venta = "venta"
    ajuste = "ajuste"
    devolucion = "devolucion"
    transferencia = "transferencia"
    pedido = "pedido"
    apartado = "apartado"
    anulacion = "anulacion"

class KardexMovimiento(BaseModel):
    fecha: str
    usuario: str
    tipo_movimiento: TipoMovimiento
    producto: dict  # Puede ser ProductoInventario o ProductoPedido
    cantidad: int
    precio: float
    observaciones: Optional[str] = None
    documento_origen: Optional[dict] = None  # Objeto del documento que genera el movimiento
    saldo_previo: Optional[int] = None
    saldo_posterior: Optional[int] = None


class ConvenioCarga(BaseModel):
    fecha: str
    usuario: str
    descripcion: str
    estado: str = "activo"  # Valor por defecto si no se envía
    clientes: List[str]      # Una lista de strings
    productos: dict[str, float] # Un diccionario con clave string y valor float

    # No olvides importar 'Optional' desde 'typing' si no lo has hecho ya
from typing import Optional
from pydantic import BaseModel, EmailStr

# ... (aquí va tu clase Client y otras importaciones)

# Modelo para la actualización (todos los campos son opcionales)
class ClientUpdate(BaseModel):
    email: Optional[EmailStr] = None
    encargado: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None
    descuento1: Optional[float] = None
    descuento2: Optional[float] = None
    descuento3: Optional[float] = None
    preciosmp: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "encargado": "Ana Rodríguez",
                "telefono": "0412-9876543"
            }
        }

class Convenio(BaseModel):
    """
    Modelo Pydantic simplificado para Convenio.
    """
    # 1. El tipo de dato es ahora el ObjectId nativo de bson.
    id: ObjectId = Field(alias="_id")
    fecha: date
    usuario: str
    descripcion: str
    estado: str
    clientes: List[str]
    productos: Dict[str, float]
    fecha_carga_utc: datetime

    class Config:
        """
        Configuración clave para que Pydantic trabaje con MongoDB.
        """
        # 2. Permite que Pydantic use el alias '_id' para poblar el campo 'id'.
        populate_by_name = True
        
        # 3. Permite que Pydantic maneje tipos de datos no estándar como ObjectId.
        arbitrary_types_allowed = True
        
        # 4. Le dice a Pydantic cómo convertir ObjectId a JSON (un string).
        json_encoders = { ObjectId: str }

class VerificacionCheckPicking(BaseModel):
    cantidadVerificada: int
    fechaVencimiento: Optional[str] = None
    codigoBarra: Optional[str] = None
    estado: str  # 'bueno', 'vencido', 'dañado'
    observaciones: Optional[str] = None

class CheckPickingData(BaseModel):
    nuevo_estado: str
    verificaciones: dict[str, VerificacionCheckPicking]

class ActualizarEstadoPedido(BaseModel):
    nuevo_estado: str
    verificaciones: Optional[dict] = None
    usuario: Optional[str] = None

class FinalizarCheckPicking(BaseModel):
    verificaciones: dict
    usuario: str

class ValidacionPedido(BaseModel):
    pin: str = Field(..., description="PIN de validación para cambiar estado del pedido")