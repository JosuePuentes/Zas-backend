from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.clientes import router as clientes_router
from .routes.pedidos import router as pedidos_router
from .routes.inventario import router as inventario_router
from .routes.auth import router as auth_router
from .routes.contacto import router as contacto_router
from .routes.reclamos import router as reclamos_router
from .routes.modulos import router as modulos_router
from .routes.transaccion import router as transaccion_router
from .routes.formato_impresion import router as formato_impresion_router
from .routes.facturacion_dinamica import router as facturacion_dinamica_router
from .routes.punto_venta import router as punto_venta_router
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Optional
from pymongo import MongoClient
from passlib.context import CryptContext
import os

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

# Configuración de cifrado de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Inicializar FastAPI
app = FastAPI()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 🚨 INICIO DE LA CORRECCIÓN CORS 🚨
# Lista de orígenes permitidos, ahora incluyendo tu nuevo dominio específico
origins = [
    "https://www.drocolven.com",  # Tu frontend nuevo
    "https://drocolven.com",      # Versión sin 'www' (recomendado)
    "https://frontend-drocolven.vercel.app",  # Tu frontend en Vercel
    "http://localhost:3000",      # Si todavía lo usas para desarrollo local
    # Puedes dejar ["*"] o añadir cualquier otro dominio que necesites aquí
]

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # <-- Usamos la lista de orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 🚨 FIN DE LA CORRECCIÓN CORS 🚨

# Incluir routers segmentados
app.include_router(clientes_router)
app.include_router(pedidos_router)
app.include_router(inventario_router)
app.include_router(auth_router)
app.include_router(contacto_router)
app.include_router(reclamos_router)
app.include_router(modulos_router)
app.include_router(transaccion_router, prefix="/transaccion", tags=["Transacciones"])
app.include_router(formato_impresion_router, prefix="/formatos-impresion", tags=["Formatos de Impresión"])
app.include_router(facturacion_dinamica_router, prefix="/pedidos", tags=["Facturación Dinámica"])
app.include_router(punto_venta_router, tags=["Punto de Venta"])

from .models.models import (
    Client, ProductoInventario, UserRegister, UserLogin, UserAdminRegister, AdminLogin,
    ProductoPedido, PedidoResumen, PedidoArmado, EstadoPedido, ContactForm, CantidadesEncontradas,
    PickingInfo, PackingInfo, EnvioInfo, ReclamoCliente
)

from .auth.auth_utils import get_password_hash, verify_password, create_access_token, create_admin_access_token
from .database import (
    db, collection, inventario_collection, clients_collection, usuarios_admin_collection, ventas_collection, pedidos_collection, client as mongo_client
)

# ===============================================
#          INICIO CÓDIGO CHATBOT IA
# ===============================================
import os
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from langchain_community.memory import ConversationBufferMemory
from langchain_community.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient

# --- Cargar variables de entorno ---
# (Asegúrate de que 'app' sea tu instancia de FastAPI)
# Si tu app no se llama 'app', ajusta la línea @app.post más abajo

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("DB_NAME")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME")
VECTOR_INDEX_NAME = os.environ.get("VECTOR_INDEX_NAME")

# --- 1. Conexión a MongoDB ---
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# --- 2. Inicializa el modelo de Embeddings (para buscar) ---
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=GOOGLE_API_KEY
)

# --- 3. Inicializa el Vector Store (LangChain + Atlas) ---
vector_store = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embeddings,
    index_name=VECTOR_INDEX_NAME,
    text_key="texto_resumen",       # <-- ¡NUEVO CAMPO!
    embedding_key="vector_resumen"  # <-- ¡NUEVO CAMPO!
)

# --- 4. Inicializa el Modelo de Lenguaje (para responder) ---
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.5,
    convert_system_message_to_human=True
)

# --- 5. Define el "Prompt" (la personalidad de tu IA) ---
prompt_template = """
Eres "Dona", un asistente experto en la gestión de la empresa Drocolven.
Tu trabajo es responder preguntas sobre clientes, pedidos, movimientos, e inventario.

IMPORTANTE: Nunca inicies tu respuesta con un saludo. Responde de manera concisa y directa.

El contexto incluye datos de clientes, movimientos, inventario y pedidos.
Si la respuesta no está en el contexto, di amablemente que no tienes esa información.
No inventes información.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
"""

# --- 6. Define la memoria (para que recuerde el chat) ---
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key='answer'
)

# --- 7. Crea la "Cadena" (Chain) que une todo ---
chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            'k': 5, 
            'score_threshold': 0.7
        }
    ),
    memory=memory,
    combine_docs_chain_kwargs={
        "prompt": PromptTemplate.from_template(prompt_template)
    },
    rephrase_question=False
)

# --- El Endpoint de la API ---
class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/chat") # ¡Importante! Asegúrate de que tu app de FastAPI se llame 'app'
async def chat_endpoint(request: ChatRequest):
    try:
        # Aquí ocurre la magia:
        response = chain.invoke({"question": request.prompt})
        
        return {"response": response['answer']}

    except Exception as e:
        print(f"Error en el endpoint de chat: {e}")
        return {"response": f"Hubo un error al procesar tu solicitud: {e}"}

# ===============================================
#          FIN CÓDIGO CHATBOT IA
# ===============================================
