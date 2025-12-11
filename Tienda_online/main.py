from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

from services.Tienda_service import TiendaService
from models.Usuario import Usuario, Cliente
from models.Producto import Producto, ProductoElectronico, ProductoRopa

app = FastAPI(title="Tienda Online API - Práctica 3")

tienda_service = TiendaService()

# ---------------------- SCHEMAS ---------------------- #

# ------ Usuarios ------ #

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    tipo: str
    direccion_postal: Optional[str] = None


class UsuarioRead(BaseModel):
    id: UUID
    nombre: str
    email: EmailStr
    es_admin: bool


# ------ Productos ------ #

class ProductoCreate(BaseModel):
    tipo: str  # generico, electronico, ropa
    nombre: str
    precio: float
    stock: int
    # Campos específicos
    meses_garantia: Optional[int] = None  # para electrónicos
    talla: Optional[str] = None  # para ropa
    color: Optional[str] = None  # para ropa


class ProductoRead(BaseModel):
    id: UUID
    tipo: str
    nombre: str
    precio: float
    stock: int
    # Atributos específicos opcionales
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None


# ------ Pedidos ------ #

class PedidoItemCreate(BaseModel):
    id_producto: UUID
    cantidad: int


class PedidoCreate(BaseModel):
    id_cliente: UUID
    items: List[PedidoItemCreate]


class PedidoItemRead(BaseModel):
    id_producto: UUID
    nombre_producto: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class PedidoRead(BaseModel):
    id: UUID
    fecha: datetime
    cliente: str
    total: float
    items: List[PedidoItemRead]


# ---------------------- ENDPOINTS ---------------------- #

# ------ USUARIOS ------ #

@app.post("/usuarios", response_model=UsuarioRead, status_code=201)
def crear_usuario(datos: UsuarioCreate) -> UsuarioRead:
    """Crea un nuevo usuario (cliente o administrador)."""
    try:
        usuario = tienda_service.registrar_usuario(
            tipo=datos.tipo,
            nombre=datos.nombre,
            email=str(datos.email),
            direccion=datos.direccion_postal,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return UsuarioRead(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        es_admin=usuario.is_admin(),
    )


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: str) -> UsuarioRead:
    """Obtiene un usuario por su ID."""
    try:
        from uuid import UUID as UUID_type
        usuario = tienda_service.obtener_usuario(UUID_type(usuario_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"ID inválido: {str(exc)}")

    return UsuarioRead(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        es_admin=usuario.is_admin(),
    )


@app.get("/usuarios", response_model=List[UsuarioRead])
def listar_usuarios() -> List[UsuarioRead]:
    """Lista todos los usuarios registrados."""
    usuarios = tienda_service.usuarios.values()

    return [
        UsuarioRead(
            id=u.id,
            nombre=u.nombre,
            email=u.email,
            es_admin=u.is_admin(),
        )
        for u in usuarios
    ]


# ------ PRODUCTOS ------ #

@app.post("/productos", response_model=ProductoRead, status_code=201)
def crear_producto(datos: ProductoCreate) -> ProductoRead:
    """Crea un nuevo producto (genérico, electrónico o ropa)."""
    tipo_lower = datos.tipo.lower()
    
    try:
        if tipo_lower == "electronico":
            if datos.meses_garantia is None:
                raise HTTPException(
                    status_code=400,
                    detail="meses_garantia es obligatorio para productos electrónicos"
                )
            producto = ProductoElectronico(
                nombre=datos.nombre,
                precio=datos.precio,
                stock=datos.stock,
                garantia_meses=datos.meses_garantia
            )
        elif tipo_lower == "ropa":
            if datos.talla is None or datos.color is None:
                raise HTTPException(
                    status_code=400,
                    detail="talla y color son obligatorios para productos de ropa"
                )
            producto = ProductoRopa(
                nombre=datos.nombre,
                precio=datos.precio,
                stock=datos.stock,
                talla=datos.talla,
                color=datos.color
            )
        elif tipo_lower == "generico":
            producto = Producto(
                nombre=datos.nombre,
                precio=datos.precio,
                stock=datos.stock
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Tipo de producto no válido. Usa 'generico', 'electronico' o 'ropa'."
            )
        
        tienda_service.agregar_producto(producto)
        
        # Construir respuesta según el tipo
        response_data = {
            "id": producto.id,
            "tipo": tipo_lower,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "stock": producto.stock,
        }
        
        if isinstance(producto, ProductoElectronico):
            response_data["meses_garantia"] = producto.garantia_meses
        elif isinstance(producto, ProductoRopa):
            response_data["talla"] = producto.talla
            response_data["color"] = producto.color
            
        return ProductoRead(**response_data)
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/productos", response_model=List[ProductoRead])
def listar_productos() -> List[ProductoRead]:
    """Lista todos los productos del inventario."""
    productos = tienda_service.listar_productos()
    
    result = []
    for p in productos:
        data = {
            "id": p.id,
            "nombre": p.nombre,
            "precio": p.precio,
            "stock": p.stock,
        }
        
        if isinstance(p, ProductoElectronico):
            data["tipo"] = "electronico"
            data["meses_garantia"] = p.garantia_meses
        elif isinstance(p, ProductoRopa):
            data["tipo"] = "ropa"
            data["talla"] = p.talla
            data["color"] = p.color
        else:
            data["tipo"] = "generico"
            
        result.append(ProductoRead(**data))
    
    return result


@app.get("/productos/{producto_id}", response_model=ProductoRead)
def obtener_producto(producto_id: str) -> ProductoRead:
    """Obtiene un producto por su ID."""
    try:
        from uuid import UUID as UUID_type
        producto = tienda_service.obtener_producto(UUID_type(producto_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"ID inválido: {str(exc)}")
    
    data = {
        "id": producto.id,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "stock": producto.stock,
    }
    
    if isinstance(producto, ProductoElectronico):
        data["tipo"] = "electronico"
        data["meses_garantia"] = producto.garantia_meses
    elif isinstance(producto, ProductoRopa):
        data["tipo"] = "ropa"
        data["talla"] = producto.talla
        data["color"] = producto.color
    else:
        data["tipo"] = "generico"
    
    return ProductoRead(**data)


@app.delete("/productos/{producto_id}", status_code=204)
def eliminar_producto(producto_id: str):
    """Elimina un producto del inventario."""
    try:
        from uuid import UUID as UUID_type
        tienda_service.eliminar_producto(UUID_type(producto_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"ID inválido: {str(exc)}")


# ------ PEDIDOS ------ #

@app.post("/pedidos", response_model=PedidoRead, status_code=201)
def crear_pedido(datos: PedidoCreate) -> PedidoRead:
    """
    Crea un nuevo pedido.
    
    Verifica:
    - Existencia del cliente
    - Existencia de los productos
    - Stock suficiente
    """
    # Verificar que el cliente existe
    try:
        cliente = tienda_service.obtener_usuario(datos.id_cliente)
        if not isinstance(cliente, Cliente):
            raise HTTPException(status_code=400, detail="El usuario no es un cliente")
    except ValueError:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Verificar existencia de productos y construir diccionario
    productos_cantidades = {}
    for item in datos.items:
        try:
            producto = tienda_service.obtener_producto(item.id_producto)
            productos_cantidades[item.id_producto] = item.cantidad
        except ValueError:
            raise HTTPException(
                status_code=404,
                detail=f"Producto {item.id_producto} no encontrado"
            )
    
    # Realizar pedido (verifica stock automáticamente)
    try:
        pedido = tienda_service.realizar_pedido(datos.id_cliente, productos_cantidades)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    
    # Construir respuesta
    items_read = []
    for producto, cantidad in pedido.productos.items():
        subtotal = producto.precio * cantidad
        items_read.append(
            PedidoItemRead(
                id_producto=producto.id,
                nombre_producto=producto.nombre,
                precio_unitario=producto.precio,
                cantidad=cantidad,
                subtotal=subtotal
            )
        )
    
    return PedidoRead(
        id=pedido.id,
        fecha=pedido.fecha,
        cliente=pedido.cliente.nombre,
        total=pedido.calcular_total(),
        items=items_read
    )


@app.get("/usuarios/{cliente_id}/pedidos", response_model=List[PedidoRead])
def obtener_pedidos_cliente(cliente_id: str) -> List[PedidoRead]:
    """Obtiene todos los pedidos de un cliente."""
    # Verificar que el cliente existe
    try:
        from uuid import UUID as UUID_type
        cliente_uuid = UUID_type(cliente_id)
        cliente = tienda_service.obtener_usuario(cliente_uuid)
        if not isinstance(cliente, Cliente):
            raise HTTPException(status_code=400, detail="El usuario no es un cliente")
    except ValueError:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"ID inválido: {str(exc)}")
    
    pedidos = tienda_service.pedidos_de_usuario(cliente_uuid)
    
    result = []
    for pedido in pedidos:
        items_read = []
        for producto, cantidad in pedido.productos.items():
            subtotal = producto.precio * cantidad
            items_read.append(
                PedidoItemRead(
                    id_producto=producto.id,
                    nombre_producto=producto.nombre,
                    precio_unitario=producto.precio,
                    cantidad=cantidad,
                    subtotal=subtotal
                )
            )
        
        result.append(
            PedidoRead(
                id=pedido.id,
                fecha=pedido.fecha,
                cliente=pedido.cliente.nombre,
                total=pedido.calcular_total(),
                items=items_read
            )
        )
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
