"""
Módulo de modelos ORM de la base de datos.

Define las clases que SQLAlchemy mapea a tablas de la base de datos.
Estos modelos son exclusivos de la capa de infraestructura y no deben
ser usados directamente en las capas de dominio o aplicación.
"""

# src/infrastructure/db/models.py
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class ProductModel(Base):
    """
    Modelo ORM que representa la tabla 'products' en la base de datos.

    Mapea cada fila de la tabla a un objeto Python. Los repositorios
    convierten entre este modelo y la entidad de dominio Product.

    Attributes:
        id (int): Clave primaria, autoincremental.
        name (str): Nombre del producto. Máximo 200 caracteres. Obligatorio.
        brand (str): Marca del producto. Máximo 100 caracteres.
        category (str): Categoría del producto. Máximo 100 caracteres.
        size (str): Talla del producto. Máximo 20 caracteres.
        color (str): Color del producto. Máximo 50 caracteres.
        price (float): Precio del producto.
        stock (int): Cantidad disponible en inventario.
        description (str): Descripción detallada. Sin límite de longitud.
    """

    __tablename__ = 'products'

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(200), nullable=False)
    brand       = Column(String(100))
    category    = Column(String(100))
    size        = Column(String(20))
    color       = Column(String(50))
    price       = Column(Float)
    stock       = Column(Integer)
    description = Column(Text)

    def __repr__(self):
        """Representación legible del modelo para debugging."""
        return f"<ProductModel id={self.id} name={self.name!r} brand={self.brand!r}>"


class ChatMemoryModel(Base):
    """
    Modelo ORM que representa la tabla 'chat_memory' en la base de datos.

    Almacena cada mensaje de la conversación entre el usuario y el asistente.
    La columna session_id tiene índice para optimizar las consultas de historial,
    que son la operación más frecuente de esta tabla.

    Attributes:
        id (int): Clave primaria, autoincremental.
        session_id (str): Identificador de la sesión. Indexado. Obligatorio.
            Máximo 100 caracteres.
        role (str): Rol del emisor: 'user' o 'assistant'. Obligatorio.
            Máximo 20 caracteres.
        message (str): Contenido del mensaje. Sin límite de longitud. Obligatorio.
        timestamp (datetime): Fecha y hora de creación del mensaje.
            Por defecto, la fecha/hora actual al insertar.
    """

    __tablename__ = 'chat_memory'

    id         = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    role       = Column(String(20), nullable=False)
    message    = Column(Text, nullable=False)
    timestamp  = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        """Representación legible del modelo para debugging."""
        return (
            f"<ChatMemoryModel id={self.id} "
            f"session_id={self.session_id!r} role={self.role!r}>"
        )
