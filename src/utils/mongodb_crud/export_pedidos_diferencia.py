import os
from pymongo import MongoClient, errors
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de conexión
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("La variable de entorno MONGO_URI no está definida.")


# Parámetros de búsqueda
RIFS = [
    "J296449546",
    # Agrega aquí los RIFs que necesites
]
FECHA_INICIO = input("Ingrese la fecha de inicio (YYYY-MM-DD): ").strip()
FECHA_FIN = input("Ingrese la fecha de fin (YYYY-MM-DD): ").strip()

try:
    client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
    db = client["DROCOLVEN"]
    
    # Convertir fechas a string para comparar solo la parte de la fecha
    fecha_inicio_str = FECHA_INICIO
    fecha_fin_str = FECHA_FIN

    for RIF in RIFS:
        pedidos_cursor = db["PEDIDOS"].find({
            "rif": RIF,
            "$expr": {
                "$and": [
                    {"$gte": [{"$substr": ["$fecha", 0, 10]}, fecha_inicio_str]},
                    {"$lte": [{"$substr": ["$fecha", 0, 10]}, fecha_fin_str]}
                ]
            }
        })
        pedidos = list(pedidos_cursor)

        if not pedidos:
            print(f"No se encontraron pedidos para el RIF '{RIF}' en el rango de fechas especificado.")
            continue
        # Exportar resultados en formato CSV para Excel
        with open(f"export_pedidos_{RIF}.csv", "w", encoding="utf-8") as f:
            f.write("rif;pedido_id;fecha_pedido;estado_pedido;codigo;nombre;cantidad_encontrada;cantidad_pedida;diferencia\n")
            for pedido in pedidos:
                pedido_id = str(pedido.get("_id", ""))
                fecha_pedido = pedido.get("fecha", "")
                estado_pedido = pedido.get("estado", "")
                cliente = pedido.get("cliente", "")
                # Fila de encabezado por pedido con nombre del cliente
                f.write(f"PEDIDO: {pedido_id};CLIENTE: {cliente};FECHA: {fecha_pedido};ESTADO: {estado_pedido}\n")
                productos = pedido.get("productos", [])
                for prod in productos:
                    codigo = prod.get("codigo", "")
                    nombre = prod.get("nombre", prod.get("descripcion", ""))
                    cantidad_encontrada = prod.get("cantidad_encontrada", 0)
                    cantidad_pedida = prod.get("cantidad_pedida", 0)
                    diferencia = cantidad_encontrada - cantidad_pedida
                    f.write(f"{RIF};{pedido_id};{fecha_pedido};{estado_pedido};{codigo};{nombre};{cantidad_encontrada};{cantidad_pedida};{diferencia}\n")
        print(f"Exportación completada en export_pedidos_{RIF}.csv")
except errors.PyMongoError as e:
    print(f"Error de conexión o consulta: {e}")
except Exception as ex:
    print(f"Error: {ex}")
