#!/usr/bin/env python3
"""
Script para probar la conexión del backend local
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.database import db, inventario_collection, modulos_collection

def probar_backend_local():
    """Probar que el backend local funcione correctamente"""
    
    print("PROBANDO BACKEND LOCAL")
    print("=" * 50)
    
    try:
        # Probar conexión a la base de datos
        print("1. Probando conexión a MongoDB...")
        colecciones = db.list_collection_names()
        print(f"   OK - {len(colecciones)} colecciones encontradas")
        
        # Probar endpoint de inventario
        print("2. Probando endpoint de inventario...")
        productos = list(inventario_collection.find({}).limit(5))
        print(f"   OK - {len(productos)} productos encontrados")
        
        # Probar endpoint de módulos
        print("3. Probando endpoint de módulos...")
        modulos = list(modulos_collection.find({}))
        print(f"   OK - {len(modulos)} módulos encontrados")
        
        # Mostrar algunos módulos
        print("\nMódulos disponibles:")
        for modulo in modulos[:5]:
            print(f"   - {modulo.get('name', 'Sin nombre')}")
        
        print("\n✅ BACKEND LOCAL FUNCIONANDO CORRECTAMENTE")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN BACKEND LOCAL: {e}")
        return False

if __name__ == "__main__":
    exito = probar_backend_local()
    
    if exito:
        print("\n🎯 PRÓXIMO PASO: Desplegar estos cambios a Render")
        print("   - Haz commit y push de los cambios")
        print("   - O configura las variables de entorno en Render")
    else:
        print("\n🔧 NECESITAS ARREGLAR EL BACKEND LOCAL PRIMERO")

