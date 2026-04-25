"""
Módulo de entidades del dominio.

Contiene las clases de negocio principales del e-commerce:
Product, ChatMessage y ChatContext.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """
    Entidad que representa un producto (zapato) en el e-commerce.

    Esta clase encapsula la lógica de negocio relacionada con productos,
    incluyendo validaciones de precio, stock y disponibilidad. No depende
    de ningún framework externo ni base de datos.

    Attributes:
        id (Optional[int]): Identificador único del producto. None si aún no
            ha sido persistido.
        name (str): Nombre del producto. No puede estar vacío.
        brand (str): Marca del producto (Nike, Adidas, Puma, etc.).
        category (str): Categoría del producto (Running, Casual, Formal).
        size (str): Talla del producto.
        color (str): Color o combinación de colores del producto.
        price (float): Precio en dólares. Debe ser mayor a 0.
        stock (int): Cantidad disponible en inventario. No puede ser negativo.
        description (str): Descripción detallada del producto.
    """

    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self):
        """
        Ejecuta validaciones de negocio al crear el objeto.

        Este método se llama automáticamente por el decorador @dataclass
        después de __init__. Valida que los datos cumplan las reglas de
        negocio antes de permitir la creación del producto.

        Raises:
            ValueError: Si el nombre está vacío o contiene solo espacios.
            ValueError: Si el precio es menor o igual a cero.
            ValueError: Si el stock es negativo.

        Example:
            >>> Product(id=None, name="", brand="Nike", category="Running",
            ...         size="42", color="Negro", price=100, stock=5,
            ...         description="Zapato")
            Traceback (most recent call last):
                ...
            ValueError: El nombre del producto no puede estar vacío
        """
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del producto no puede estar vacío")
        if self.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")

    def is_available(self) -> bool:
        """
        Verifica si el producto tiene stock disponible para la venta.

        Returns:
            bool: True si el stock es mayor a 0, False en caso contrario.

        Example:
            >>> product = Product(id=1, name="Air Max", brand="Nike",
            ...                   category="Running", size="42", color="Negro",
            ...                   price=150.0, stock=5, description="...")
            >>> product.is_available()
            True
            >>> product.stock = 0
            >>> product.is_available()
            False
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """
        Reduce el stock del producto en la cantidad especificada.

        Este método valida que haya suficiente stock antes de reducir.
        Se usa típicamente cuando se confirma una venta.

        Args:
            quantity (int): Cantidad a reducir del stock. Debe ser positivo.

        Raises:
            ValueError: Si quantity es cero o negativo.
            ValueError: Si quantity es mayor al stock disponible.

        Example:
            >>> product = Product(id=1, name="Air Max", brand="Nike",
            ...                   category="Running", size="42", color="Negro",
            ...                   price=150.0, stock=10, description="...")
            >>> product.reduce_stock(3)
            >>> print(product.stock)
            7
        """
        if quantity <= 0:
            raise ValueError("La cantidad debe ser positiva")
        if quantity > self.stock:
            raise ValueError(
                f"Stock insuficiente: disponible {self.stock}, solicitado {quantity}"
            )
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """
        Aumenta el stock del producto en la cantidad especificada.

        Se usa cuando se recibe nueva mercancía o se cancela un pedido.

        Args:
            quantity (int): Cantidad a agregar al stock. Debe ser positivo.

        Raises:
            ValueError: Si quantity es cero o negativo.

        Example:
            >>> product = Product(id=1, name="Air Max", brand="Nike",
            ...                   category="Running", size="42", color="Negro",
            ...                   price=150.0, stock=10, description="...")
            >>> product.increase_stock(5)
            >>> print(product.stock)
            15
        """
        if quantity <= 0:
            raise ValueError("La cantidad debe ser positiva")
        self.stock += quantity


@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje individual en la conversación.

    Permite distinguir quién emitió cada mensaje (usuario o asistente)
    y cuándo fue enviado, lo que es fundamental para mantener el contexto
    conversacional coherente.

    Attributes:
        id (Optional[int]): Identificador único del mensaje. None si aún no
            ha sido persistido en la base de datos.
        session_id (str): Identificador de la sesión del usuario. No puede
            estar vacío. Permite separar conversaciones entre usuarios.
        role (str): Rol del emisor. Solo acepta 'user' o 'assistant'.
        message (str): Contenido textual del mensaje. No puede estar vacío.
        timestamp (datetime): Fecha y hora en que fue enviado el mensaje.
    """

    id: Optional[int]
    session_id: str
    role: str  # 'user' o 'assistant'
    message: str
    timestamp: datetime

    def __post_init__(self):
        """
        Ejecuta validaciones de negocio al crear el mensaje.

        Raises:
            ValueError: Si session_id está vacío o contiene solo espacios.
            ValueError: Si role no es 'user' ni 'assistant'.
            ValueError: Si message está vacío o contiene solo espacios.

        Example:
            >>> ChatMessage(id=None, session_id="", role="user",
            ...             message="Hola", timestamp=datetime.utcnow())
            Traceback (most recent call last):
                ...
            ValueError: El session_id no puede estar vacío
        """
        if not self.session_id or not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío")
        if self.role not in ('user', 'assistant'):
            raise ValueError(
                f"El rol debe ser 'user' o 'assistant', recibido: '{self.role}'"
            )
        if not self.message or not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío")

    def is_from_user(self) -> bool:
        """
        Determina si el mensaje fue enviado por el usuario.

        Returns:
            bool: True si el rol es 'user', False en caso contrario.

        Example:
            >>> msg = ChatMessage(id=1, session_id="abc", role="user",
            ...                   message="Hola", timestamp=datetime.utcnow())
            >>> msg.is_from_user()
            True
        """
        return self.role == 'user'

    def is_from_assistant(self) -> bool:
        """
        Determina si el mensaje fue enviado por el asistente de IA.

        Returns:
            bool: True si el rol es 'assistant', False en caso contrario.

        Example:
            >>> msg = ChatMessage(id=2, session_id="abc", role="assistant",
            ...                   message="¿En qué puedo ayudarte?",
            ...                   timestamp=datetime.utcnow())
            >>> msg.is_from_assistant()
            True
        """
        return self.role == 'assistant'


@dataclass
class ChatContext:
    """
    Value Object que encapsula el contexto conversacional reciente.

    Mantiene los últimos N mensajes de una sesión para proporcionar
    memoria conversacional al modelo de IA. Al incluir el historial en
    el prompt, Gemini puede dar respuestas coherentes con lo hablado
    anteriormente.

    Attributes:
        messages (list[ChatMessage]): Lista completa de mensajes de la sesión.
        max_messages (int): Número máximo de mensajes recientes a incluir en
            el contexto. Por defecto 6.
    """

    messages: list[ChatMessage]
    max_messages: int = 6

    def get_recent_messages(self) -> list[ChatMessage]:
        """
        Retorna los últimos N mensajes según el límite configurado.

        Usa slicing de Python, por lo que funciona correctamente incluso
        si la lista tiene menos mensajes que max_messages.

        Returns:
            list[ChatMessage]: Los últimos max_messages mensajes en orden
                cronológico (más antiguo primero).

        Example:
            >>> messages = [ChatMessage(...) for _ in range(10)]
            >>> context = ChatContext(messages=messages, max_messages=6)
            >>> len(context.get_recent_messages())
            6
        """
        return self.messages[-self.max_messages:]

    def format_for_prompt(self) -> str:
        """
        Formatea los mensajes recientes como texto para incluir en el prompt de IA.

        Genera un string con el historial conversacional en un formato
        legible para el modelo de lenguaje, alternando entre 'Usuario'
        y 'Asistente'.

        Returns:
            str: Historial formateado. Cadena vacía si no hay mensajes.
                Formato de cada línea: "Rol: contenido del mensaje".

        Example:
            >>> messages = [
            ...     ChatMessage(id=1, session_id="s1", role="user",
            ...                 message="Busco zapatos Nike", ...),
            ...     ChatMessage(id=2, session_id="s1", role="assistant",
            ...                 message="¿Qué talla necesitas?", ...),
            ... ]
            >>> context = ChatContext(messages=messages)
            >>> print(context.format_for_prompt())
            Usuario: Busco zapatos Nike
            Asistente: ¿Qué talla necesitas?
        """
        role_label = {
            'user': 'Usuario',
            'assistant': 'Asistente'
        }
        return '\n'.join(
            f"{role_label[msg.role]}: {msg.message}"
            for msg in self.get_recent_messages()
        )
