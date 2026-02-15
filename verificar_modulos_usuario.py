#!/usr/bin/env python3
"""
Script para verificar los módulos asignados a usuarios admin
"""
from pymongo import MongoClient

def verificar_modulos_usuario():
    """Verificar qué módulos tienen asignados los usuarios admin"""
    
    print("VERIFICANDO MODULOS DE USUARIOS ADMIN")
    print("=" * 50)
    
    MONGO_URI = "mongodb+srv://Dios:EikobPHJKkEMSUq9@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["DROCOLVEN"]
        usuarios_admin_collection = db["usuarios_admin"]
        modulos_collection = db["modulos"]
        
        # Verificar usuarios admin
        print("1. Usuarios admin encontrados:")
        usuarios = list(usuarios_admin_collection.find())
        for usuario in usuarios:
            print(f"   - Usuario: {usuario.get('usuario', 'Sin nombre')}")
            modulos_usuario = usuario.get('modulos', [])
            print(f"     Módulos asignados: {len(modulos_usuario)}")
            for modulo in modulos_usuario:
                print(f"       * {modulo}")
            print()
        
        # Verificar todos los módulos disponibles
        print("2. Todos los módulos disponibles:")
        todos_modulos = list(modulos_collection.find())
        print(f"   Total de módulos: {len(todos_modulos)}")
        for modulo in todos_modulos:
            print(f"   - {modulo.get('name', 'Sin nombre')}")
        
        # Comparar
        print("\n3. Análisis:")
        if usuarios:
            primer_usuario = usuarios[0]
            modulos_usuario = primer_usuario.get('modulos', [])
            nombres_modulos_disponibles = [m.get('name') for m in todos_modulos]
            
            print(f"   Usuario '{primer_usuario.get('usuario')}' tiene {len(modulos_usuario)} módulos")
            print(f"   Total de módulos disponibles: {len(nombres_modulos_disponibles)}")
            
            modulos_faltantes = []
            for modulo_disponible in nombres_modulos_disponibles:
                if modulo_disponible not in modulos_usuario:
                    modulos_faltantes.append(modulo_disponible)
            
            if modulos_faltantes:
                print(f"\n   Módulos faltantes para el usuario:")
                for modulo in modulos_faltantes:
                    print(f"   - {modulo}")
            else:
                print("\n   OK - El usuario tiene todos los módulos")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    verificar_modulos_usuario()

