"""
Módulo del servicio de aplicación para el chat con IA.

Implementa el caso de uso principal del sistema: procesar mensajes
de usuarios y generar respuestas contextuales usando Google Gemini.
"""

# src/application/chat_service.py
from datetime import datetime
from typing import List, Optional
from domain.entities import ChatMessage, ChatContext
from domain.repositories import IProductRepository, IChatRepository
from domain.exceptions import ChatServiceError
from application.dtos import ChatMessageRequestDTO, ChatMessageResponseDTO, ChatHistoryDTO


class ChatService:
    """
    Servicio de aplicación para gestionar el chat con IA.

    Orquesta la interacción entre el repositorio de productos,
    el repositorio de chat y el servicio de IA de Gemini para
    proporcionar respuestas contextuales a los usuarios. El flujo
    completo por cada mensaje es: obtener catálogo → recuperar historial
    → construir contexto → llamar a IA → persistir → retornar respuesta.

    Attributes:
        _products (IProductRepository): Repositorio de productos para
            obtener el catálogo disponible.
        _chat (IChatRepository): Repositorio de chat para persistir y
            recuperar el historial conversacional.
        _ai: Servicio de IA (GeminiService) para generar respuestas.

    Example:
        >>> service = ChatService(
        ...     product_repository=SQLProductRepository(db),
        ...     chat_repository=SQLChatRepository(db),
        ...     ai_service=GeminiService(),
        ... )
        >>> response = await service.process_message(request)
    """

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        ai_service,
    ):
        """
        Inicializa el servicio con sus tres dependencias.

        Args:
            product_repository (IProductRepository): Repositorio de productos
                para obtener el catálogo disponible.
            chat_repository (IChatRepository): Repositorio para persistir y
                recuperar el historial de conversaciones.
            ai_service: Servicio de IA que implementa generate_response().
                Normalmente una instancia de GeminiService.
        """
        self._products = product_repository
        self._chat = chat_repository
        self._ai = ai_service

    async def process_message(
        self, request: ChatMessageRequestDTO
    ) -> ChatMessageResponseDTO:
        """
        Procesa un mensaje del usuario y genera una respuesta con IA.

        Ejecuta el flujo completo de manera asíncrona:
        1. Obtiene todos los productos del catálogo.
        2. Recupera los últimos 6 mensajes de la sesión.
        3. Construye el contexto conversacional.
        4. Llama a Gemini AI con mensaje + catálogo + contexto.
        5. Persiste el mensaje del usuario en la base de datos.
        6. Persiste la respuesta del asistente en la base de datos.
        7. Retorna el DTO de respuesta.

        Args:
            request (ChatMessageRequestDTO): Mensaje del usuario con su
                session_id y el texto del mensaje.

        Returns:
            ChatMessageResponseDTO: Respuesta generada por la IA, junto
                con el mensaje original y el timestamp de la interacción.

        Raises:
            ChatServiceError: Si hay un error al procesar el mensaje,
                ya sea al llamar a la IA o por cualquier error inesperado.

        Example:
            >>> request = ChatMessageRequestDTO(
            ...     session_id="usuario_001",
            ...     message="Busco zapatos Nike para correr"
            ... )
            >>> response = await chat_service.process_message(request)
            >>> print(response.assistant_message)
            "¡Hola! Tengo varias opciones Nike para running..."
        """
        try:
            # 1. Productos disponibles como catálogo para la IA
            products = self._products.get_all()

            # 2. Historial reciente para mantener coherencia conversacional
            recent = self._chat.get_recent_messages(request.session_id, count=6)

            # 3. Contexto conversacional
            context = ChatContext(messages=recent)

            # 4. Llamada a la IA
            ai_response = await self._ai.generate_response(
            user_message=request.message,
            products=products,
            context=context,
            )

            now = datetime.utcnow()

            # 5. Persistir mensaje del usuario
            user_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role='user',
                message=request.message,
                timestamp=now,
            )
            self._chat.save_message(user_message)

            # 6. Persistir respuesta del asistente
            assistant_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role='assistant',
                message=ai_response,
                timestamp=now,
            )
            self._chat.save_message(assistant_message)

            # 7. Retornar DTO de respuesta
            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=ai_response,
                timestamp=now,
            )

        except ChatServiceError:
            raise
        except Exception as e:
            raise ChatServiceError(f"Error procesando mensaje: {str(e)}")

    def get_session_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
    ) -> List[ChatHistoryDTO]:
        """
        Obtiene el historial de mensajes de una sesión.

        Args:
            session_id (str): Identificador de la sesión cuyo historial
                se desea consultar.
            limit (Optional[int]): Número máximo de mensajes a retornar.
                Si es None, retorna el historial completo.

        Returns:
            List[ChatHistoryDTO]: Lista de mensajes en orden cronológico
                (del más antiguo al más reciente).

        Example:
            >>> history = service.get_session_history("usuario_001", limit=10)
            >>> for msg in history:
            ...     print(f"{msg.role}: {msg.message}")
        """
        messages = self._chat.get_session_history(session_id, limit=limit)
        return [
            ChatHistoryDTO(
                id=msg.id,
                role=msg.role,
                message=msg.message,
                timestamp=msg.timestamp,
            )
            for msg in messages
        ]

    def clear_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de mensajes de una sesión.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Número de mensajes eliminados. Cero si la sesión
                no existía o ya estaba vacía.

        Example:
            >>> deleted = service.clear_session_history("usuario_001")
            >>> print(f"Se eliminaron {deleted} mensajes")
        """
        return self._chat.delete_session_history(session_id)
