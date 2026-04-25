"""
Módulo de implementación del repositorio de productos con SQLAlchemy.

Implementa la interface IProductRepository usando SQLAlchemy como ORM,
traduciendo entre los modelos de base de datos y las entidades del dominio.
"""

# src/infrastructure/repositories/product_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from domain.entities import Product
from domain.repositories import IProductRepository
from infrastructure.db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """
    Implementación SQLAlchemy del repositorio de productos.

    Traduce entre el modelo ORM (ProductModel) y la entidad de dominio
    (Product). Todas las operaciones de lectura y escritura pasan por
    esta clase, que encapsula los detalles de SQLAlchemy.

    Attributes:
        db (Session): Sesión de SQLAlchemy inyectada en el constructor.

    Example:
        >>> repo = SQLProductRepository(db_session)
        >>> products = repo.get_all()
        >>> product = repo.get_by_id(1)
    """

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            db (Session): Sesión de SQLAlchemy activa. Se inyecta desde
                el endpoint de FastAPI mediante Depends(get_db).
        """
        self.db = db

    # --- Lectura ---

    def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos de la base de datos.

        Returns:
            List[Product]: Lista de todas las entidades Product. Vacía
                si no hay productos registrados.
        """
        models = self.db.query(ProductModel).all()
        return [self._model_to_entity(m) for m in models]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por su ID en la base de datos.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            Optional[Product]: La entidad Product si existe, None si no.
        """
        model = self.db.query(ProductModel).filter(
            ProductModel.id == product_id
        ).first()
        return self._model_to_entity(model) if model else None

    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Busca productos por marca usando búsqueda parcial e insensible a mayúsculas.

        Usa ILIKE para que "nike" encuentre "Nike" y "NIKE".

        Args:
            brand (str): Nombre o parte del nombre de la marca a buscar.

        Returns:
            List[Product]: Lista de productos cuya marca coincide con el
                criterio de búsqueda. Puede estar vacía.
        """
        models = (
            self.db.query(ProductModel)
            .filter(ProductModel.brand.ilike(f"%{brand}%"))
            .all()
        )
        return [self._model_to_entity(m) for m in models]

    def get_by_category(self, category: str) -> List[Product]:
        """
        Busca productos por categoría usando búsqueda parcial e insensible a mayúsculas.

        Args:
            category (str): Nombre o parte del nombre de la categoría.

        Returns:
            List[Product]: Lista de productos en esa categoría. Puede estar vacía.
        """
        models = (
            self.db.query(ProductModel)
            .filter(ProductModel.category.ilike(f"%{category}%"))
            .all()
        )
        return [self._model_to_entity(m) for m in models]

    # --- Escritura ---

    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto en la base de datos.

        Si el producto tiene ID, intenta actualizar el registro existente
        campo a campo. Si no tiene ID o el ID no existe, crea un nuevo registro.
        Después del commit llama a refresh() para obtener el ID generado.

        Args:
            product (Product): Entidad a guardar o actualizar.

        Returns:
            Product: La entidad guardada con su ID asignado por la BD.
        """
        if product.id:
            model = self.db.query(ProductModel).filter(
                ProductModel.id == product.id
            ).first()
            if model:
                model.name        = product.name
                model.brand       = product.brand
                model.category    = product.category
                model.size        = product.size
                model.color       = product.color
                model.price       = product.price
                model.stock       = product.stock
                model.description = product.description
            else:
                model = self._entity_to_model(product)
                self.db.add(model)
        else:
            model = self._entity_to_model(product)
            self.db.add(model)

        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto de la base de datos por su ID.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si el producto existía y fue eliminado,
                False si no se encontró el producto.
        """
        model = self.db.query(ProductModel).filter(
            ProductModel.id == product_id
        ).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True

    # --- Helpers privados ---

    def _model_to_entity(self, model: ProductModel) -> Product:
        """
        Convierte un modelo ORM (ProductModel) a una entidad de dominio (Product).

        Args:
            model (ProductModel): Modelo ORM obtenido de SQLAlchemy.

        Returns:
            Product: Entidad de dominio con los datos del modelo.
        """
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )

    def _entity_to_model(self, product: Product) -> ProductModel:
        """
        Convierte una entidad de dominio (Product) a un modelo ORM (ProductModel).

        Args:
            product (Product): Entidad de dominio a convertir.

        Returns:
            ProductModel: Modelo ORM listo para persistir con SQLAlchemy.
        """
        return ProductModel(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category,
            size=product.size,
            color=product.color,
            price=product.price,
            stock=product.stock,
            description=product.description,
        )
