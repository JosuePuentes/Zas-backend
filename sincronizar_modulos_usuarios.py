#!/usr/bin/env python3
"""
Script para sincronizar módulos de usuarios con los módulos disponibles
"""
from pymongo import MongoClient

def sincronizar_modulos_usuarios():
    """Sincronizar módulos de usuarios con los módulos disponibles"""
    
    print("SINCRONIZANDO MODULOS DE USUARIOS")
    print("=" * 50)
    
    MONGO_URI = "mongodb+srv://Dios:EikobPHJKkEMSUq9@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["DROCOLVEN"]
        usuarios_admin_collection = db["usuarios_admin"]
        modulos_collection = db["modulos"]
        
        # Obtener todos los módulos disponibles
        todos_modulos = list(modulos_collection.find())
        nombres_modulos_disponibles = [m.get('name') for m in todos_modulos]
        
        print(f"Módulos disponibles: {len(nombres_modulos_disponibles)}")
        for modulo in nombres_modulos_disponibles:
            print(f"  - {modulo}")
        
        # Mapeo de módulos antiguos a nuevos
        mapeo_modulos = {
            "envios": "envio",
            "checkpicking": "check_picking", 
            "admin-pedidos": "pedidos_enviados",
            "crear-clientes": "clientes",
            "info-pedidos": "info-pedido",
            "vistapedidos": "pedidos",
            "pendientes": "pedidos"
        }
        
        # Actualizar usuarios
        usuarios = list(usuarios_admin_collection.find())
        usuarios_actualizados = 0
        
        for usuario in usuarios:
            usuario_nombre = usuario.get('usuario', 'Sin nombre')
            modulos_actuales = usuario.get('modulos', [])
            
            print(f"\nProcesando usuario: {usuario_nombre}")
            print(f"  Módulos actuales: {len(modulos_actuales)}")
            
            # Aplicar mapeo y agregar módulos faltantes
            modulos_nuevos = []
            
            for modulo in modulos_actuales:
                # Aplicar mapeo si existe
                modulo_mapeado = mapeo_modulos.get(modulo, modulo)
                
                # Si el módulo mapeado existe en los disponibles, agregarlo
                if modulo_mapeado in nombres_modulos_disponibles:
                    if modulo_mapeado not in modulos_nuevos:
                        modulos_nuevos.append(modulo_mapeado)
                # Si el módulo original existe, mantenerlo
                elif modulo in nombres_modulos_disponibles:
                    if modulo not in modulos_nuevos:
                        modulos_nuevos.append(modulo)
            
            # Agregar módulos faltantes para usuarios específicos
            if usuario_nombre in ["soporte2", "anubis"]:  # Usuarios admin completos
                for modulo_disponible in nombres_modulos_disponibles:
                    if modulo_disponible not in modulos_nuevos:
                        modulos_nuevos.append(modulo_disponible)
            
            # Actualizar si hay cambios
            if set(modulos_nuevos) != set(modulos_actuales):
                usuarios_admin_collection.update_one(
                    {"_id": usuario["_id"]},
                    {"$set": {"modulos": modulos_nuevos}}
                )
                print(f"  ACTUALIZADO: {len(modulos_nuevos)} módulos")
                usuarios_actualizados += 1
            else:
                print(f"  SIN CAMBIOS: {len(modulos_nuevos)} módulos")
        
        print(f"\nRESULTADO:")
        print(f"  Usuarios actualizados: {usuarios_actualizados}")
        print(f"  Total de usuarios: {len(usuarios)}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    exito = sincronizar_modulos_usuarios()
    
    if exito:
        print("\nOK - Módulos de usuarios sincronizados correctamente")
    else:
        print("\nERROR - Problema al sincronizar módulos")


