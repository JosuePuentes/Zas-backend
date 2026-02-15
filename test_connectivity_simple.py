#!/usr/bin/env python3
"""
Script para probar la conectividad del backend
"""
import requests
import json
from datetime import datetime

def test_backend_connectivity():
    """Prueba la conectividad con el backend"""
    
    # URLs base para probar
    base_urls = [
        "https://droclven-back.onrender.com",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    endpoints_to_test = [
        "/inventario/",
        "/inventario_maestro/",
        "/pedidos/",
        "/clientes/",
        "/auth/login/"
    ]
    
    print("Probando conectividad del backend...")
    print("=" * 50)
    
    for base_url in base_urls:
        print(f"\nProbando: {base_url}")
        print("-" * 30)
        
        try:
            # Probar endpoint raíz
            response = requests.get(f"{base_url}/", timeout=10)
            print(f"Root endpoint: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Root endpoint: Error - {e}")
            continue
        
        # Probar endpoints específicos
        for endpoint in endpoints_to_test:
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"OK {endpoint}: {response.status_code}")
                    # Mostrar una muestra de la respuesta para inventario
                    if endpoint == "/inventario/":
                        try:
                            data = response.json()
                            if "inventario" in data:
                                print(f"   Productos encontrados: {len(data['inventario'])}")
                            else:
                                print(f"   Estructura inesperada: {list(data.keys())}")
                        except:
                            print(f"   Respuesta no es JSON válido")
                elif response.status_code == 404:
                    print(f"ERROR {endpoint}: 404 - No encontrado")
                elif response.status_code == 405:
                    print(f"WARNING {endpoint}: 405 - Método no permitido (esperado para algunos endpoints)")
                else:
                    print(f"WARNING {endpoint}: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"ERROR {endpoint}: Error - {e}")

def test_cors_headers():
    """Prueba los headers CORS"""
    print("\nProbando headers CORS...")
    print("=" * 50)
    
    test_url = "https://droclven-back.onrender.com"
    
    try:
        # Hacer una petición OPTIONS para probar CORS
        response = requests.options(f"{test_url}/inventario/", timeout=10)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print("Headers CORS encontrados:")
        for header, value in cors_headers.items():
            if value:
                print(f"OK {header}: {value}")
            else:
                print(f"ERROR {header}: No encontrado")
                
    except requests.exceptions.RequestException as e:
        print(f"ERROR probando CORS: {e}")

if __name__ == "__main__":
    print(f"Iniciando pruebas de conectividad - {datetime.now()}")
    
    test_backend_connectivity()
    test_cors_headers()
    
    print("\n" + "=" * 50)
    print("Pruebas completadas")
    print("\nRecomendaciones:")
    print("1. Si el backend local funciona pero Render no, revisa los logs de Render")
    print("2. Si hay errores 404, verifica que las rutas estén correctamente registradas")
    print("3. Si hay errores CORS, verifica la configuración del middleware")
    print("4. Asegúrate de que el frontend esté apuntando a la URL correcta del backend")

