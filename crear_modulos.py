#!/usr/bin/env python3
"""
Script para crear/actualizar módulos en la base de datos
"""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client["DROCOLVEN"]
modulos_collection = db["modulos"]

def crear_modulos():
    """Crear todos los módulos necesarios"""
    
    # Lista completa de módulos que deberías tener
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
    
    print("Creando/actualizando módulos...")
    print("=" * 50)
    
    # Limpiar módulos existentes
    print("Limpiando módulos existentes...")
    modulos_collection.delete_many({})
    
    # Insertar nuevos módulos
    print("Insertando nuevos módulos...")
    resultado = modulos_collection.insert_many(modulos_completos)
    
    print(f"Módulos creados: {len(resultado.inserted_ids)}")
    
    # Mostrar los módulos creados
    print("\nMódulos disponibles:")
    print("-" * 30)
    modulos = list(modulos_collection.find())
    for i, modulo in enumerate(modulos, 1):
        print(f"{i:2d}. {modulo['name']} - {modulo.get('descripcion', 'Sin descripción')}")
    
    return len(resultado.inserted_ids)

def verificar_modulos():
    """Verificar qué módulos están en la base de datos"""
    print("\nVerificando módulos existentes...")
    print("=" * 50)
    
    modulos = list(modulos_collection.find())
    
    if not modulos:
        print("No hay módulos en la base de datos")
        return 0
    
    print(f"Total de módulos encontrados: {len(modulos)}")
    print("\nMódulos actuales:")
    print("-" * 30)
    
    for i, modulo in enumerate(modulos, 1):
        print(f"{i:2d}. {modulo['name']} - {modulo.get('descripcion', 'Sin descripción')}")
    
    return len(modulos)

if __name__ == "__main__":
    print("GESTOR DE MÓDULOS - DROCOLVEN")
    print("=" * 50)
    
    try:
        # Verificar módulos actuales
        modulos_actuales = verificar_modulos()
        
        if modulos_actuales < 10:  # Si hay menos de 10 módulos, recrear
            print(f"\nSolo se encontraron {modulos_actuales} módulos. Creando módulos completos...")
            modulos_creados = crear_modulos()
            print(f"\n✅ Se crearon {modulos_creados} módulos exitosamente")
        else:
            print(f"\n✅ Se encontraron {modulos_actuales} módulos. No es necesario recrear.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Proceso completado")
