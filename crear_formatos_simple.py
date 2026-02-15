#!/usr/bin/env python3
"""
Script simple para crear formatos de impresión por defecto usando la conexión existente del backend.
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importar la conexión existente
from api.database import db

def crear_formatos_por_defecto():
    """Crear formatos de impresión por defecto usando la conexión existente."""
    
    try:
        formatos_collection = db["formatos_impresion"]
        
        # Verificar si ya existen formatos
        formatos_existentes = list(formatos_collection.find({}))
        if formatos_existentes:
            print(f"📋 Ya existen {len(formatos_existentes)} formatos en la base de datos")
            print("✅ Los endpoints ya deberían funcionar correctamente")
            return True
        
        # Definir formatos por defecto
        formatos_por_defecto = [
            {
                "tipo": "factura_preliminar",
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
                "plantilla_html": "",
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
                "activo": True,
                "fecha_creacion": datetime.now(),
                "fecha_actualizacion": datetime.now(),
                "usuario_creacion": "sistema",
                "usuario_actualizacion": "sistema"
            },
            {
                "tipo": "factura_final",
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
                    "mostrar_web": True,
                    "color_principal": "#059669",
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
                "plantilla_html": "",
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
                "activo": True,
                "fecha_creacion": datetime.now(),
                "fecha_actualizacion": datetime.now(),
                "usuario_creacion": "sistema",
                "usuario_actualizacion": "sistema"
            },
            {
                "tipo": "etiqueta_envio",
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
                    "mostrar_direccion": False,
                    "mostrar_telefono": True,
                    "mostrar_email": False,
                    "mostrar_web": False,
                    "color_principal": "#dc2626",
                    "color_secundario": "#374151",
                    "fuente_titulo": "bold",
                    "fuente_texto": "normal",
                    "tamaño_fuente": "10px",
                    "espaciado": "compacto",
                    "margen_superior": "10px",
                    "margen_inferior": "10px",
                    "margen_izquierdo": "10px",
                    "margen_derecho": "10px"
                },
                "plantilla_html": "",
                "campos_dinamicos": {
                    "mostrar_fecha": True,
                    "mostrar_numero_factura": True,
                    "mostrar_cliente": True,
                    "mostrar_productos": False,
                    "mostrar_totales": False,
                    "mostrar_observaciones": True,
                    "formato_fecha": "DD/MM/YYYY",
                    "formato_moneda": "Bs.",
                    "decimales": 2
                },
                "activo": True,
                "fecha_creacion": datetime.now(),
                "fecha_actualizacion": datetime.now(),
                "usuario_creacion": "sistema",
                "usuario_actualizacion": "sistema"
            }
        ]
        
        # Insertar formatos
        resultado = formatos_collection.insert_many(formatos_por_defecto)
        
        print(f"✅ Se crearon {len(resultado.inserted_ids)} formatos de impresión:")
        for formato in formatos_por_defecto:
            print(f"   📄 {formato['tipo']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear formatos: {e}")
        return False

def main():
    """Función principal."""
    print("🚀 Creando formatos de impresión por defecto...")
    print("=" * 50)
    
    if crear_formatos_por_defecto():
        print("\n✅ ¡Formatos de impresión creados exitosamente!")
        print("\n📋 Formatos disponibles:")
        print("   • factura_preliminar")
        print("   • factura_final") 
        print("   • etiqueta_envio")
        print("\n🌐 Ahora tu frontend debería poder conectarse correctamente!")
    else:
        print("\n❌ Error al crear los formatos de impresión")

if __name__ == "__main__":
    main()

