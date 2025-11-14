import uuid
from datetime import datetime
from typing import Dict
from .Usuario import Cliente
from .Producto import Producto

class Pedido:
    """Clase que representa un pedido realizado por un cliente."""

    def __init__(self, cliente: Cliente, productos: Dict[Producto, int]):
        """
        Inicializa un pedido.

        Args:
            cliente (Cliente): Cliente que realiza el pedido.
            productos (dict[Producto, int]): Productos con sus cantidades.
        """
        self.id = str(uuid.uuid4())
        self.fecha = datetime.now()
        self.cliente = cliente
        self.productos = productos

    def calcular_total(self) -> float:
        """
        Calcula el total del pedido.

        Returns:
            float: Importe total del pedido.
        """
        return sum(p.precio * c for p, c in self.productos.items())

    def __str__(self) -> str:
        """Devuelve un resumen en texto del pedido."""
        productos_str = "\n".join([f"- {p.nombre} x{c}" for p, c in self.productos.items()])
        return (f"Pedido {self.id} ({self.fecha.strftime('%Y-%m-%d %H:%M')})\n"
                f"Cliente: {self.cliente.nombre}\n"
                f"Productos:\n{productos_str}\n"
                f"Total: ${self.calcular_total():.2f}")
