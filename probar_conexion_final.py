#!/usr/bin/env python3
"""
Script para probar la conexión con las variables de entorno proporcionadas
"""
import os
from pymongo import MongoClient

def probar_conexion():
    """Probar la conexión con MongoDB Atlas"""
    
    print("PROBANDO CONEXION CON MONGODB ATLAS")
    print("=" * 50)
    
    # Variables de entorno proporcionadas
    MONGO_URI = "mongodb+srv://Dios:EikobPHJKkEMSUq9@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
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
        
        # Crear módulos si no existen
        if "modulos" not in colecciones or db["modulos"].count_documents({}) < 10:
            print("\nCreando módulos faltantes...")
            modulos_completos = [
                {"name": "inventario", "descripcion": "Gestión de inventario", "activo": True},
                {"name": "pedidos", "descripcion": "Gestión de pedidos", "activo": True},
                {"name": "pedidos_enviados", "descripcion": "Pedidos enviados", "activo": True},
                {"name": "clientes", "descripcion": "Gestión de clientes", "activo": True},
                {"name": "picking", "descripcion": "Proceso de picking", "activo": True},
                {"name": "check_picking", "descripcion": "Verificación de picking", "activo": True},
                {"name": "packing", "descripcion": "Proceso de packing", "activo": True},
                {"name": "envio", "descripcion": "Gestión de envíos", "activo": True},
                {"name": "facturacion", "descripcion": "Gestión de facturación", "activo": True},
                {"name": "reclamos", "descripcion": "Gestión de reclamos", "activo": True},
                {"name": "reportes", "descripcion": "Generación de reportes", "activo": True},
                {"name": "usuarios", "descripcion": "Gestión de usuarios", "activo": True},
                {"name": "configuracion", "descripcion": "Configuración del sistema", "activo": True},
                {"name": "transacciones", "descripcion": "Gestión de transacciones", "activo": True},
                {"name": "convenios", "descripcion": "Gestión de convenios", "activo": True},
                {"name": "contacto", "descripcion": "Gestión de contacto", "activo": True}
            ]
            
            # Limpiar módulos existentes
            db["modulos"].delete_many({})
            
            # Insertar nuevos módulos
            resultado = db["modulos"].insert_many(modulos_completos)
            print(f"✅ Se crearon {len(resultado.inserted_ids)} módulos")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR DE CONEXION: {e}")
        return False

if __name__ == "__main__":
    exito = probar_conexion()
    
    print("\n" + "=" * 50)
    if exito:
        print("✅ RESULTADO: Conexión a MongoDB Atlas funcionando correctamente")
        print("✅ Módulos creados/verificados exitosamente")
    else:
        print("❌ RESULTADO: Problemas con la conexión a MongoDB Atlas")
