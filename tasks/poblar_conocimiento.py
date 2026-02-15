# poblar_conocimiento.py

import os
import google.generativeai as genai
from pymongo import MongoClient
import time
from typing import Dict, Any, Optional, List 

# ===============================================
#          ¡CONFIGURACIÓN PARA RENDER!
# ===============================================
# Ahora lee las claves de las Variables de Entorno de Render
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") 
MONGO_URI = os.environ.get("MONGO_URI") 
DB_NAME = os.environ.get("DB_NAME")

# Verificar que las variables de entorno estén definidas
if not GOOGLE_API_KEY:
    print("❌ Error: GOOGLE_API_KEY no está definida en las variables de entorno")
    exit(1)
    
if not MONGO_URI:
    print("❌ Error: MONGO_URI no está definida en las variables de entorno")
    exit(1)
    
if not DB_NAME:
    print("❌ Error: DB_NAME no está definida en las variables de entorno")
    exit(1)

print("✅ Variables de entorno cargadas correctamente")
print(f"   GOOGLE_API_KEY: {'*' * 20}...{GOOGLE_API_KEY[-4:] if len(GOOGLE_API_KEY) > 4 else '****'}")
print(f"   MONGO_URI: {MONGO_URI[:30]}...")
print(f"   DB_NAME: {DB_NAME}")
# ===============================================


# --- Configuración Base y Conexiones ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    # Colección que centralizará todo el conocimiento
    coleccion_destino = db["conocimiento_ia"] 
except Exception as e:
    print(f"Error de conexión o configuración inicial: {e}")
    # Si la conexión falla, detenemos el script
    exit()


# --- Función de Vectorización (Google) ---
def get_embedding(text: str, model: str = "models/text-embedding-004") -> List[float]:
   """Llama a la API de Google para obtener el vector (embedding) de un texto."""
   text = text.replace("\n", " ")
   return genai.embed_content(model=model,
                              content=text,
                              task_type="RETRIEVAL_DOCUMENT")["embedding"]


# --- Función para Resumir y Crear Texto de Conocimiento ---
def crear_texto_resumen(documento: Dict[str, Any], nombre_coleccion: str) -> Optional[str]:
    """Traduce un documento de cualquier colección a un párrafo de texto para la IA."""
    
    # --- Lógica para CLIENTES ---
    if nombre_coleccion == "CLIENTES":
        nombre = documento.get("descripcion", "N/A") 
        rif = documento.get("rif", "N/A")
        telefono = documento.get("telefono", "N/A")
        limite_credito = documento.get("limite_credito", 0)
        return f"DATOS DE CLIENTE: {nombre} (RIF: {rif}). Teléfono: {telefono}. Límite de crédito: {limite_credito}."

    # --- Lógica para PEDIDOS (¡Corregida con tus nombres de campo!) ---
    elif nombre_coleccion == "PEDIDOS":
        # Nombres de campos confirmados en tu DB
        nombre_cliente = documento.get("cliente", "N/A")
        rif_ped = documento.get("rif", "N/A")         # <-- ¡CORREGIDO a 'rif'!
        total = documento.get("total", 0.0)
        fecha = documento.get("fecha", "Sin fecha")
        estado_actual = documento.get("estado", "N/A") # <-- ¡CORREGIDO a 'estado'!

        # El texto de resumen es ahora muy claro para el conteo de estados
        return (f"REGISTRO DE PEDIDO: Pedido para el cliente {nombre_cliente} (RIF: {rif_ped}). "
                f"Total: {total} USD. Estado del Pedido: {estado_actual}. "
                f"Fecha: {fecha}. Este documento está en el estado de {estado_actual}.") # <-- Repetimos el estado para reforzar el vector

    # LA LÓGICA DE INVENTARIO FUE MOVIDA A LA FUNCIÓN poblar_enciclopedia
    
    else:
        return None


# --- SCRIPT PRINCIPAL ---
def poblar_enciclopedia():
    """Ejecuta el proceso de vectorización para todas las colecciones fuente."""
    
    # Lista de TODAS las colecciones que Dona debe aprender
    colecciones_fuente = [
        "CLIENTES", 
        "PEDIDOS", 
        "INVENTARIO" # Ahora la lógica está aquí abajo
    ]

    for nombre_col in colecciones_fuente:
        print(f"--- Procesando colección: {nombre_col} ---")
        coleccion_fuente = db[nombre_col]
        
        for doc in coleccion_fuente.find():
            
            # 1. 🛑 LÓGICA ESPECIAL PARA EL INVENTARIO ANIDADO
            if nombre_col == "INVENTARIO":
                if "inventario" in doc and isinstance(doc["inventario"], list):
                    
                    for producto in doc["inventario"]:
                        # 1.1 Extraer los campos confirmados por el usuario
                        nombre = producto.get("descripcion", "N/A") 
                        codigo = producto.get("codigo", "N/A")
                        cantidad = producto.get("existencia", 0) 
                        precio_venta = producto.get("precio", 0.0) # <--- ¡EL PRECIO CORRECTO!
                        
                        # 1.2 Crear el texto resumen (El texto de conocimiento)
                        texto_resumen = f"DATOS DE INVENTARIO: Artículo {nombre} (Código: {codigo}). Stock: {cantidad}. Precio de venta: {precio_venta} USD. Laboratorio: {producto.get('laboratorio', 'N/A')}."
                        
                        # 1.3 Crear un ID único para cada producto (Padre ID + Código de Producto)
                        unique_id = f"INV_{doc['_id']}_{codigo}"

                        # 1.4 Vectorizar e Insertar el PRODUCTO INDIVIDUAL
                        try:
                            vector_resumen = get_embedding(texto_resumen)
                            documento_conocimiento = {
                                "fuente_coleccion": nombre_col, 
                                "fuente_id": unique_id,         
                                "texto_resumen": texto_resumen,  
                                "vector_resumen": vector_resumen 
                            }
                            coleccion_destino.update_one(
                                {"fuente_id": unique_id}, 
                                {"$set": documento_conocimiento},
                                upsert=True 
                            )
                            time.sleep(0.1) # Pausa mínima
                        
                        except Exception as e:
                            print(f"Error procesando producto {codigo}: {e}")
                
                continue # Saltamos el resto del loop para INVENTARIO


            # 2. 🟢 LÓGICA ESTÁNDAR PARA CLIENTES Y PEDIDOS
            texto_resumen = crear_texto_resumen(doc, nombre_col)
            
            if texto_resumen:
                try:
                    # 3. Crear el vector
                    vector_resumen = get_embedding(texto_resumen)
                    
                    # 4. Preparar el nuevo documento para la "Enciclopedia"
                    documento_conocimiento = {
                        "fuente_coleccion": nombre_col, 
                        "fuente_id": doc["_id"],         
                        "texto_resumen": texto_resumen,  
                        "vector_resumen": vector_resumen 
                    }
                    
                    # 5. Insertar/Actualizar
                    coleccion_destino.update_one(
                        {"fuente_id": doc["_id"]}, 
                        {"$set": documento_conocimiento},
                        upsert=True 
                    )
                    time.sleep(0.1)
                
                except Exception as e:
                    print(f"Error procesando documento ID {doc.get('_id')}: {e}")

    print("=" * 40)
    print("¡Enciclopedia de IA completada! (Colección: conocimiento_ia)")
    print("=" * 40)

# --- Ejecutar el script ---
if __name__ == "__main__":
    poblar_enciclopedia()
