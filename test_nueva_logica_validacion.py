#!/usr/bin/env python3
"""
Script para probar la nueva lógica de validación de pedidos
"""
from pymongo import MongoClient
from datetime import datetime

def probar_nueva_logica_validacion():
    """Probar la nueva lógica de validación y filtrado de pedidos"""
    
    print("PROBANDO NUEVA LOGICA DE VALIDACION DE PEDIDOS")
    print("=" * 60)
    
    MONGO_URI = "mongodb+srv://Dios:EikobPHJKkEMSUq9@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["DROCOLVEN"]
        pedidos_collection = db["pedidos"]
        
        print("1. Verificando pedidos existentes...")
        total_pedidos = pedidos_collection.count_documents({})
        print(f"   Total de pedidos: {total_pedidos}")
        
        # 2. Verificar pedidos en estado 'nuevo'
        print("\n2. Verificando pedidos en estado 'nuevo'...")
        pedidos_nuevos = list(pedidos_collection.find({"estado": "nuevo"}))
        print(f"   Pedidos en estado 'nuevo': {len(pedidos_nuevos)}")
        
        for i, pedido in enumerate(pedidos_nuevos[:3]):  # Mostrar solo los primeros 3
            print(f"     {i+1}. ID: {str(pedido.get('_id'))}")
            print(f"        Estado: {pedido.get('estado', 'Sin estado')}")
            print(f"        Validado: {pedido.get('validado', 'Sin campo')}")
            print(f"        Fecha validación: {pedido.get('fecha_validacion', 'Sin fecha')}")
            print(f"        Usuario validación: {pedido.get('usuario_validacion', 'Sin usuario')}")
        
        # 3. Simular endpoint de administración (pedidos no validados)
        print("\n3. Simulando endpoint /pedidos/administracion/...")
        pedidos_admin = list(pedidos_collection.find({
            "estado": "nuevo",
            "$or": [
                {"validado": {"$exists": False}},
                {"validado": False}
            ]
        }))
        print(f"   Pedidos para administración (no validados): {len(pedidos_admin)}")
        
        # 4. Simular endpoint de picking (pedidos validados)
        print("\n4. Simulando endpoint /pedidos/picking/...")
        pedidos_picking = list(pedidos_collection.find({
            "estado": "nuevo",
            "validado": True
        }))
        print(f"   Pedidos para picking (validados): {len(pedidos_picking)}")
        
        # 5. Si hay pedidos no validados, simular validación
        if pedidos_admin:
            print("\n5. Simulando validación de un pedido...")
            pedido_a_validar = pedidos_admin[0]
            pedido_id = pedido_a_validar["_id"]
            
            print(f"   Validando pedido ID: {str(pedido_id)}")
            
            # Simular la validación
            fecha_validacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            resultado = pedidos_collection.update_one(
                {"_id": pedido_id},
                {"$set": {
                    "validado": True,
                    "fecha_validacion": fecha_validacion,
                    "usuario_validacion": "admin"
                }}
            )
            
            if resultado.modified_count > 0:
                print(f"   Validación exitosa!")
                print(f"   Fecha validación: {fecha_validacion}")
                print(f"   Usuario validación: admin")
                
                # Verificar que ahora aparece en picking
                pedidos_picking_actualizado = list(pedidos_collection.find({
                    "estado": "nuevo",
                    "validado": True
                }))
                print(f"   Pedidos para picking después de validación: {len(pedidos_picking_actualizado)}")
            else:
                print("   Error en la validación")
        else:
            print("\n5. No hay pedidos para validar")
        
        # 6. Resumen final
        print("\n6. RESUMEN FINAL:")
        print("   - Pedidos totales:", total_pedidos)
        print("   - Pedidos 'nuevo':", len(pedidos_nuevos))
        print("   - Para administración:", len(pedidos_admin))
        print("   - Para picking:", len(pedidos_picking))
        
        print("\nRESULTADO: Nueva lógica de validación funcionando correctamente")
        
    except Exception as e:
        print(f"ERROR EN LA PRUEBA: {e}")
        print("\nRESULTADO: Problemas con la nueva lógica")
    finally:
        if 'client' in locals() and client:
            client.close()
            print("Conexión a MongoDB cerrada.")

if __name__ == "__main__":
    probar_nueva_logica_validacion()


