"""
Módulo del servicio de aplicación para productos.

Implementa los casos de uso relacionados con la gestión de productos
del e-commerce, coordinando entre el repositorio de datos y las
entidades del dominio.
"""

# src/application/product_service.py
from typing import List, Optional, Dict, Any
from domain.entities import Product
from domain.repositories import IProductRepository
from domain.exceptions import ProductNotFoundError, InvalidProductDataError
from application.dtos import ProductDTO


class ProductService:
    """
    Servicio de aplicación para la gestión de productos del e-commerce.

    Orquesta los casos de uso relacionados con productos: listado,
    búsqueda, creación, actualización y eliminación. Recibe el repositorio
    por inyección de dependencias, lo que permite testear sin base de datos.

    Attributes:
        _repository (IProductRepository): Repositorio de productos inyectado
            en el constructor.

    Example:
        >>> repo = SQLProductRepository(db_session)
        >>> service = ProductService(repo)
        >>> products = service.get_all_products()
    """

    def __init__(self, repository: IProductRepository):
        """
        Inicializa el servicio con el repositorio de productos.

        Args:
            repository (IProductRepository): Implementación concreta del
                repositorio. Se inyecta desde la capa de infraestructura.
        """
        self._repository = repository

    def get_all_products(self) -> List[ProductDTO]:
        """
        Retorna todos los productos disponibles en el catálogo.

        Returns:
            List[ProductDTO]: Lista de todos los productos, incluyendo
                los que no tienen stock.

        Example:
            >>> service.get_all_products()
            [ProductDTO(id=1, name='Air Max', ...), ...]
        """
        products = self._repository.get_all()
        return [self._to_dto(p) for p in products]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """
        Busca y retorna un producto por su identificador único.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            ProductDTO: Datos del producto encontrado.

        Raises:
            ProductNotFoundError: Si no existe ningún producto con ese ID.

        Example:
            >>> service.get_product_by_id(1)
            ProductDTO(id=1, name='Air Max', ...)
        """
        product = self._repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)
        return self._to_dto(product)

    def search_products(self, filters: Dict[str, Any]) -> List[ProductDTO]:
        """
        Filtra productos según los criterios proporcionados.

        Actualmente soporta filtrado por marca y por categoría.
        Si no se proporciona ningún filtro, retorna todos los productos.

        Args:
            filters (Dict[str, Any]): Diccionario con criterios de búsqueda.
                Claves soportadas: 'brand' (str), 'category' (str).

        Returns:
            List[ProductDTO]: Lista de productos que cumplen el filtro.
                Puede estar vacía si ningún producto coincide.

        Example:
            >>> service.search_products({'brand': 'Nike'})
            [ProductDTO(id=1, name='Air Max', brand='Nike', ...), ...]
        """
        if brand := filters.get('brand'):
            products = self._repository.get_by_brand(brand)
        elif category := filters.get('category'):
            products = self._repository.get_by_category(category)
        else:
            products = self._repository.get_all()

        return [self._to_dto(p) for p in products]

    def create_product(self, product_dto: ProductDTO) -> ProductDTO:
        """
        Crea un nuevo producto en el sistema.

        Convierte el DTO a una entidad de dominio (lo que ejecuta las
        validaciones de negocio) y lo persiste a través del repositorio.

        Args:
            product_dto (ProductDTO): Datos del producto a crear.
                El campo id debe ser None.

        Returns:
            ProductDTO: El producto creado con su ID asignado.

        Raises:
            InvalidProductDataError: Si los datos del DTO son inválidos
                según las reglas de la entidad Product.

        Example:
            >>> dto = ProductDTO(name='Air Max', brand='Nike', ...)
            >>> service.create_product(dto)
            ProductDTO(id=5, name='Air Max', ...)
        """
        try:
            product = self._to_entity(product_dto)
        except ValueError as e:
            raise InvalidProductDataError(str(e))

        saved = self._repository.save(product)
        return self._to_dto(saved)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> ProductDTO:
        """
        Actualiza un producto existente en el sistema.

        Verifica que el producto exista antes de intentar actualizarlo.

        Args:
            product_id (int): ID del producto a actualizar.
            product_dto (ProductDTO): Nuevos datos del producto.

        Returns:
            ProductDTO: El producto actualizado.

        Raises:
            ProductNotFoundError: Si no existe un producto con ese ID.
            InvalidProductDataError: Si los nuevos datos son inválidos.

        Example:
            >>> dto = ProductDTO(name='Air Max 2', brand='Nike', price=160, ...)
            >>> service.update_product(1, dto)
            ProductDTO(id=1, name='Air Max 2', price=160, ...)
        """
        existing = self._repository.get_by_id(product_id)
        if not existing:
            raise ProductNotFoundError(product_id)

        try:
            updated = self._to_entity(product_dto)
            updated.id = product_id
        except ValueError as e:
            raise InvalidProductDataError(str(e))

        saved = self._repository.save(updated)
        return self._to_dto(saved)

    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto del sistema.

        Verifica que el producto exista antes de intentar eliminarlo.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si el producto fue eliminado exitosamente.

        Raises:
            ProductNotFoundError: Si no existe un producto con ese ID.

        Example:
            >>> service.delete_product(1)
            True
        """
        if not self._repository.get_by_id(product_id):
            raise ProductNotFoundError(product_id)
        return self._repository.delete(product_id)

    def get_available_products(self) -> List[ProductDTO]:
        """
        Retorna solo los productos que tienen stock disponible para la venta.

        Delega la lógica de disponibilidad al método is_available() de la
        entidad Product, respetando el principio de responsabilidad única.

        Returns:
            List[ProductDTO]: Lista de productos con stock mayor a 0.

        Example:
            >>> service.get_available_products()
            [ProductDTO(id=1, name='Air Max', stock=25, ...), ...]
        """
        products = self._repository.get_all()
        return [self._to_dto(p) for p in products if p.is_available()]

    # --- Helpers privados ---

    def _to_entity(self, dto: ProductDTO) -> Product:
        """
        Convierte un ProductDTO a una entidad Product del dominio.

        Al crear la entidad, se ejecutan automáticamente las validaciones
        de negocio definidas en __post_init__.

        Args:
            dto (ProductDTO): DTO con los datos del producto.

        Returns:
            Product: Entidad de dominio con los datos del DTO.

        Raises:
            ValueError: Si los datos del DTO no cumplen las reglas de
                negocio de la entidad Product.
        """
        return Product(
            id=dto.id,
            name=dto.name,
            brand=dto.brand,
            category=dto.category,
            size=dto.size,
            color=dto.color,
            price=dto.price,
            stock=dto.stock,
            description=dto.description,
        )

    def _to_dto(self, product: Product) -> ProductDTO:
        """
        Convierte una entidad Product del dominio a un ProductDTO.

        Usado para preparar la respuesta antes de enviarla al cliente.

        Args:
            product (Product): Entidad de dominio a convertir.

        Returns:
            ProductDTO: DTO listo para serialización JSON.
        """
        return ProductDTO(
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
