"""
Módulo de configuración de la base de datos.

Configura el motor SQLAlchemy, la fábrica de sesiones y proporciona
las funciones de dependencia para FastAPI y de inicialización de tablas.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR}/ecommerce_chat.db"

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

    Yields:
        Session: Sesión de SQLAlchemy lista para usar en el request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando tablas y cargando datos iniciales.
    """
    from infrastructure.db.models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        from infrastructure.db.init_data import load_initial_data
        load_initial_data(db)
    finally:
        db.close()