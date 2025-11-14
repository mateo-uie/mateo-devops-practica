from typing import Dict, List
from models.Usuario import Usuario, Cliente, Administrador
from models.Producto import Producto
from models.Pedido import Pedido

class TiendaService:
    """Clase de servicios que gestiona usuarios, productos y pedidos de la tienda."""

    def __init__(self):
        """Inicializa la tienda con listas vacías de usuarios, productos y pedidos."""
        self.usuarios: Dict[str, Usuario] = {}
        self.productos: Dict[str, Producto] = {}
        self.pedidos: List[Pedido] = []

    def registrar_usuario(self, tipo: str, nombre: str, email: str, direccion: str = None) -> Usuario:
        """
        Registra un nuevo usuario en la tienda.

        Args:
            tipo (str): Tipo de usuario ("cliente" o "admin").
            nombre (str): Nombre del usuario.
            email (str): Correo electrónico.
            direccion (str, optional): Dirección postal (solo clientes).

        Returns:
            Usuario: El usuario registrado.
        """
        if tipo == "cliente":
            usuario = Cliente(nombre, email, direccion)
        elif tipo == "admin":
            usuario = Administrador(nombre, email)
        else:
            raise ValueError("Tipo de usuario no válido")
        self.usuarios[usuario.id] = usuario
        return usuario

    def agregar_producto(self, producto: Producto):
        """
        Agrega un producto al inventario.

        Args:
            producto (Producto): Producto a agregar.
        """
        self.productos[producto.id] = producto

    def eliminar_producto(self, producto_id: str):
        """
        Elimina un producto del inventario.

        Args:
            producto_id (str): ID del producto a eliminar.
        """
        if producto_id in self.productos:
            del self.productos[producto_id]

    def listar_productos(self) -> List[Producto]:
        """
        Devuelve la lista de productos disponibles.

        Returns:
            list[Producto]: Lista de productos en inventario.
        """
        return list(self.productos.values())

    def realizar_pedido(self, cliente_id: str, productos_cantidades: Dict[str, int]) -> Pedido:
        """
        Crea un pedido para un cliente.

        Args:
            cliente_id (str): ID del cliente.
            productos_cantidades (dict[str, int]): Diccionario de productos con cantidades.

        Returns:
            Pedido: Pedido generado.

        Raises:
            ValueError: Si el cliente no existe o si no hay stock suficiente.
        """
        if cliente_id not in self.usuarios or not isinstance(self.usuarios[cliente_id], Cliente):
            raise ValueError("Cliente no encontrado")
        cliente = self.usuarios[cliente_id]

        productos = {}
        for pid, cantidad in productos_cantidades.items():
            if pid not in self.productos:
                raise ValueError(f"Producto {pid} no existe")
            producto = self.productos[pid]
            if not producto.hay_stock(cantidad):
                raise ValueError(f"No hay stock suficiente de {producto.nombre}")
            producto.actualizar_stock(-cantidad)
            productos[producto] = cantidad

        pedido = Pedido(cliente, productos)
        self.pedidos.append(pedido)
        return pedido

    def pedidos_de_usuario(self, cliente_id: str) -> List[Pedido]:
        """
        Obtiene todos los pedidos realizados por un cliente.

        Args:
            cliente_id (str): ID del cliente.

        Returns:
            list[Pedido]: Lista de pedidos del cliente.
        """
        return [p for p in self.pedidos if p.cliente.id == cliente_id]
