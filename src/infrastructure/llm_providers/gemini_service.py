"""
Módulo del servicio de integración con Google Gemini AI.

Implementa la comunicación con la API de Google Gemini para generar
respuestas contextuales del asistente de ventas de zapatos.
"""

# src/infrastructure/llm_providers/gemini_service.py
import os
import google.generativeai as genai
from typing import List
from domain.entities import Product, ChatContext
from domain.exceptions import ChatServiceError


class GeminiService:
    """
    Servicio de IA que se integra con Google Gemini para generar respuestas.

    Encapsula toda la comunicación con la API de Gemini, incluyendo la
    construcción del prompt, el formateo del catálogo de productos y el
    historial conversacional. Convierte cualquier error de la API en una
    ChatServiceError para mantener las capas superiores desacopladas.

    Attributes:
        model: Instancia del modelo generativo de Gemini configurado
            para usar gemini-2.5-flash.

    Example:
        >>> service = GeminiService()
        >>> response = await service.generate_response(
        ...     message="Busco zapatos para correr",
        ...     products=products_list,
        ...     context=chat_context,
        ... )
    """

    def __init__(self):
        """
        Inicializa el servicio cargando la API key y configurando el modelo.

        Lee la API key de la variable de entorno GEMINI_API_KEY y
        configura el cliente de Gemini. Falla inmediatamente si la
        key no está definida, en lugar de fallar en el primer request.

        Raises:
            ValueError: Si la variable de entorno GEMINI_API_KEY no está
                definida o está vacía.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está definida en las variables de entorno")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def generate_response(
        self,
        user_message: str,
        products: List[Product],
        context: ChatContext,
    ) -> str:
        """
        Genera una respuesta contextual usando Google Gemini AI.

        Construye el prompt completo con el catálogo de productos y el
        historial de conversación, luego llama a la API de Gemini de forma
        asíncrona para no bloquear el event loop de FastAPI.

        Args:
            user_message (str): Mensaje actual del usuario.
            products (List[Product]): Catálogo completo de productos disponibles
                para que la IA pueda hacer recomendaciones específicas.
            context (ChatContext): Contexto con los últimos mensajes de la
                conversación para mantener coherencia.

        Returns:
            str: Respuesta generada por la IA, limpia de espacios al inicio
                y al final.

        Raises:
            ChatServiceError: Si ocurre cualquier error al comunicarse con
                la API de Gemini (red, cuota, formato, etc.).

        Example:
            >>> response = await service.generate_response(
            ...     message="¿Tienen Nike talla 42?",
            ...     products=products,
            ...     context=context,
            ... )
            >>> print(response)
            "¡Sí! Tenemos el Air Max 90 en talla 42 por $150..."
        """
        try:
            prompt = self._build_prompt(user_message, products, context)
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            raise ChatServiceError(f"Error al llamar a Gemini API: {str(e)}")

    def format_products_info(self, products: List[Product]) -> str:
        """
        Convierte la lista de productos a texto legible para el prompt de IA.

        Genera una línea por producto con su nombre, marca, precio, talla,
        color y stock disponible. Este formato permite al modelo de IA hacer
        recomendaciones precisas y mencionar disponibilidad.

        Args:
            products (List[Product]): Lista de productos a formatear.

        Returns:
            str: Texto formateado con un producto por línea, o un mensaje
                de "no disponible" si la lista está vacía.

        Example:
            >>> print(service.format_products_info(products))
            - Air Max 90 | Nike | $150.00 | Talla: 42 | Color: Blanco/Negro | Stock: 25 unidades
            - Ultraboost 22 | Adidas | $180.00 | Talla: 41 | Color: Negro | Stock: 15 unidades
        """
        if not products:
            return "No hay productos disponibles en este momento."

        lines = [
            f"- {p.name} | {p.brand} | ${p.price:.2f} | "
            f"Talla: {p.size} | Color: {p.color} | "
            f"Stock: {p.stock} unidades"
            for p in products
        ]
        return "\n".join(lines)

    def _build_prompt(
        self,
        user_message: str,
        products: List[Product],
        context: ChatContext,
    ) -> str:
        """
        Construye el prompt completo para enviar a Gemini AI.

        Combina las instrucciones del sistema, el catálogo de productos,
        el historial conversacional (si existe) y el mensaje actual del
        usuario en un prompt estructurado optimizado para el asistente
        de ventas de zapatos.

        Args:
            user_message (str): Mensaje actual del usuario.
            products (List[Product]): Catálogo de productos disponibles.
            context (ChatContext): Contexto con el historial reciente.

        Returns:
            str: Prompt completo listo para enviar a la API de Gemini.
        """
        products_info = self.format_products_info(products)
        conversation_history = context.format_for_prompt()

        history_section = (
            f"HISTORIAL DE CONVERSACIÓN:\n{conversation_history}\n"
            if conversation_history.strip()
            else ""
        )

        return f"""Eres un asistente virtual experto en ventas de zapatos para un e-commerce.
Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.

PRODUCTOS DISPONIBLES:
{products_info}

INSTRUCCIONES:
- Sé amigable y profesional
- Usa el contexto de la conversación anterior para dar respuestas coherentes
- Recomienda productos específicos cuando sea apropiado
- Menciona precios, tallas y disponibilidad cuando sea relevante
- Si no tienes información suficiente, sé honesto con el cliente
- Responde siempre en español

{history_section}Usuario: {user_message}
Asistente:"""
