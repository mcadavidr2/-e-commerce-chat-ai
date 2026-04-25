"""
Módulo de interfaces de repositorios del dominio.

Define los contratos abstractos para acceder a datos de productos
y mensajes de chat. Las implementaciones concretas viven en la capa
de infraestructura, lo que permite cambiar la base de datos sin
afectar la lógica de negocio.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage


class IProductRepository(ABC):
    """
    Interface que define el contrato para acceder a productos.

    Declara las operaciones disponibles sobre el almacenamiento de
    productos sin especificar su implementación. Siguiendo el principio
    de inversión de dependencias, la capa de dominio depende de esta
    abstracción y no de SQLAlchemy u otra librería concreta.

    Note:
        Esta clase no puede ser instanciada directamente. Cualquier
        subclase debe implementar todos los métodos abstractos.
    """

    @abstractmethod
    def get_all(self) -> List[Product]:
        """
        Retorna todos los productos registrados en el sistema.

        Returns:
            List[Product]: Lista de productos. Puede estar vacía si no
                hay productos registrados.
        """
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca y retorna un producto por su identificador único.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            Optional[Product]: El producto encontrado, o None si no existe
                ningún producto con ese ID.
        """
        pass

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Retorna todos los productos de una marca específica.

        Args:
            brand (str): Nombre de la marca a filtrar (ej. "Nike", "Adidas").

        Returns:
            List[Product]: Lista de productos de esa marca. Puede estar vacía.
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """
        Retorna todos los productos de una categoría específica.

        Args:
            category (str): Nombre de la categoría (ej. "Running", "Casual").

        Returns:
            List[Product]: Lista de productos en esa categoría. Puede estar vacía.
        """
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto en el almacenamiento.

        Si el producto tiene ID, actualiza el registro existente.
        Si no tiene ID, crea un nuevo registro y asigna un ID generado.

        Args:
            product (Product): Producto a guardar o actualizar.

        Returns:
            Product: El producto guardado, con su ID asignado si era nuevo.
        """
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto del almacenamiento por su ID.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si el producto existía y fue eliminado,
                False si no se encontró ningún producto con ese ID.
        """
        pass


class IChatRepository(ABC):
    """
    Interface para gestionar el historial de conversaciones.

    Declara las operaciones necesarias para persistir y recuperar
    mensajes del chat. El historial es fundamental para mantener
    el contexto conversacional entre requests.

    Note:
        Esta clase no puede ser instanciada directamente. Cualquier
        subclase debe implementar todos los métodos abstractos.
    """

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Persiste un mensaje de chat en el almacenamiento.

        Args:
            message (ChatMessage): Mensaje a guardar. Su campo id debe
                ser None si es un mensaje nuevo.

        Returns:
            ChatMessage: El mensaje guardado con su ID asignado por
                el almacenamiento.
        """
        pass

    @abstractmethod
    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Retorna el historial de mensajes de una sesión en orden cronológico.

        Args:
            session_id (str): Identificador de la sesión cuyo historial
                se quiere obtener.
            limit (Optional[int]): Si se especifica, retorna solo los
                últimos N mensajes. Si es None, retorna el historial completo.

        Returns:
            List[ChatMessage]: Mensajes ordenados del más antiguo al más
                reciente. Puede estar vacía si la sesión no existe.
        """
        pass

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todos los mensajes de una sesión.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Número de mensajes eliminados. Cero si la sesión no existía.
        """
        pass

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Retorna los últimos N mensajes de una sesión en orden cronológico.

        Es el método principal para construir el contexto conversacional
        que se envía al modelo de IA en cada request.

        Args:
            session_id (str): Identificador de la sesión.
            count (int): Número máximo de mensajes a retornar.

        Returns:
            List[ChatMessage]: Los últimos 'count' mensajes ordenados del
                más antiguo al más reciente. Puede estar vacía.
        """
        pass
