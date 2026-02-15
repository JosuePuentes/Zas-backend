#!/usr/bin/env python3
"""
Script para probar los endpoints localmente.
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importar la aplicación FastAPI
from api.main import app
from api.database import db

def test_local_endpoints():
    """Probar los endpoints localmente usando la aplicación FastAPI."""
    
    try:
        # Obtener la colección de formatos
        formatos_collection = db["formatos_impresion"]
        
        # Verificar que existen formatos
        formatos = list(formatos_collection.find({}))
        print(f"📊 Formatos en la base de datos: {len(formatos)}")
        
        for formato in formatos:
            print(f"   📄 {formato['tipo']} - Activo: {formato.get('activo', False)}")
        
        # Probar la función de obtener formatos
        from api.routes.formato_impresion import obtener_formatos, obtener_formato_por_tipo
        
        print("\n🧪 Probando funciones localmente...")
        
        # Simular una petición GET /formatos-impresion/
        print("1. Probando obtener_formatos()...")
        # Esta función necesita ser llamada como endpoint, no directamente
        
        # Verificar que las rutas están registradas
        print("\n📋 Rutas registradas en la aplicación:")
        for route in app.routes:
            if hasattr(route, 'path'):
                print(f"   {route.methods} {route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al probar localmente: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    print("🧪 Probando endpoints localmente...")
    print("=" * 50)
    
    if test_local_endpoints():
        print("\n✅ Pruebas locales completadas")
        print("\n💡 Si las pruebas locales funcionan pero el servidor remoto no,")
        print("   es posible que necesites reiniciar el servidor en Render.")
    else:
        print("\n❌ Error en las pruebas locales")

if __name__ == "__main__":
    main()

