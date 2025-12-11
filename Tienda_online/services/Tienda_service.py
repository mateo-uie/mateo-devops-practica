from typing import Dict, List
from uuid import UUID
from models.Usuario import Usuario, Cliente, Administrador
from models.Producto import Producto
from models.Pedido import Pedido

class TiendaService:
    """Clase de servicios que gestiona usuarios, productos y pedidos de la tienda."""

    def __init__(self):
        """Inicializa la tienda con listas vacías de usuarios, productos y pedidos."""
        self.usuarios: Dict[UUID, Usuario] = {}
        self.productos: Dict[UUID, Producto] = {}
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
        tipo_lower = tipo.lower()
        if tipo_lower == "cliente":
            if not direccion:
                raise ValueError("La dirección postal es obligatoria para clientes.")
            usuario = Cliente(nombre, email, direccion)
        elif tipo_lower in ("admin", "administrador"):
            usuario = Administrador(nombre, email)
        else:
            raise ValueError("Tipo de usuario no válido. Usa 'cliente' o 'admin'.")
        self.usuarios[usuario.id] = usuario
        return usuario

    def obtener_usuario(self, usuario_id: UUID) -> Usuario:
        """
        Obtiene un usuario por su ID.

        Args:
            usuario_id (UUID): ID del usuario.

        Returns:
            Usuario: El usuario solicitado.

        Raises:
            ValueError: Si el usuario no existe.
        """
        usuario = self.usuarios.get(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado.")
        return usuario

    def agregar_producto(self, producto: Producto):
        """
        Agrega un producto al inventario.

        Args:
            producto (Producto): Producto a agregar.
        """
        self.productos[producto.id] = producto

    def obtener_producto(self, producto_id: UUID) -> Producto:
        """
        Obtiene un producto por su ID.

        Args:
            producto_id (UUID): ID del producto.

        Returns:
            Producto: El producto solicitado.

        Raises:
            ValueError: Si el producto no existe.
        """
        producto = self.productos.get(producto_id)
        if not producto:
            raise ValueError("Producto no encontrado.")
        return producto

    def eliminar_producto(self, producto_id: UUID):
        """
        Elimina un producto del inventario.

        Args:
            producto_id (UUID): ID del producto a eliminar.
        """
        if producto_id not in self.productos:
            raise ValueError("Producto no encontrado.")
        del self.productos[producto_id]

    def listar_productos(self) -> List[Producto]:
        """
        Devuelve la lista de productos disponibles.

        Returns:
            list[Producto]: Lista de productos en inventario.
        """
        return list(self.productos.values())

    def realizar_pedido(self, cliente_id: UUID, productos_cantidades: Dict[UUID, int]) -> Pedido:
        """
        Crea un pedido para un cliente.

        Args:
            cliente_id (UUID): ID del cliente.
            productos_cantidades (dict[UUID, int]): Diccionario de productos con cantidades.

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

    def pedidos_de_usuario(self, cliente_id: UUID) -> List[Pedido]:
        """
        Obtiene todos los pedidos realizados por un cliente.

        Args:
            cliente_id (UUID): ID del cliente.

        Returns:
            list[Pedido]: Lista de pedidos del cliente.
        """
        return [p for p in self.pedidos if p.cliente.id == cliente_id]
