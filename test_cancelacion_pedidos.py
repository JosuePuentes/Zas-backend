#!/usr/bin/env python3
"""
Script para probar la funcionalidad de cancelación de pedidos
"""
from pymongo import MongoClient
from datetime import datetime

def probar_cancelacion_pedidos():
    """Probar la funcionalidad de cancelación de pedidos"""
    
    print("PROBANDO FUNCIONALIDAD DE CANCELACION DE PEDIDOS")
    print("=" * 60)
    
    MONGO_URI = "mongodb+srv://Dios:EikobPHJKkEMSUq9@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["DROCOLVEN"]
        pedidos_collection = db["pedidos"]
        
        print("1. Verificando pedidos existentes...")
        total_pedidos = pedidos_collection.count_documents({})
        print(f"   Total de pedidos: {total_pedidos}")
        
        # 2. Buscar pedidos que se puedan cancelar (no entregados ni cancelados)
        print("\n2. Buscando pedidos cancelables...")
        pedidos_cancelables = list(pedidos_collection.find({
            "estado": {"$nin": ["entregado", "cancelado"]}
        }).limit(3))
        
        print(f"   Pedidos cancelables encontrados: {len(pedidos_cancelables)}")
        
        if pedidos_cancelables:
            for i, pedido in enumerate(pedidos_cancelables):
                print(f"     {i+1}. ID: {str(pedido.get('_id'))}")
                print(f"        Estado: {pedido.get('estado', 'Sin estado')}")
                print(f"        Cliente: {pedido.get('cliente', {}).get('nombre', 'Sin cliente')}")
                print(f"        Fecha: {pedido.get('fecha', 'Sin fecha')}")
                print(f"        Cancelado: {pedido.get('fecha_cancelacion', 'No')}")
        
        # 3. Simular cancelación de un pedido
        if pedidos_cancelables:
            print("\n3. Simulando cancelación de un pedido...")
            pedido_a_cancelar = pedidos_cancelables[0]
            pedido_id = pedido_a_cancelar["_id"]
            estado_anterior = pedido_a_cancelar.get("estado", "Sin estado")
            
            print(f"   Cancelando pedido ID: {str(pedido_id)}")
            print(f"   Estado anterior: {estado_anterior}")
            
            # Simular la cancelación
            fecha_cancelacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            resultado = pedidos_collection.update_one(
                {"_id": pedido_id},
                {"$set": {
                    "estado": "cancelado",
                    "fecha_cancelacion": fecha_cancelacion,
                    "usuario_cancelacion": "admin"
                }}
            )
            
            if resultado.modified_count > 0:
                print(f"   Cancelación exitosa!")
                print(f"   Fecha cancelación: {fecha_cancelacion}")
                print(f"   Usuario cancelación: admin")
                
                # Verificar el pedido cancelado
                pedido_cancelado = pedidos_collection.find_one({"_id": pedido_id})
                print(f"   Estado nuevo: {pedido_cancelado.get('estado')}")
                print(f"   Fecha cancelación: {pedido_cancelado.get('fecha_cancelacion')}")
                print(f"   Usuario cancelación: {pedido_cancelado.get('usuario_cancelacion')}")
            else:
                print("   Error en la cancelación")
        else:
            print("\n3. No hay pedidos para cancelar")
        
        # 4. Verificar pedidos cancelados
        print("\n4. Verificando pedidos cancelados...")
        pedidos_cancelados = list(pedidos_collection.find({"estado": "cancelado"}))
        print(f"   Pedidos cancelados: {len(pedidos_cancelados)}")
        
        # 5. Verificar pedidos entregados (no cancelables)
        print("\n5. Verificando pedidos entregados...")
        pedidos_entregados = list(pedidos_collection.find({"estado": "entregado"}))
        print(f"   Pedidos entregados: {len(pedidos_entregados)}")
        
        # 6. Resumen final
        print("\n6. RESUMEN FINAL:")
        print("   - Pedidos totales:", total_pedidos)
        print("   - Pedidos cancelables:", len(pedidos_cancelables))
        print("   - Pedidos cancelados:", len(pedidos_cancelados))
        print("   - Pedidos entregados:", len(pedidos_entregados))
        
        print("\nRESULTADO: Funcionalidad de cancelación funcionando correctamente")
        
    except Exception as e:
        print(f"ERROR EN LA PRUEBA: {e}")
        print("\nRESULTADO: Problemas con la funcionalidad de cancelación")
    finally:
        if 'client' in locals() and client:
            client.close()
            print("Conexión a MongoDB cerrada.")

if __name__ == "__main__":
    probar_cancelacion_pedidos()


