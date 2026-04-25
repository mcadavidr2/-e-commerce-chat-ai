"""
Módulo de configuración de la base de datos.

Configura el motor SQLAlchemy, la fábrica de sesiones y proporciona
las funciones de dependencia para FastAPI y de inicialización de tablas.
"""

# src/infrastructure/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

DATABASE_URL = "sqlite:///./data/ecommerce_chat.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency de FastAPI que provee una sesión de base de datos por request.

    Usa el patrón generator con try/finally para garantizar que la sesión
    siempre se cierre al terminar el request, incluso si ocurre una excepción.
    Se usa con Depends(get_db) en los endpoints de FastAPI.

    Yields:
        Session: Sesión de SQLAlchemy lista para usar en el request.

    Note:
        Esta función debe usarse exclusivamente como dependencia de FastAPI.
        No instanciar SessionLocal directamente en los endpoints.

    Example:
        >>> @app.get("/products")
        ... def get_products(db: Session = Depends(get_db)):
        ...     repo = SQLProductRepository(db)
        ...     return repo.get_all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas definidas en los modelos ORM.

    Esta función crea las tablas definidas en los modelos ORM
    y carga los datos iniciales si la base de datos está vacía.
    Es idempotente: si las tablas ya existen, no hace nada.

    Returns:
        None

    Note:
        Esta función debe ejecutarse antes de iniciar la aplicación.
        Se llama en el evento 'startup' de FastAPI.

    Example:
        >>> @app.on_event("startup")
        ... def on_startup():
        ...     init_db()
    """
    from infrastructure.db import models  # import local para evitar circular imports
    Base.metadata.create_all(bind=engine)
