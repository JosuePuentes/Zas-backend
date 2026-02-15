#!/usr/bin/env python3
"""
Script para probar los endpoints de formatos de impresión.
"""

import requests
import json
import sys

# URL base de tu backend
BASE_URL = "https://droclven-back.onrender.com"

def test_endpoint(method, endpoint, data=None, headers=None):
    """Probar un endpoint específico."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"❌ Método HTTP no soportado: {method}")
            return False
        
        print(f"🔍 {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   ✅ Éxito")
            if response.content:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'formatos' in data:
                        print(f"   📊 Formatos encontrados: {len(data['formatos'])}")
                    elif isinstance(data, dict) and 'tipo' in data:
                        print(f"   📄 Formato: {data['tipo']}")
                except:
                    print(f"   📝 Respuesta: {response.text[:100]}...")
        else:
            print(f"   ❌ Error: {response.text}")
        
        print()
        return response.status_code < 400
        
    except Exception as e:
        print(f"❌ Error al probar {method} {endpoint}: {e}")
        print()
        return False

def main():
    """Probar todos los endpoints de formatos de impresión."""
    print("🧪 Probando endpoints de formatos de impresión...")
    print("=" * 60)
    
    # Headers para autenticación (si es necesaria)
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer tu_token_aqui"  # Descomenta si necesitas autenticación
    }
    
    # Lista de endpoints a probar
    tests = [
        ("GET", "/formatos-impresion/"),
        ("GET", "/formatos-impresion/factura_preliminar"),
        ("GET", "/formatos-impresion/factura_final"),
        ("GET", "/formatos-impresion/etiqueta_envio"),
        ("GET", "/formatos-impresion/factura_preliminar/preview"),
    ]
    
    # Probar cada endpoint
    resultados = []
    for method, endpoint in tests:
        resultado = test_endpoint(method, endpoint, headers=headers)
        resultados.append(resultado)
    
    # Resumen
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 30)
    exitosos = sum(resultados)
    total = len(resultados)
    
    print(f"✅ Exitosos: {exitosos}/{total}")
    print(f"❌ Fallidos: {total - exitosos}/{total}")
    
    if exitosos == total:
        print("\n🎉 ¡Todos los endpoints funcionan correctamente!")
        print("🌐 Tu frontend debería poder conectarse sin problemas.")
    else:
        print(f"\n⚠️ {total - exitosos} endpoints tienen problemas.")
        print("🔧 Revisa la configuración del servidor.")
    
    return exitosos == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

