#!/usr/bin/env python3
"""
Script para crear el módulo 'administracion' en la base de datos
"""
from pymongo import MongoClient

def crear_modulo_administracion():
    """Crear el módulo administracion en la base de datos"""
    
    print("CREANDO MODULO ADMINISTRACION")
    print("=" * 50)
    
    MONGO_URI = "mongodb+srv://Dios:EikobPHJKkEMSUq9@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["DROCOLVEN"]
        modulos_collection = db["modulos"]
        
        # Datos del módulo administración
        modulo_administracion = {
            "name": "administracion",
            "descripcion": "Gestión central de pedidos y estados del sistema",
            "activo": True
        }
        
        print("1. Verificando si el módulo ya existe...")
        modulo_existente = modulos_collection.find_one({"name": "administracion"})
        
        if modulo_existente:
            print("   El módulo 'administracion' ya existe.")
            print(f"   ID: {modulo_existente['_id']}")
            print(f"   Descripción: {modulo_existente.get('descripcion', 'Sin descripción')}")
            print(f"   Activo: {modulo_existente.get('activo', False)}")
        else:
            print("2. Creando nuevo módulo 'administracion'...")
            resultado = modulos_collection.insert_one(modulo_administracion)
            print(f"   Módulo creado con ID: {resultado.inserted_id}")
        
        print("\n3. Verificando módulos existentes...")
        total_modulos = modulos_collection.count_documents({})
        print(f"   Total de módulos: {total_modulos}")
        
        # Listar todos los módulos
        modulos = list(modulos_collection.find())
        print("\n   Lista de módulos:")
        for modulo in modulos:
            print(f"     - {modulo.get('name')} (ID: {modulo.get('_id')})")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    finally:
        client.close()
        print("\nConexión a MongoDB cerrada.")

if __name__ == "__main__":
    exito = crear_modulo_administracion()
    if exito:
        print("\n✅ RESULTADO: Módulo administración creado/verificado correctamente.")
    else:
        print("\n❌ RESULTADO: Problemas al crear el módulo administración.")


