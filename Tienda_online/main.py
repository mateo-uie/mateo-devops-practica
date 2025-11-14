from models.Producto import ProductoElectronico, ProductoRopa
from services.Tienda_service import TiendaService

def main():
    tienda = TiendaService() # Inicializar servicio de tienda

    # Registrar usuarios
    cliente1 = tienda.registrar_usuario("cliente", "Ana", "ana@mail.com", "Prolongacion San Sebastian 97, Los Marines, Huelva, 21293, España")
    
    cliente2 = tienda.registrar_usuario("cliente", "Luis", "luis@mail.com", "Quevedo 45, Culleredo, A Coruña, 15189, España")
    cliente3 = tienda.registrar_usuario("cliente", "Marta", "marta@mail.com", "C/ Domingo Beltrán 53, Povedilla, Albacete, 02311, España")
    admin = tienda.registrar_usuario("admin", "Carlos", "admin@mail.com")

    # Crear productos
    portatil = ProductoElectronico("Ordenador Portátil", 1200.0, 10, 24)
    iphone = ProductoElectronico("iPhone 12 Pro Max", 800.0, 15, 12)
    sudadera = ProductoRopa("Sudadera Jack & Jones", 35.0, 25, "XL", "Negro")
    camiseta = ProductoRopa("Camiseta Deportiva Nike", 35.0, 20, "M", "Verde")
    pantalon = ProductoRopa("Pantalón Vaquero Levi's", 60.0, 15, "L", "Azul")
    camiseta2 = ProductoRopa("Camiseta Manga Larga Adidas", 28.0, 18, "S", "Blanco")
    pantalon2 = ProductoRopa("Pantalón Deportivo Puma", 45.0, 12, "M", "Negro")

    # Agregar productos
    for producto in [portatil, iphone, camiseta, pantalon, sudadera, camiseta2, pantalon2]:
        tienda.agregar_producto(producto)

    # Listar inventario
    print("\n--- Inventario ---")
    for producto in tienda.listar_productos():
        print(producto)

    # Simular pedidos
    print("\n--- Pedidos ---")
    pedido1 = tienda.realizar_pedido(cliente1.id, {portatil.id: 1, camiseta.id: 2})
    pedido2 = tienda.realizar_pedido(cliente2.id, {iphone.id: 1, pantalon.id: 1, camiseta2.id: 1})
    pedido3 = tienda.realizar_pedido(cliente3.id, {sudadera.id: 3})

    for pedido in [pedido1, pedido2, pedido3]:
        print(pedido)
        print("-" * 40)

    # Histórico de un cliente
    print("\n--- Histórico de Ana ---")
    for pedido in tienda.pedidos_de_usuario(cliente1.id):
        print(pedido)

    # Inventario actualizado
    print("\n--- Inventario actualizado ---")
    for producto in tienda.listar_productos():
        print(producto)

if __name__ == "__main__":
    main()
