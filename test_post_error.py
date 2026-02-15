#!/usr/bin/env python3
"""
Script para probar el endpoint POST de formatos de impresión y diagnosticar el error 400.
"""

import requests
import json
import sys

# URL base de tu backend
BASE_URL = "https://droclven-back.onrender.com"

def test_post_formato():
    """Probar el endpoint POST con diferentes tipos de datos."""
    
    headers = {
        "Content-Type": "application/json",
    }
    
    # Datos de prueba que deberían funcionar
    datos_prueba = {
        "tipo": "factura_test",
        "datos_empresa": {
            "nombre": "FARMA AMERICA (DANIEL)",
            "rif": "J-12345678-9",
            "telefono": "+58 212 123-4567",
            "email": "info@farmaamerica.com",
            "web": "www.farmaamerica.com",
            "direccion": "Av. Principal, Edificio Farma, Piso 3, Caracas, Venezuela",
            "ciudad": "Caracas",
            "estado": "Distrito Capital",
            "codigo_postal": "1010"
        },
        "configuracion_diseno": {
            "mostrar_logo": True,
            "mostrar_direccion": True,
            "mostrar_telefono": True,
            "mostrar_email": True,
            "mostrar_web": False,
            "color_principal": "#1e40af",
            "color_secundario": "#64748b",
            "fuente_titulo": "bold",
            "fuente_texto": "normal",
            "tamaño_fuente": "12px",
            "espaciado": "normal",
            "margen_superior": "20px",
            "margen_inferior": "20px",
            "margen_izquierdo": "20px",
            "margen_derecho": "20px"
        },
        "plantilla_html": "",
        "campos_dinamicos": {
            "mostrar_fecha": True,
            "mostrar_numero_factura": True,
            "mostrar_cliente": True,
            "mostrar_productos": True,
            "mostrar_totales": True,
            "mostrar_observaciones": True,
            "formato_fecha": "DD/MM/YYYY",
            "formato_moneda": "Bs.",
            "decimales": 2
        },
        "activo": True,
        "usuario_creacion": "test_user"
    }
    
    print("🧪 Probando endpoint POST /formatos-impresion/")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/formatos-impresion/",
            json=datos_prueba,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ POST exitoso!")
            try:
                data = response.json()
                print(f"Respuesta: {json.dumps(data, indent=2)}")
            except:
                print(f"Respuesta: {response.text}")
        else:
            print(f"❌ Error {response.status_code}")
            print(f"Respuesta: {response.text}")
            
            # Intentar parsear el error
            try:
                error_data = response.json()
                print(f"Error detallado: {json.dumps(error_data, indent=2)}")
            except:
                pass
        
        return response.status_code < 400
        
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def test_minimal_post():
    """Probar con datos mínimos requeridos."""
    
    headers = {
        "Content-Type": "application/json",
    }
    
    # Datos mínimos
    datos_minimos = {
        "tipo": "test_minimal"
    }
    
    print("\n🧪 Probando POST con datos mínimos")
    print("=" * 40)
    
    try:
        response = requests.post(
            f"{BASE_URL}/formatos-impresion/",
            json=datos_minimos,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {response.text}")
        
        return response.status_code < 400
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal."""
    print("🔍 Diagnosticando error 400 en POST /formatos-impresion/")
    print("=" * 60)
    
    # Probar con datos completos
    success1 = test_post_formato()
    
    # Probar con datos mínimos
    success2 = test_minimal_post()
    
    print("\n📊 RESUMEN:")
    print("=" * 20)
    print(f"POST completo: {'✅' if success1 else '❌'}")
    print(f"POST mínimo: {'✅' if success2 else '❌'}")
    
    if not success1 and not success2:
        print("\n💡 Posibles causas del error 400:")
        print("   • Validación de datos fallando")
        print("   • Campos requeridos faltantes")
        print("   • Formato de datos incorrecto")
        print("   • Problema con el modelo Pydantic")

if __name__ == "__main__":
    main()

