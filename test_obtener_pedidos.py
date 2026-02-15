#!/usr/bin/env python3
"""
Script para probar el endpoint obtener_pedidos corregido
"""
from pymongo import MongoClient

def probar_obtener_pedidos():
    """Probar la consulta de pedidos directamente en MongoDB"""
    
    print("PROBANDO CONSULTA DE PEDIDOS")
    print("=" * 50)
    
    MONGO_URI = "mongodb+srv://Dios:EikobPHJKkEMSUq9@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["DROCOLVEN"]
        pedidos_collection = db["PEDIDOS"]
        
        print("1. Contando total de pedidos...")
        total_pedidos = pedidos_collection.count_documents({})
        print(f"   Total de pedidos: {total_pedidos}")
        
        print("\n2. Probando consulta sin filtros...")
        query_filter = {}
        pedidos = list(pedidos_collection.find(query_filter).limit(5))
        print(f"   Pedidos encontrados: {len(pedidos)}")
        
        if pedidos:
            print("   Primeros pedidos:")
            for i, pedido in enumerate(pedidos[:3]):
                print(f"     {i+1}. ID: {pedido.get('_id')}")
                print(f"        Estado: {pedido.get('estado', 'Sin estado')}")
                print(f"        Cliente: {pedido.get('cliente_nombre', 'Sin cliente')}")
                print(f"        Fecha: {pedido.get('fecha_creacion', 'Sin fecha')}")
                print()
        
        print("3. Probando consulta por estados específicos...")
        estados_test = ["pendiente", "armado", "enviado"]
        query_filter = {"estado": {"$in": estados_test}}
        pedidos_estado = list(pedidos_collection.find(query_filter).limit(3))
        print(f"   Pedidos con estados {estados_test}: {len(pedidos_estado)}")
        
        print("4. Verificando estructura de pedidos...")
        if pedidos:
            primer_pedido = pedidos[0]
            print("   Campos disponibles en el primer pedido:")
            for campo in sorted(primer_pedido.keys()):
                print(f"     - {campo}: {type(primer_pedido[campo]).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    finally:
        client.close()
        print("\nConexión a MongoDB cerrada.")

if __name__ == "__main__":
    exito = probar_obtener_pedidos()
    if exito:
        print("\n✅ RESULTADO: Consulta de pedidos funcionando correctamente.")
    else:
        print("\n❌ RESULTADO: Problemas con la consulta de pedidos.")


