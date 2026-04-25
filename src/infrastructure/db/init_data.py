"""
Módulo de inicialización de datos de ejemplo.

Proporciona una función para poblar la base de datos con productos
de muestra al iniciar la aplicación por primera vez.
"""

# src/infrastructure/db/init_data.py
from infrastructure.db.models import ProductModel
from sqlalchemy.orm import Session


def load_initial_data(session: Session) -> None:
    """
    Carga productos de ejemplo si la tabla de productos está vacía.

    Esta función es idempotente: verifica primero si ya existen registros
    y no hace nada si la tabla tiene contenido. Se llama desde init_db()
    al arrancar la aplicación para asegurar que siempre haya datos para
    demostrar la funcionalidad.

    Los productos cargados incluyen variedad de marcas (Nike, Adidas, Puma,
    Converse, Reebok, Asics, New Balance, Vans, Clarks), categorías
    (Running, Casual, Formal) y precios entre $75 y $195.

    Args:
        session (Session): Sesión de SQLAlchemy activa. La función hace
            commit al final; el llamador es responsable de cerrar la sesión.

    Returns:
        None

    Note:
        La sesión llega por parámetro para mantener la función desacoplada
        de la configuración de base de datos y facilitar las pruebas.

    Example:
        >>> with SessionLocal() as session:
        ...     load_initial_data(session)
    """
    if session.query(ProductModel).count() > 0:
        return

    products = [
        ProductModel(
            name="Air Max 90",
            brand="Nike",
            category="Running",
            size="42",
            color="Blanco/Negro",
            price=150.00,
            stock=25,
            description="Zapatilla clásica de running con amortiguación Air Max.",
        ),
        ProductModel(
            name="Ultraboost 22",
            brand="Adidas",
            category="Running",
            size="41",
            color="Negro",
            price=180.00,
            stock=15,
            description="Alta respuesta energética con suela Boost para corredores exigentes.",
        ),
        ProductModel(
            name="RS-X Reinvention",
            brand="Puma",
            category="Casual",
            size="43",
            color="Blanco/Azul",
            price=120.00,
            stock=30,
            description="Diseño retro con tecnología moderna, ideal para uso diario.",
        ),
        ProductModel(
            name="Chuck Taylor All Star",
            brand="Converse",
            category="Casual",
            size="40",
            color="Rojo",
            price=75.00,
            stock=40,
            description="Ícono cultural en lona resistente, perfecto para el día a día.",
        ),
        ProductModel(
            name="Classic Leather",
            brand="Reebok",
            category="Casual",
            size="42",
            color="Blanco",
            price=90.00,
            stock=20,
            description="Cuero genuino con perfil limpio, versátil para cualquier outfit.",
        ),
        ProductModel(
            name="Gel-Kayano 29",
            brand="Asics",
            category="Running",
            size="44",
            color="Azul/Plateado",
            price=195.00,
            stock=10,
            description="Control de movimiento y amortiguación GEL para largas distancias.",
        ),
        ProductModel(
            name="Fresh Foam 1080",
            brand="New Balance",
            category="Running",
            size="41",
            color="Gris",
            price=165.00,
            stock=18,
            description="Espuma Fresh Foam v4 para máxima comodidad en rodajes largos.",
        ),
        ProductModel(
            name="Old Skool",
            brand="Vans",
            category="Casual",
            size="39",
            color="Negro/Blanco",
            price=80.00,
            stock=35,
            description="Silueta skate clásica con la icónica franja lateral.",
        ),
        ProductModel(
            name="Suede Classic",
            brand="Puma",
            category="Casual",
            size="43",
            color="Verde Oliva",
            price=95.00,
            stock=22,
            description="Gamuza premium con suela de goma, un clásico de los 70.",
        ),
        ProductModel(
            name="Oxford Brogue",
            brand="Clarks",
            category="Formal",
            size="42",
            color="Marrón",
            price=160.00,
            stock=12,
            description="Cuero curtido a mano con detalle brogue, elegancia atemporal.",
        ),
    ]

    session.add_all(products)
    session.commit()
