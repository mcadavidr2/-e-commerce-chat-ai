"""
Módulo de excepciones del dominio.

Contiene excepciones específicas del negocio que representan
errores semánticos, no errores técnicos. Usar estas excepciones
en lugar de Exception genérico permite un manejo más preciso
en las capas superiores.
"""


class ProductNotFoundError(Exception):
    """
    Excepción que se lanza cuando se busca un producto que no existe.

    Se usa en los servicios de aplicación cuando un repositorio retorna
    None para una búsqueda por ID, permitiendo que la capa HTTP la
    convierta en un 404.

    Attributes:
        message (str): Mensaje descriptivo del error, generado automáticamente.

    Example:
        >>> raise ProductNotFoundError(42)
        ProductNotFoundError: Producto con ID 42 no encontrado

        >>> raise ProductNotFoundError()
        ProductNotFoundError: Producto no encontrado
    """

    def __init__(self, product_id: int = None):
        """
        Inicializa la excepción con un mensaje contextual.

        Args:
            product_id (int, optional): ID del producto que no fue encontrado.
                Si se omite, se usa un mensaje genérico.
        """
        message = (
            f"Producto con ID {product_id} no encontrado"
            if product_id
            else "Producto no encontrado"
        )
        super().__init__(message)


class InvalidProductDataError(Exception):
    """
    Excepción que se lanza cuando los datos de un producto son inválidos.

    Se usa para propagar errores de validación de la entidad Product
    hacia la capa de aplicación, convirtiéndolos en errores de dominio
    con semántica de negocio.

    Example:
        >>> raise InvalidProductDataError("El precio no puede ser negativo")
        InvalidProductDataError: El precio no puede ser negativo

        >>> raise InvalidProductDataError()
        InvalidProductDataError: Datos de producto inválidos
    """

    def __init__(self, message: str = "Datos de producto inválidos"):
        """
        Inicializa la excepción con un mensaje personalizado.

        Args:
            message (str): Descripción del error de validación.
                Por defecto: "Datos de producto inválidos".
        """
        super().__init__(message)


class ChatServiceError(Exception):
    """
    Excepción que se lanza cuando ocurre un error en el servicio de chat.

    Envuelve errores técnicos (fallas de red, timeouts de la API de Gemini,
    errores inesperados) en una excepción de dominio que la capa HTTP
    convierte en un 500.

    Example:
        >>> raise ChatServiceError("Tiempo de espera agotado al llamar a Gemini")
        ChatServiceError: Tiempo de espera agotado al llamar a Gemini

        >>> raise ChatServiceError()
        ChatServiceError: Error en el servicio de chat
    """

    def __init__(self, message: str = "Error en el servicio de chat"):
        """
        Inicializa la excepción con un mensaje descriptivo.

        Args:
            message (str): Descripción del error ocurrido.
                Por defecto: "Error en el servicio de chat".
        """
        super().__init__(message)
