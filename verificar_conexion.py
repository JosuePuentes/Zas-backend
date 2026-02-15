#!/usr/bin/env python3
"""
Script para verificar la conexión a MongoDB Atlas
"""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def verificar_conexion():
    """Verificar la conexión a MongoDB Atlas"""
    
    print("VERIFICANDO CONEXION A MONGODB ATLAS")
    print("=" * 50)
    
    try:
        # Obtener la URI de MongoDB
        MONGO_URI = os.getenv("MONGO_URI")
        
        if not MONGO_URI:
            print("ERROR: No se encontró MONGO_URI en las variables de entorno")
            return False
        
        print(f"MONGO_URI encontrada: {MONGO_URI[:50]}...")
        
        # Intentar conectar
        print("Conectando a MongoDB Atlas...")
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        
        # Probar la conexión
        db = client["DROCOLVEN"]
        
        # Listar colecciones para verificar que funciona
        colecciones = db.list_collection_names()
        
        print("✅ CONEXION EXITOSA A MONGODB ATLAS")
        print(f"Base de datos: {db.name}")
        print(f"Colecciones encontradas: {len(colecciones)}")
        
        print("\nColecciones disponibles:")
        for i, collection in enumerate(colecciones, 1):
            print(f"  {i:2d}. {collection}")
        
        # Verificar colecciones específicas
        colecciones_importantes = [
            "INVENTARIO_MAESTRO",
            "CLIENTES", 
            "PEDIDOS",
            "usuarios_admin",
            "modulos",
            "CONVENIOS"
        ]
        
        print("\nVerificando colecciones importantes:")
        for coleccion in colecciones_importantes:
            if coleccion in colecciones:
                count = db[coleccion].count_documents({})
                print(f"  ✅ {coleccion}: {count} documentos")
            else:
                print(f"  ❌ {coleccion}: NO ENCONTRADA")
        
        # Verificar módulos específicamente
        print("\nVerificando módulos:")
        if "modulos" in colecciones:
            modulos = list(db["modulos"].find())
            print(f"  Total de módulos: {len(modulos)}")
            for modulo in modulos:
                print(f"    - {modulo.get('name', 'Sin nombre')}")
        else:
            print("  ❌ Colección 'modulos' no encontrada")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR DE CONEXION: {e}")
        return False

if __name__ == "__main__":
    exito = verificar_conexion()
    
    print("\n" + "=" * 50)
    if exito:
        print("✅ RESULTADO: Conexión a MongoDB Atlas funcionando correctamente")
    else:
        print("❌ RESULTADO: Problemas con la conexión a MongoDB Atlas")
        print("\nPosibles soluciones:")
        print("1. Verificar que MONGO_URI esté configurada en el archivo .env")
        print("2. Verificar que la IP esté autorizada en MongoDB Atlas")
        print("3. Verificar que las credenciales sean correctas")

