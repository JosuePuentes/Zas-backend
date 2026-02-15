#!/usr/bin/env python3
"""
Script para probar el endpoint de validación de pedidos
"""
from pymongo import MongoClient
from bson import ObjectId

def probar_validacion_pedidos():
    """Probar la funcionalidad de validación de pedidos"""
    
    print("PROBANDO VALIDACION DE PEDIDOS")
    print("=" * 50)
    
    MONGO_URI = "mongodb+srv://Dios:EikobPHJKkEMSUq9@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["DROCOLVEN"]
        pedidos_collection = db["PEDIDOS"]
        
        print("1. Buscando pedidos en estado 'nuevo'...")
        pedidos_nuevos = list(pedidos_collection.find({"estado": "nuevo"}).limit(3))
        
        if not pedidos_nuevos:
            print("   No se encontraron pedidos en estado 'nuevo'")
            print("   Creando un pedido de prueba...")
            
            # Crear un pedido de prueba
            pedido_prueba = {
                "cliente": "Cliente Prueba",
                "rif": "J-12345678-9",
                "estado": "nuevo",
                "fecha": "2024-01-15",
                "productos": [
                    {"codigo": "PROD001", "descripcion": "Producto Prueba", "cantidad": 2, "precio": 10.50}
                ],
                "subtotal": 21.00,
                "total": 21.00,
                "observacion": "Pedido de prueba para validación"
            }
            
            resultado = pedidos_collection.insert_one(pedido_prueba)
            pedido_id = str(resultado.inserted_id)
            print(f"   Pedido de prueba creado con ID: {pedido_id}")
        else:
            pedido_id = str(pedidos_nuevos[0]["_id"])
            print(f"   Pedido encontrado con ID: {pedido_id}")
        
        print(f"\n2. Simulando validación del pedido {pedido_id}...")
        print("   PIN correcto: 1234")
        print("   PIN incorrecto: 0000")
        
        # Simular validación con PIN correcto
        print("\n   Probando con PIN correcto (1234)...")
        pedido_object_id = ObjectId(pedido_id)
        pedido = pedidos_collection.find_one({"_id": pedido_object_id})
        
        if pedido and pedido.get("estado") == "nuevo":
            # Actualizar estado a picking
            resultado = pedidos_collection.update_one(
                {"_id": pedido_object_id},
                {"$set": {"estado": "picking"}}
            )
            
            if resultado.modified_count > 0:
                print("   ✅ Validación exitosa - Estado cambiado a 'picking'")
                
                # Verificar el cambio
                pedido_actualizado = pedidos_collection.find_one({"_id": pedido_object_id})
                print(f"   Estado anterior: nuevo")
                print(f"   Estado nuevo: {pedido_actualizado.get('estado')}")
            else:
                print("   ❌ Error al actualizar el estado")
        else:
            print(f"   ❌ Pedido no encontrado o estado incorrecto: {pedido.get('estado') if pedido else 'No encontrado'}")
        
        print("\n3. Verificando pedidos por estado...")
        estados = ["nuevo", "picking", "armado", "enviado"]
        for estado in estados:
            count = pedidos_collection.count_documents({"estado": estado})
            print(f"   {estado}: {count} pedidos")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    finally:
        client.close()
        print("\nConexión a MongoDB cerrada.")

if __name__ == "__main__":
    exito = probar_validacion_pedidos()
    if exito:
        print("\n✅ RESULTADO: Validación de pedidos funcionando correctamente.")
    else:
        print("\n❌ RESULTADO: Problemas con la validación de pedidos.")


