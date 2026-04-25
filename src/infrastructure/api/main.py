"""
Módulo principal de la aplicación FastAPI.

Define la instancia de FastAPI, el middleware de CORS, el evento de
arranque y todos los endpoints de la API REST del e-commerce con
asistente de ventas inteligente.
"""

# src/infrastructure/api/main.py
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from application.dtos import (
    ProductDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)
from application.product_service import ProductService
from application.chat_service import ChatService
from domain.exceptions import ProductNotFoundError, ChatServiceError
from infrastructure.db.database import get_db, init_db
from infrastructure.repositories.product_repository import SQLProductRepository
from infrastructure.repositories.chat_repository import SQLChatRepository
from infrastructure.llm_providers.gemini_service import GeminiService


app = FastAPI(
    title="Shoe Store AI Assistant",
    description="E-commerce de zapatos con asistente de ventas powered by Gemini.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """
    Evento de arranque de la aplicación.

    Inicializa la base de datos creando las tablas si no existen.
    Se ejecuta automáticamente al iniciar el servidor uvicorn.
    """
    init_db()


# --- Helpers de dependencias ---

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """
    Factory de dependencia para el servicio de productos.

    Construye el servicio con el repositorio SQLAlchemy inyectado
    automáticamente por FastAPI. Se usa con Depends() en los endpoints.

    Args:
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        ProductService: Servicio listo para usar en el endpoint.
    """
    return ProductService(SQLProductRepository(db))


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    """
    Factory de dependencia para el servicio de chat.

    Construye el servicio con todos sus repositorios y el servicio de IA
    inyectados. Se usa con Depends() en los endpoints de chat.

    Args:
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        ChatService: Servicio listo para usar en el endpoint.
    """
    return ChatService(
        product_repository=SQLProductRepository(db),
        chat_repository=SQLChatRepository(db),
        ai_service=GeminiService(),
    )


# --- Endpoints ---

@app.get("/", tags=["General"])
def root():
    """
    Retorna información básica de la API y lista de endpoints disponibles.

    Returns:
        dict: Nombre, versión y mapa de endpoints de la API.

    Example:
        GET /
        Response: {"name": "Shoe Store AI Assistant", "version": "1.0.0", ...}
    """
    return {
        "name": "Shoe Store AI Assistant",
        "version": "1.0.0",
        "endpoints": {
            "products":      "GET  /products",
            "product_by_id": "GET  /products/{product_id}",
            "chat":          "POST /chat",
            "chat_history":  "GET  /chat/history/{session_id}",
            "clear_history": "DELETE /chat/history/{session_id}",
            "health":        "GET  /health",
        },
    }


@app.get("/products", response_model=List[ProductDTO], tags=["Products"])
def get_products(service: ProductService = Depends(get_product_service)):
    """
    Obtiene la lista completa de productos disponibles en el catálogo.

    Retorna todos los productos registrados en la base de datos,
    incluyendo aquellos sin stock disponible.

    Args:
        service (ProductService): Servicio de productos inyectado por FastAPI.

    Returns:
        List[ProductDTO]: Lista de todos los productos con su información completa.

    Example:
        GET /products
        Response: [{"id": 1, "name": "Air Max 90", "brand": "Nike", ...}, ...]
    """
    return service.get_all_products()


@app.get("/products/{product_id}", response_model=ProductDTO, tags=["Products"])
def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    """
    Obtiene un producto específico por su identificador único.

    Args:
        product_id (int): ID del producto a buscar. Se pasa en la URL.
        service (ProductService): Servicio de productos inyectado por FastAPI.

    Returns:
        ProductDTO: Datos completos del producto encontrado.

    Raises:
        HTTPException: 404 si no existe ningún producto con ese ID.

    Example:
        GET /products/1
        Response: {"id": 1, "name": "Air Max 90", "brand": "Nike", ...}
    """
    try:
        return service.get_product_by_id(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/chat", response_model=ChatMessageResponseDTO, tags=["Chat"])
async def chat(
    request: ChatMessageRequestDTO,
    service: ChatService = Depends(get_chat_service),
):
    """
    Procesa un mensaje del usuario y retorna la respuesta del asistente de IA.

    Recibe el mensaje del usuario y su session_id, consulta el catálogo
    y el historial de la sesión, y genera una respuesta contextual usando
    Google Gemini AI. Persiste ambos mensajes (usuario y asistente) en la BD.

    Args:
        request (ChatMessageRequestDTO): Cuerpo del request con session_id y message.
        service (ChatService): Servicio de chat inyectado por FastAPI.

    Returns:
        ChatMessageResponseDTO: Respuesta de la IA junto con el mensaje original
            y el timestamp de la interacción.

    Raises:
        HTTPException: 500 si hay un error al procesar el mensaje o comunicarse
            con la API de Gemini.

    Example:
        POST /chat
        Body: {"session_id": "usuario_001", "message": "Busco zapatos Nike"}
        Response: {"session_id": "usuario_001", "user_message": "...", 
                   "assistant_message": "¡Hola! Tengo varias opciones Nike...", ...}
    """
    try:
        return await service.process_message(request)
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO], tags=["Chat"])
def get_chat_history(
    session_id: str,
    limit: Optional[int] = 10,
    service: ChatService = Depends(get_chat_service),
):
    """
    Obtiene el historial de mensajes de una sesión de chat.

    Retorna los mensajes en orden cronológico (del más antiguo al más reciente).

    Args:
        session_id (str): Identificador de la sesión. Se pasa en la URL.
        limit (Optional[int]): Número máximo de mensajes a retornar.
            Por defecto 10. Se pasa como query parameter.
        service (ChatService): Servicio de chat inyectado por FastAPI.

    Returns:
        List[ChatHistoryDTO]: Lista de mensajes de la sesión con su rol,
            contenido y timestamp.

    Example:
        GET /chat/history/usuario_001?limit=5
        Response: [{"id": 1, "role": "user", "message": "...", "timestamp": "..."}, ...]
    """
    return service.get_session_history(session_id, limit=limit)


@app.delete("/chat/history/{session_id}", tags=["Chat"])
def delete_chat_history(
    session_id: str,
    service: ChatService = Depends(get_chat_service),
):
    """
    Elimina todo el historial de mensajes de una sesión de chat.

    Args:
        session_id (str): Identificador de la sesión a limpiar. Se pasa en la URL.
        service (ChatService): Servicio de chat inyectado por FastAPI.

    Returns:
        dict: Confirmación con el session_id y el número de mensajes eliminados.

    Example:
        DELETE /chat/history/usuario_001
        Response: {"session_id": "usuario_001", "messages_deleted": 8}
    """
    deleted = service.clear_session_history(session_id)
    return {"session_id": session_id, "messages_deleted": deleted}


@app.get("/health", tags=["General"])
def health_check():
    """
    Endpoint de verificación del estado de la API.

    Permite a Docker, load balancers y herramientas de monitoreo
    verificar que la aplicación está operativa.

    Returns:
        dict: Estado de la API y timestamp actual en formato ISO 8601.

    Example:
        GET /health
        Response: {"status": "ok", "timestamp": "2024-01-15T10:30:00.000000"}
    """
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
