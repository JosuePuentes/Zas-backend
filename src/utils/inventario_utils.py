"""
Utilidades para el manejo de inventario
Incluye funciones para calcular utilidad del 40% y manejo de descuentos de inventario
"""

def calcular_precio_con_utilidad_40(precio_costo: float) -> float:
    """
    Calcula el precio de venta con una utilidad del 40%
    
    Fórmula: Precio de venta = Precio de costo / (1 - 0.40) = Precio de costo / 0.60
    Esto garantiza que el margen de utilidad sea exactamente del 40% sobre el precio de venta.
    
    Args:
        precio_costo: Precio de costo del producto
        
    Returns:
        Precio de venta con utilidad del 40%
    """
    if precio_costo is None or precio_costo <= 0:
        return 0.0
    
    # Precio de venta = Precio de costo / (1 - margen_utilidad)
    # Para 40% de utilidad: precio_venta = precio_costo / 0.60
    precio_venta = precio_costo / 0.60
    
    # Redondear a 2 decimales
    return round(precio_venta, 2)


def precio_desde_costo_y_utilidad(costo: float, utilidad_pct: float) -> float:
    """
    Precio de venta dado costo y utilidad (% sobre precio de venta, utilidad comercial/contable).
    Fórmula: precio = costo / (1 - utilidad_pct/100).
    Ejemplo: costo $1, utilidad 30% → precio = 1 / 0.70 = 1.43 (no 1.30).
    """
    if costo is None or costo <= 0:
        return 0.0
    try:
        u = float(utilidad_pct)
        if u >= 100:
            return 0.0
        return round(costo / (1 - u / 100), 2)
    except (TypeError, ValueError):
        return 0.0


def utilidad_pct_desde_precio_y_costo(precio: float, costo: float) -> float:
    """Utilidad % sobre precio (margen): (1 - costo/precio)*100. Para informe como porcentaje."""
    if precio is None or precio <= 0:
        return 0.0
    try:
        c = float(costo) if costo is not None else 0
        return round((1 - c / precio) * 100, 2)
    except (TypeError, ValueError):
        return 0.0


def calcular_precio_con_utilidad_40_alternativa(precio_costo: float) -> float:
    """
    Alternativa: Calcula el precio de venta agregando 40% al costo
    Fórmula: Precio de venta = Precio de costo * 1.40
    
    Esta fórmula agrega el 40% sobre el costo, no sobre el precio de venta.
    Úsala si prefieres este método de cálculo.
    
    Args:
        precio_costo: Precio de costo del producto
        
    Returns:
        Precio de venta con 40% agregado al costo
    """
    if precio_costo is None or precio_costo <= 0:
        return 0.0
    
    precio_venta = precio_costo * 1.40
    
    # Redondear a 2 decimales
    return round(precio_venta, 2)


def validar_stock_suficiente(existencia_actual: int, cantidad_solicitada: int) -> tuple[bool, str]:
    """
    Valida si hay stock suficiente para realizar una operación
    
    Args:
        existencia_actual: Cantidad actual en inventario
        cantidad_solicitada: Cantidad que se desea descontar
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if existencia_actual is None:
        existencia_actual = 0
    
    if cantidad_solicitada <= 0:
        return False, "La cantidad solicitada debe ser mayor a cero"
    
    if existencia_actual < cantidad_solicitada:
        return False, f"Stock insuficiente. Disponible: {existencia_actual}, Solicitado: {cantidad_solicitada}"
    
    return True, ""


def calcular_nuevo_stock(existencia_actual: int, cantidad: int, operacion: str) -> int:
    """
    Calcula el nuevo stock después de una operación
    
    Args:
        existencia_actual: Stock actual
        cantidad: Cantidad a procesar
        operacion: 'descontar' o 'agregar'
        
    Returns:
        Nuevo stock calculado
    """
    if existencia_actual is None:
        existencia_actual = 0
    
    if operacion == "descontar":
        nuevo_stock = existencia_actual - cantidad
        # No permitir stock negativo
        return max(0, nuevo_stock)
    elif operacion == "agregar":
        return existencia_actual + cantidad
    else:
        return existencia_actual

