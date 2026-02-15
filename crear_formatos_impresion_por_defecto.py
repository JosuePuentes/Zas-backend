#!/usr/bin/env python3
"""
Script para crear formatos de impresión por defecto en la base de datos.
Este script crea los formatos básicos que necesita el frontend.
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Agregar el directorio src al path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

def conectar_mongodb():
    """Conectar a MongoDB usando las variables de entorno."""
    try:
        # Usar la configuración existente del backend
        mongodb_url = "mongodb+srv://master:go3DjrOJmczPNDNNz@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        
        client = MongoClient(mongodb_url)
        # Probar la conexión
        client.admin.command('ping')
        print("✅ Conexión a MongoDB establecida correctamente")
        return client
    except Exception as e:
        print(f"❌ Error al conectar a MongoDB: {e}")
        return None

def crear_formatos_por_defecto():
    """Crear formatos de impresión por defecto."""
    
    client = conectar_mongodb()
    if not client:
        return False
    
    try:
        db = client.get_database()
        formatos_collection = db["formatos_impresion"]
        
        # Verificar si ya existen formatos
        formatos_existentes = list(formatos_collection.find({}))
        if formatos_existentes:
            print(f"📋 Ya existen {len(formatos_existentes)} formatos en la base de datos")
            respuesta = input("¿Deseas recrear los formatos? (s/n): ").lower()
            if respuesta != 's':
                print("✅ Operación cancelada")
                return True
            else:
                # Eliminar formatos existentes
                formatos_collection.delete_many({})
                print("🗑️ Formatos existentes eliminados")
        
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
        
        # Verificar que se crearon correctamente
        formatos_creados = list(formatos_collection.find({}))
        print(f"\n📊 Total de formatos en la base de datos: {len(formatos_creados)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear formatos: {e}")
        return False
    finally:
        client.close()

def main():
    """Función principal."""
    print("🚀 Iniciando creación de formatos de impresión por defecto...")
    print("=" * 60)
    
    if crear_formatos_por_defecto():
        print("\n✅ ¡Formatos de impresión creados exitosamente!")
        print("\n📋 Formatos disponibles:")
        print("   • factura_preliminar")
        print("   • factura_final") 
        print("   • etiqueta_envio")
        print("\n🌐 Ahora tu frontend debería poder conectarse correctamente a:")
        print("   GET /formatos-impresion/")
        print("   GET /formatos-impresion/factura_preliminar")
        print("   POST /formatos-impresion/")
        print("   PUT /formatos-impresion/{tipo}")
        print("   DELETE /formatos-impresion/{tipo}")
        print("   DELETE /formatos-impresion/id/{id}")
    else:
        print("\n❌ Error al crear los formatos de impresión")
        sys.exit(1)

if __name__ == "__main__":
    main()