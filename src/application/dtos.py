"""
Módulo de DTOs (Data Transfer Objects) de la capa de aplicación.

Los DTOs validan automáticamente los datos de entrada usando Pydantic
y sirven como contrato entre la API HTTP y los servicios de aplicación.
Evitan que objetos de dominio crudos sean expuestos directamente.
"""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ProductDTO(BaseModel):
    """
    DTO para transferir datos de productos entre capas.

    Pydantic valida automáticamente los tipos al construir el objeto.
    Se usa tanto para recibir datos de creación/actualización como para
    enviar datos de productos al cliente.

    Attributes:
        id (Optional[int]): ID del producto. None para productos nuevos.
        name (str): Nombre del producto.
        brand (str): Marca del producto.
        category (str): Categoría del producto.
        size (str): Talla del producto.
        color (str): Color del producto.
        price (float): Precio. Debe ser mayor a 0.
        stock (int): Cantidad en inventario. No puede ser negativo.
        description (str): Descripción del producto.
    """

    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    @validator('price')
    def price_must_be_positive(cls, v):
        """
        Valida que el precio del producto sea mayor a cero.

        Args:
            v (float): Valor del precio a validar.

        Returns:
            float: El precio validado sin modificaciones.

        Raises:
            ValueError: Si el precio es menor o igual a cero.
        """
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

    @validator('stock')
    def stock_must_be_non_negative(cls, v):
        """
        Valida que el stock no sea negativo.

        Args:
            v (int): Valor del stock a validar.

        Returns:
            int: El stock validado sin modificaciones.

        Raises:
            ValueError: Si el stock es negativo.
        """
        if v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v

    class Config:
        """Configuración de Pydantic para este modelo."""
        from_attributes = True  # Permite crear desde objetos ORM


class ChatMessageRequestDTO(BaseModel):
    """
    DTO para recibir mensajes del usuario en el endpoint POST /chat.

    Valida que el mensaje y la sesión tengan contenido válido antes
    de procesarlos.

    Attributes:
        session_id (str): Identificador único de la sesión del usuario.
            No puede estar vacío.
        message (str): Texto del mensaje del usuario. No puede estar vacío.
    """

    session_id: str
    message: str

    @validator('message')
    def message_not_empty(cls, v):
        """
        Valida que el mensaje no esté vacío ni contenga solo espacios.

        Args:
            v (str): Valor del mensaje a validar.

        Returns:
            str: El mensaje limpio (sin espacios al inicio y al final).

        Raises:
            ValueError: Si el mensaje está vacío o tiene solo espacios.
        """
        if not v or not v.strip():
            raise ValueError("El mensaje no puede estar vacío")
        return v.strip()

    @validator('session_id')
    def session_id_not_empty(cls, v):
        """
        Valida que el session_id no esté vacío ni contenga solo espacios.

        Args:
            v (str): Valor del session_id a validar.

        Returns:
            str: El session_id limpio (sin espacios al inicio y al final).

        Raises:
            ValueError: Si el session_id está vacío o tiene solo espacios.
        """
        if not v or not v.strip():
            raise ValueError("El session_id no puede estar vacío")
        return v.strip()


class ChatMessageResponseDTO(BaseModel):
    """
    DTO para enviar la respuesta del chat al cliente.

    Incluye tanto el mensaje original del usuario como la respuesta
    generada por la IA, junto con el timestamp de la interacción.

    Attributes:
        session_id (str): Identificador de la sesión.
        user_message (str): Mensaje original enviado por el usuario.
        assistant_message (str): Respuesta generada por el asistente de IA.
        timestamp (datetime): Marca de tiempo de la interacción.
    """

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """
    DTO para representar un mensaje individual en el historial de chat.

    Se usa en el endpoint GET /chat/history/{session_id} para listar
    los mensajes de una sesión.

    Attributes:
        id (int): Identificador único del mensaje.
        role (str): Emisor del mensaje ('user' o 'assistant').
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Fecha y hora en que fue enviado.
    """

    id: int
    role: str
    message: str
    timestamp: datetime

    class Config:
        """Configuración de Pydantic para este modelo."""
        from_attributes = True  # Permite crear desde objetos ORM
