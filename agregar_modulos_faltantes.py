#!/usr/bin/env python3
"""
Script para agregar módulos faltantes a la base de datos
"""
from pymongo import MongoClient

def agregar_modulos_faltantes():
    """Agregar módulos que faltan en el panel de administración"""
    
    print("AGREGANDO MODULOS FALTANTES")
    print("=" * 50)
    
    # Variables de entorno proporcionadas
    MONGO_URI = "mongodb+srv://Dios:EikobPHJKkEMSUq9@cluster0.t4ykike.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        print("Conectando a MongoDB Atlas...")
        client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
        db = client["DROCOLVEN"]
        modulos_collection = db["modulos"]
        
        # Módulos que faltan específicamente
        modulos_faltantes = [
            {"name": "pedidos_enviados", "descripcion": "Pedidos enviados", "activo": True},
            {"name": "check_picking", "descripcion": "Verificación de picking", "activo": True},
            {"name": "facturacion", "descripcion": "Gestión de facturación", "activo": True},
            {"name": "reclamos", "descripcion": "Gestión de reclamos", "activo": True},
            {"name": "transacciones", "descripcion": "Gestión de transacciones", "activo": True},
            {"name": "contacto", "descripcion": "Gestión de contacto", "activo": True}
        ]
        
        print("Verificando módulos existentes...")
        modulos_existentes = list(modulos_collection.find())
        nombres_existentes = [modulo.get('name') for modulo in modulos_existentes]
        
        print(f"Módulos existentes: {len(modulos_existentes)}")
        for modulo in modulos_existentes:
            print(f"  - {modulo.get('name')}")
        
        # Filtrar módulos que realmente faltan
        modulos_a_agregar = []
        for modulo in modulos_faltantes:
            if modulo['name'] not in nombres_existentes:
                modulos_a_agregar.append(modulo)
                print(f"FALTA: {modulo['name']}")
            else:
                print(f"YA EXISTE: {modulo['name']}")
        
        if modulos_a_agregar:
            print(f"\nAgregando {len(modulos_a_agregar)} módulos faltantes...")
            resultado = modulos_collection.insert_many(modulos_a_agregar)
            print(f"OK Se agregaron {len(resultado.inserted_ids)} módulos nuevos")
            
            # Mostrar los módulos agregados
            print("\nMódulos agregados:")
            for modulo in modulos_a_agregar:
                print(f"  - {modulo['name']}: {modulo['descripcion']}")
        else:
            print("\nOK Todos los módulos ya existen")
        
        # Verificar el total final
        total_modulos = modulos_collection.count_documents({})
        print(f"\nTotal de módulos en la base de datos: {total_modulos}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    exito = agregar_modulos_faltantes()
    
    print("\n" + "=" * 50)
    if exito:
        print("RESULTADO: Módulos agregados exitosamente")
    else:
        print("RESULTADO: Error al agregar módulos")

