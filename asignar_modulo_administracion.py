#!/usr/bin/env python3
"""
Script para asignar el módulo administracion al usuario soporte2
"""
from pymongo import MongoClient

def asignar_modulo_administracion():
    """Asignar el módulo administracion al usuario soporte2"""
    
    print("ASIGNANDO MODULO ADMINISTRACION AL USUARIO SOPORTE2")
    print("=" * 60)
    
    MONGO_URI = "mongodb+srv://Dios:EikobPHJKkEMSUq9@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["DROCOLVEN"]
        modulos_collection = db["modulos"]
        usuarios_admin_collection = db["usuarios_admin"]
        
        print("1. Verificando que el módulo 'administracion' existe...")
        modulo_admin = modulos_collection.find_one({"name": "administracion"})
        
        if not modulo_admin:
            print("   ❌ ERROR: El módulo 'administracion' no existe")
            return False
        
        print(f"   ✅ Módulo encontrado:")
        print(f"      - ID: {modulo_admin['_id']}")
        print(f"      - Nombre: {modulo_admin['name']}")
        print(f"      - Descripción: {modulo_admin['descripcion']}")
        print(f"      - Activo: {modulo_admin['activo']}")
        
        print("\n2. Buscando usuario 'soporte2'...")
        usuario_soporte2 = usuarios_admin_collection.find_one({"usuario": "soporte2"})
        
        if not usuario_soporte2:
            print("   ❌ ERROR: Usuario 'soporte2' no encontrado")
            return False
        
        print(f"   ✅ Usuario encontrado:")
        print(f"      - ID: {usuario_soporte2['_id']}")
        print(f"      - Usuario: {usuario_soporte2['usuario']}")
        print(f"      - Módulos actuales: {usuario_soporte2.get('modulos', [])}")
        
        print("\n3. Verificando si ya tiene el módulo 'administracion'...")
        modulos_actuales = usuario_soporte2.get('modulos', [])
        
        if 'administracion' in modulos_actuales:
            print("   ✅ El usuario ya tiene el módulo 'administracion' asignado")
        else:
            print("   📝 Agregando módulo 'administracion' al usuario...")
            
            # Agregar el módulo administracion
            modulos_actuales.append('administracion')
            
            # Actualizar el usuario
            resultado = usuarios_admin_collection.update_one(
                {"usuario": "soporte2"},
                {"$set": {"modulos": modulos_actuales}}
            )
            
            if resultado.modified_count > 0:
                print("   ✅ Módulo 'administracion' asignado exitosamente")
            else:
                print("   ❌ Error al asignar el módulo")
                return False
        
        print("\n4. Verificando la asignación...")
        usuario_actualizado = usuarios_admin_collection.find_one({"usuario": "soporte2"})
        modulos_finales = usuario_actualizado.get('modulos', [])
        
        print(f"   📋 Módulos finales del usuario soporte2:")
        for i, modulo in enumerate(modulos_finales, 1):
            print(f"      {i}. {modulo}")
        
        print(f"\n   📊 Total de módulos: {len(modulos_finales)}")
        
        # Verificar que administracion está en la lista
        if 'administracion' in modulos_finales:
            print("   ✅ CONFIRMADO: El usuario soporte2 tiene acceso al módulo 'administracion'")
        else:
            print("   ❌ ERROR: El módulo 'administracion' no está asignado")
            return False
        
        print("\n5. Simulando respuesta de login...")
        print("   📋 Respuesta que debería devolver el endpoint de login:")
        print("   {")
        print(f'     "access_token": "jwt_token_aqui",')
        print(f'     "usuario": "soporte2",')
        print(f'     "modulos": {modulos_finales}')
        print("   }")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    finally:
        client.close()
        print("\nConexión a MongoDB cerrada.")

if __name__ == "__main__":
    exito = asignar_modulo_administracion()
    if exito:
        print("\n✅ RESULTADO: Módulo administracion asignado correctamente al usuario soporte2.")
        print("   Ahora el usuario soporte2 debería tener acceso al módulo administracion en el login.")
    else:
        print("\n❌ RESULTADO: Error al asignar el módulo administracion.")


