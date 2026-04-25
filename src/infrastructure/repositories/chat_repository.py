"""
Módulo de implementación del repositorio de chat con SQLAlchemy.

Implementa la interface IChatRepository usando SQLAlchemy como ORM,
gestionando la persistencia y recuperación del historial conversacional.
"""

# src/infrastructure/repositories/chat_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from domain.entities import ChatMessage
from domain.repositories import IChatRepository
from infrastructure.db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """
    Implementación SQLAlchemy del repositorio de historial de chat.

    Gestiona la persistencia del historial conversacional en la tabla
    chat_memory. El orden correcto de los mensajes es crucial: los
    métodos que retornan mensajes recientes usan un truco de ordenar
    descendente, limitar y luego invertir para aprovechar el índice
    de session_id.

    Attributes:
        db (Session): Sesión de SQLAlchemy inyectada en el constructor.

    Example:
        >>> repo = SQLChatRepository(db_session)
        >>> recent = repo.get_recent_messages("session_abc", count=6)
    """

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            db (Session): Sesión de SQLAlchemy activa. Se inyecta desde
                el endpoint de FastAPI mediante Depends(get_db).
        """
        self.db = db

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Persiste un mensaje de chat en la base de datos.

        Convierte la entidad a modelo ORM, la agrega a la sesión,
        hace commit y llama a refresh() para obtener el ID asignado.

        Args:
            message (ChatMessage): Mensaje a persistir. El campo id
                debe ser None para mensajes nuevos.

        Returns:
            ChatMessage: El mensaje guardado con su ID asignado por la BD.
        """
        model = self._entity_to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
    ) -> List[ChatMessage]:
        """
        Obtiene el historial de mensajes de una sesión en orden cronológico.

        Si se especifica limit, usa la estrategia desc+limit+reverse para
        obtener los últimos N mensajes de forma eficiente. Sin limit,
        usa un query ascendente directo.

        Args:
            session_id (str): Identificador de la sesión.
            limit (Optional[int]): Máximo de mensajes a retornar. Si es None,
                retorna el historial completo.

        Returns:
            List[ChatMessage]: Mensajes ordenados del más antiguo al más
                reciente. Vacía si la sesión no existe.
        """
        query = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.asc())
        )
        if limit:
            rows = (
                self.db.query(ChatMemoryModel)
                .filter(ChatMemoryModel.session_id == session_id)
                .order_by(ChatMemoryModel.timestamp.desc())
                .limit(limit)
                .all()
            )
            rows.reverse()
            return [self._model_to_entity(m) for m in rows]

        return [self._model_to_entity(m) for m in query.all()]

    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todos los mensajes de una sesión con un DELETE directo en BD.

        Usa delete() con synchronize_session=False para ejecutar un
        DELETE WHERE directo sin cargar los objetos en memoria, lo que
        es más eficiente para sesiones con muchos mensajes.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Número de mensajes eliminados. Cero si la sesión no existía.
        """
        deleted = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Obtiene los últimos N mensajes de una sesión en orden cronológico.

        Usa la estrategia desc+limit+reverse: ordena descendente (más reciente
        primero), limita a N, e invierte la lista para obtener el orden
        cronológico correcto. Esto es eficiente porque usa el índice de
        session_id y evita cargar todo el historial en memoria.

        Args:
            session_id (str): Identificador de la sesión.
            count (int): Número máximo de mensajes a retornar.

        Returns:
            List[ChatMessage]: Los últimos 'count' mensajes ordenados del
                más antiguo al más reciente. Vacía si la sesión no existe.
        """
        rows = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(count)
            .all()
        )
        rows.reverse()
        return [self._model_to_entity(m) for m in rows]

    # --- Helpers privados ---

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """
        Convierte un modelo ORM (ChatMemoryModel) a una entidad de dominio (ChatMessage).

        Args:
            model (ChatMemoryModel): Modelo ORM obtenido de SQLAlchemy.

        Returns:
            ChatMessage: Entidad de dominio con los datos del modelo.
        """
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    def _entity_to_model(self, message: ChatMessage) -> ChatMemoryModel:
        """
        Convierte una entidad de dominio (ChatMessage) a un modelo ORM (ChatMemoryModel).

        Args:
            message (ChatMessage): Entidad de dominio a convertir.

        Returns:
            ChatMemoryModel: Modelo ORM listo para persistir con SQLAlchemy.
        """
        return ChatMemoryModel(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            message=message.message,
            timestamp=message.timestamp,
        )
