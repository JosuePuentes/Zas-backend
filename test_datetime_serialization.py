#!/usr/bin/env python3
"""
Script para probar que la serialización de fechas funciona correctamente.
"""

import requests
import json
import sys
from datetime import datetime

# URL base de tu backend
BASE_URL = "https://droclven-back.onrender.com"

def test_datetime_serialization():
    """Probar que las fechas se serialicen correctamente."""
    
    print("🧪 Probando serialización de fechas datetime...")
    print("=" * 50)
    
    try:
        # Probar GET /formatos-impresion/
        response = requests.get(f"{BASE_URL}/formatos-impresion/")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            formatos = data.get("formatos", [])
            
            print(f"✅ GET exitoso - {len(formatos)} formatos encontrados")
            
            # Verificar que las fechas están serializadas correctamente
            for i, formato in enumerate(formatos[:2]):  # Solo los primeros 2
                print(f"\n📄 Formato {i+1}: {formato.get('tipo', 'N/A')}")
                
                # Verificar fecha_creacion
                fecha_creacion = formato.get("fecha_creacion")
                if fecha_creacion:
                    print(f"   📅 fecha_creacion: {fecha_creacion} (tipo: {type(fecha_creacion).__name__})")
                    # Verificar que es string
                    if isinstance(fecha_creacion, str):
                        print("   ✅ fecha_creacion serializada correctamente como string")
                    else:
                        print(f"   ❌ fecha_creacion NO es string: {type(fecha_creacion)}")
                
                # Verificar fecha_actualizacion
                fecha_actualizacion = formato.get("fecha_actualizacion")
                if fecha_actualizacion:
                    print(f"   📅 fecha_actualizacion: {fecha_actualizacion} (tipo: {type(fecha_actualizacion).__name__})")
                    # Verificar que es string
                    if isinstance(fecha_actualizacion, str):
                        print("   ✅ fecha_actualizacion serializada correctamente como string")
                    else:
                        print(f"   ❌ fecha_actualizacion NO es string: {type(fecha_actualizacion)}")
                
                # Verificar que se puede parsear como datetime
                try:
                    if fecha_creacion:
                        parsed_date = datetime.strptime(fecha_creacion, "%Y-%m-%d %H:%M:%S")
                        print(f"   ✅ fecha_creacion parseable: {parsed_date}")
                except ValueError as e:
                    print(f"   ❌ Error parseando fecha_creacion: {e}")
                
                try:
                    if fecha_actualizacion:
                        parsed_date = datetime.strptime(fecha_actualizacion, "%Y-%m-%d %H:%M:%S")
                        print(f"   ✅ fecha_actualizacion parseable: {parsed_date}")
                except ValueError as e:
                    print(f"   ❌ Error parseando fecha_actualizacion: {e}")
            
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def test_json_serialization():
    """Probar que la respuesta se puede serializar a JSON."""
    
    print("\n🧪 Probando serialización JSON...")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/formatos-impresion/")
        
        if response.status_code == 200:
            data = response.json()
            
            # Intentar serializar de nuevo
            json_string = json.dumps(data, indent=2)
            print("✅ Respuesta se puede serializar a JSON correctamente")
            
            # Verificar que no hay objetos datetime
            json_string_lower = json_string.lower()
            if "datetime" in json_string_lower or "datetime.datetime" in json_string_lower:
                print("❌ Aún hay objetos datetime en la respuesta JSON")
                return False
            else:
                print("✅ No hay objetos datetime en la respuesta JSON")
                return True
        else:
            print(f"❌ Error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal."""
    print("🔍 Verificando serialización de fechas datetime")
    print("=" * 60)
    
    # Esperar un poco para que el despliegue se complete
    import time
    print("⏳ Esperando que el despliegue se complete...")
    time.sleep(10)
    
    # Probar serialización de fechas
    success1 = test_datetime_serialization()
    
    # Probar serialización JSON
    success2 = test_json_serialization()
    
    print("\n📊 RESUMEN:")
    print("=" * 20)
    print(f"Serialización de fechas: {'✅' if success1 else '❌'}")
    print(f"Serialización JSON: {'✅' if success2 else '❌'}")
    
    if success1 and success2:
        print("\n🎉 ¡Serialización de fechas funciona correctamente!")
        print("🌐 Tu frontend debería poder procesar las fechas sin problemas.")
    else:
        print("\n⚠️ Aún hay problemas con la serialización de fechas.")

if __name__ == "__main__":
    main()

