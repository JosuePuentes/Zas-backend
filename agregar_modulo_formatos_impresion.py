#!/usr/bin/env python3
"""
Script para agregar el módulo 'formatos_impresion' a la base de datos
"""
from pymongo import MongoClient
from datetime import datetime

def agregar_modulo_formatos_impresion():
    """Agregar el módulo formatos_impresion a la base de datos"""
    
    print("AGREGANDO MODULO FORMATOS_IMPRESION")
    print("=" * 50)
    
    MONGO_URI = "mongodb+srv://Dios:EikobPHJKkEMSUq9@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["DROCOLVEN"]
        modulos_collection = db["modulos"]
        
        # Datos del módulo formatos_impresion
        modulo_formatos_impresion = {
            "name": "formatos_impresion",
            "descripcion": "Gestión de formatos de impresión dinámicos",
            "activo": True
        }
        
        print("1. Verificando si el módulo 'formatos_impresion' ya existe...")
        if modulos_collection.find_one({"name": "formatos_impresion"}):
            print("   El módulo 'formatos_impresion' ya existe. No se creará de nuevo.")
        else:
            print("   Creando módulo 'formatos_impresion'...")
            result = modulos_collection.insert_one(modulo_formatos_impresion)
            print(f"   Módulo 'formatos_impresion' creado con ID: {result.inserted_id}")
        
        print("\n2. Verificando todos los módulos existentes...")
        modulos_actuales = list(modulos_collection.find())
        print(f"   Total de módulos en la base de datos: {len(modulos_actuales)}")
        for modulo in modulos_actuales:
            print(f"     - {modulo.get('name')} (ID: {modulo.get('_id')})")
            
        print("\nProceso de creación de módulo completado.")
        
    except Exception as e:
        print(f"Error al crear módulo: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()
            print("Conexión a MongoDB cerrada.")

if __name__ == "__main__":
    agregar_modulo_formatos_impresion()


