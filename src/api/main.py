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
from .routes.fallas import router as fallas_router
from .routes.cuentas_por_cobrar import router as cuentas_por_cobrar_router
from .routes.cuentas_por_pagar import router as cuentas_por_pagar_router
from .routes.facturas import router as facturas_router
from .routes.proveedores import router as proveedores_router
from .routes.compras import router as compras_router
from .routes.ordenes_compra import router as ordenes_compra_router
from .routes.listas_comparativas import router as listas_comparativas_router
from .routes.gastos import router as gastos_router
from .routes.finanzas import router as finanzas_router
from .routes.cierre_diario import router as cierre_diario_router
from .routes.bcv import router as bcv_router
from .routes.area_cliente import router as area_cliente_router
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

# CORS: un solo backend para varios frontends
# Orígenes permitidos desde variable de entorno (separados por coma) o lista por defecto
_default_origins = [
    "https://www.drocolven.com",
    "https://drocolven.com",
    "https://frontend-drocolven.vercel.app",
    "https://virgen-del-carmen-frontend.vercel.app",
    "http://localhost:3000",
]
_cors_env = os.getenv("CORS_ORIGINS", "").strip()
origins = [o.strip() for o in _cors_env.split(",") if o.strip()] if _cors_env else _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(fallas_router, tags=["Control de fallas"])
app.include_router(cuentas_por_cobrar_router)
app.include_router(cuentas_por_pagar_router)
app.include_router(facturas_router)
app.include_router(proveedores_router)
app.include_router(compras_router)
app.include_router(ordenes_compra_router)
app.include_router(listas_comparativas_router)
app.include_router(gastos_router)
app.include_router(finanzas_router)
app.include_router(cierre_diario_router)
app.include_router(bcv_router, tags=["BCV"])
app.include_router(area_cliente_router, tags=["Área cliente"])

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
#          SETUP: Crear usuario master (una vez)
# ===============================================
# En Render agrega variable: CREAR_MASTER_KEY = la clave que quieras (será también la contraseña del usuario master).
# Luego abre: https://tu-backend.onrender.com/setup/crear-master?key=ESA_MISMA_CLAVE
# Crea o actualiza usuario "master" en DROCOLVEN y VIRGENCARMEN con esa contraseña. Después puedes quitar CREAR_MASTER_KEY.
@app.get("/setup/crear-master")
def crear_usuario_master(key: Optional[str] = None):
    secret = os.getenv("CREAR_MASTER_KEY")
    if not secret or key != secret:
        return {"error": "Acceso no autorizado. Usa ?key=tu_clave (la que pusiste en CREAR_MASTER_KEY)."}
    USUARIO = "master"
    # La contraseña del usuario master es la misma que CREAR_MASTER_KEY (lo que pusiste en la variable de entorno).
    password_hash = get_password_hash(secret)
    # Usuario master tiene modulos: ["master"] para que el frontend muestre todos los módulos
    doc = {"usuario": USUARIO, "password": password_hash, "rol": "master", "modulos": ["master"]}
    resultados = []
    for nombre_db in ["DROCOLVEN", "VIRGENCARMEN"]:
        col = mongo_client[nombre_db]["usuarios_admin"]
        existente = col.find_one({"usuario": USUARIO})
        if existente:
            col.update_one({"usuario": USUARIO}, {"$set": {"password": password_hash, "rol": "master", "modulos": doc["modulos"]}})
            resultados.append(f"{nombre_db}: usuario 'master' ya existía; contraseña actualizada.")
        else:
            col.insert_one(doc)
            resultados.append(f"{nombre_db}: usuario 'master' creado.")
    return {"message": "Listo.", "detalle": resultados}

# ===============================================
#          INICIO CÓDIGO CHATBOT IA
# ===============================================
import os
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# Memoria compatible con ConversationalRetrievalChain (sin depender de langchain_community.memory)
class _ConversationBufferMemory:
    def __init__(self, memory_key: str = "chat_history", return_messages: bool = True, output_key: str = "answer"):
        self.memory_key = memory_key
        self.return_messages = return_messages
        self.output_key = output_key
        self.chat_memory = InMemoryChatMessageHistory()

    def load_memory_variables(self, inputs):
        messages = self.chat_memory.messages
        return {self.memory_key: messages if self.return_messages else self._messages_to_str(messages)}

    def save_context(self, inputs, outputs):
        question = inputs.get("question", inputs.get("input", ""))
        answer = outputs.get(self.output_key, outputs.get("answer", outputs.get("output", "")))
        if question:
            self.chat_memory.add_user_message(question if isinstance(question, str) else str(question))
        if answer:
            self.chat_memory.add_ai_message(answer if isinstance(answer, str) else str(answer))

    def _messages_to_str(self, messages):
        parts = []
        for m in messages:
            role = "Human" if isinstance(m, HumanMessage) else "AI"
            parts.append(f"{role}: {getattr(m, 'content', str(m))}")
        return "\n".join(parts)

    def clear(self):
        self.chat_memory.clear()

try:
    from langchain_community.memory.buffer import ConversationBufferMemory
except ImportError:
    try:
        from langchain.memory import ConversationBufferMemory
    except ImportError:
        try:
            from langchain_community.memory import ConversationBufferMemory
        except ImportError:
            ConversationBufferMemory = _ConversationBufferMemory
try:
    from langchain_community.chains import ConversationalRetrievalChain
    _USE_NATIVE_CHAIN = True
except ImportError:
    try:
        from langchain_community.chains.conversational_retrieval.base import ConversationalRetrievalChain
        _USE_NATIVE_CHAIN = True
    except ImportError:
        try:
            from langchain.chains import ConversationalRetrievalChain
            _USE_NATIVE_CHAIN = True
        except ImportError:
            ConversationalRetrievalChain = None
            _USE_NATIVE_CHAIN = False
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

# --- 7. Retriever y prompt (siempre) ---
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 5, "score_threshold": 0.7}
)
prompt = PromptTemplate.from_template(prompt_template)

# --- 8. Chain nativo o None (flujo manual en el endpoint) ---
if _USE_NATIVE_CHAIN:
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        rephrase_question=False
    )
else:
    chain = None

# --- El Endpoint de la API ---
class ChatRequest(BaseModel):
    prompt: str

def _chat_with_retrieval(question: str) -> str:
    """Flujo manual: retriever + prompt + LLM (sin ConversationalRetrievalChain)."""
    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs) if docs else ""
    formatted = prompt.invoke({"context": context, "question": question})
    answer = llm.invoke(formatted)
    answer_text = answer.content if hasattr(answer, "content") else str(answer)
    memory.save_context({"question": question}, {"answer": answer_text})
    return answer_text

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        if chain is not None:
            response = chain.invoke({"question": request.prompt})
            return {"response": response["answer"]}
        return {"response": _chat_with_retrieval(request.prompt)}
    except Exception as e:
        print(f"Error en el endpoint de chat: {e}")
        return {"response": f"Hubo un error al procesar tu solicitud: {e}"}

# ===============================================
#          FIN CÓDIGO CHATBOT IA
# ===============================================
