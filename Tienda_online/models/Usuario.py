from uuid import uuid4, UUID

class Usuario:
    """Clase base que representa a un usuario de la tienda."""

    def __init__(self, nombre: str, email: str):
        """
        Inicializa un usuario.

        Args:
            nombre (str): Nombre del usuario.
            email (str): Correo electrónico.
        """
        self.id: UUID = uuid4()
        self.nombre = nombre
        self.email = email

    def is_admin(self) -> bool:
        """
        Indica si el usuario es administrador.

        Returns:
            bool: False por defecto.
        """
        return False

    def __str__(self) -> str:
        """Devuelve una representación en texto del usuario."""
        return f"[{self.id}] {self.nombre} ({self.email})"


class Cliente(Usuario):
    """Clase que representa a un cliente de la tienda."""

    def __init__(self, nombre: str, email: str, direccion: str):
        """
        Inicializa un cliente.

        Args:
            nombre (str): Nombre del cliente.
            email (str): Correo electrónico.
            direccion (str): Dirección postal.
        """
        super().__init__(nombre, email)
        self.direccion = direccion

    def __str__(self) -> str:
        """Devuelve una representación en texto del cliente."""
        return f"{super().__str__()} | Dirección: {self.direccion}"


class Administrador(Usuario):
    """Clase que representa a un administrador de la tienda."""

    def is_admin(self) -> bool:
        """
        Indica si el usuario es administrador.

        Returns:
            bool: True siempre.
        """
        return True
