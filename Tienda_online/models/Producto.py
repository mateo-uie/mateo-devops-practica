import uuid

class Producto:
    """Clase base que representa un producto genérico en la tienda."""
    def __init__(self, nombre: str, precio: float, stock: int):
        """
        Inicializa un producto.

        Args:
            nombre (str): Nombre del producto.
            precio (float): Precio del producto.
            stock (int): Cantidad disponible en inventario.
        """
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def hay_stock(self, cantidad: int) -> bool:
        """
        Verifica si hay suficiente stock del producto.

        Args:
            cantidad (int): Cantidad solicitada.

        Returns:
            bool: True si hay suficiente stock, False en caso contrario.
        """
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int):
        """
        Actualiza el stock del producto.

        Args:
            cantidad (int): Cantidad a modificar (positiva o negativa).
        """
        self.stock += cantidad

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} - ${self.precio:.2f} ({self.stock} disponibles)"


class ProductoElectronico(Producto):
    """Clase que representa un producto electrónico con garantía."""
    def __init__(self, nombre: str, precio: float, stock: int, garantia_meses: int):
        """
        Inicializa un producto electrónico.

        Args:
            nombre (str): Nombre del producto.
            precio (float): Precio del producto.
            stock (int): Cantidad disponible.
            garantia_meses (int): Meses de garantía.
        """
        super().__init__(nombre, precio, stock)
        self.garantia_meses = garantia_meses

    def __str__(self) -> str:
        """Devuelve una representación en texto del producto electrónico."""
        return f"{super().__str__()} | Garantía: {self.garantia_meses} meses"


class ProductoRopa(Producto):
    """Clase que representa un producto de ropa con talla y color."""
    def __init__(self, nombre: str, precio: float, stock: int, talla: str, color: str):
        """
        Inicializa un producto de ropa.

        Args:
            nombre (str): Nombre del producto.
            precio (float): Precio del producto.
            stock (int): Cantidad disponible.
            talla (str): Talla de la prenda.
            color (str): Color de la prenda.
        """
        super().__init__(nombre, precio, stock)
        self.talla = talla
        self.color = color

    def __str__(self) -> str:
        """Devuelve una representación en texto del producto de ropa."""
        return f"{super().__str__()} | Talla: {self.talla}, Color: {self.color}"
