#!/usr/bin/env python3
"""
Script para probar el chatbot de IA localmente antes del deploy.
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_chatbot_locally():
    """Probar el chatbot localmente."""
    
    print("🧪 Probando chatbot de IA localmente...")
    print("=" * 50)
    
    try:
        # Importar las dependencias necesarias
        print("1. Importando dependencias...")
    from langchain_core.prompts import PromptTemplate
    from langchain_community.memory import ConversationBufferMemory
    from langchain_community.chains import ConversationalRetrievalChain
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from langchain_mongodb import MongoDBAtlasVectorSearch
        from pymongo import MongoClient
        print("✅ Dependencias importadas correctamente")
        
        # Verificar variables de entorno
        print("\n2. Verificando variables de entorno...")
        GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
        MONGO_URI = os.environ.get("MONGO_URI")
        DB_NAME = os.environ.get("DB_NAME")
        COLLECTION_NAME = os.environ.get("COLLECTION_NAME")
        VECTOR_INDEX_NAME = os.environ.get("VECTOR_INDEX_NAME")
        
        if not GOOGLE_API_KEY:
            print("❌ GOOGLE_API_KEY no está definida")
            return False
        if not MONGO_URI:
            print("❌ MONGO_URI no está definida")
            return False
        if not DB_NAME:
            print("❌ DB_NAME no está definida")
            return False
        if not COLLECTION_NAME:
            print("❌ COLLECTION_NAME no está definida")
            return False
        if not VECTOR_INDEX_NAME:
            print("❌ VECTOR_INDEX_NAME no está definida")
            return False
        
        print("✅ Todas las variables de entorno están definidas")
        
        # Probar conexión a MongoDB
        print("\n3. Probando conexión a MongoDB...")
        try:
            client = MongoClient(MONGO_URI)
            client.admin.command('ping')
            print("✅ Conexión a MongoDB exitosa")
        except Exception as e:
            print(f"❌ Error de conexión a MongoDB: {e}")
            return False
        
        # Probar modelo de embeddings
        print("\n4. Probando modelo de embeddings...")
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=GOOGLE_API_KEY
            )
            print("✅ Modelo de embeddings inicializado correctamente")
        except Exception as e:
            print(f"❌ Error con modelo de embeddings: {e}")
            return False
        
        # Probar modelo de lenguaje
        print("\n5. Probando modelo de lenguaje...")
        try:
            llm = ChatGoogleGenerativeAI(
                model="models/gemini-2.5-flash",
                google_api_key=GOOGLE_API_KEY,
                temperature=0.5,
                convert_system_message_to_human=True
            )
            print("✅ Modelo de lenguaje inicializado correctamente")
        except Exception as e:
            print(f"❌ Error con modelo de lenguaje: {e}")
            return False
        
        # Probar una consulta simple
        print("\n6. Probando consulta simple...")
        try:
            response = llm.invoke("Hola, ¿cómo estás?")
            print(f"✅ Respuesta del modelo: {response.content[:100]}...")
        except Exception as e:
            print(f"❌ Error en consulta simple: {e}")
            return False
        
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("✅ El chatbot está listo para deploy")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que todas las dependencias estén instaladas:")
        print("   pip install google-generativeai langchain langchain-mongodb langchain-google-genai")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal."""
    print("🔍 Verificando chatbot de IA antes del deploy")
    print("=" * 60)
    
    success = test_chatbot_locally()
    
    if success:
        print("\n✅ ¡Verificación exitosa! El chatbot está listo para deploy.")
        print("🚀 Puedes hacer git push con confianza.")
    else:
        print("\n❌ ¡Verificación fallida! No hagas deploy todavía.")
        print("🔧 Corrige los errores antes de continuar.")

if __name__ == "__main__":
    main()
