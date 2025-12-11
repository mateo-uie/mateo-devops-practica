from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from services.Tienda_service import TiendaService
from services.Auth_service import AuthService
from models.Usuario import Usuario, Cliente
from models.Producto import Producto, ProductoElectronico, ProductoRopa

app = FastAPI(title="Tienda Online API - Práctica 4")

tienda_service = TiendaService()
auth_service = AuthService()

# OAuth2 scheme para autenticación con Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

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


# ------ Autenticación ------ #

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserRead(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime
    is_active: bool


# ---------------------- DEPENDENCIAS DE AUTENTICACIÓN ---------------------- #

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependencia para obtener el usuario actual desde el token JWT.
    
    Args:
        token (str): Token JWT del header Authorization.
        
    Returns:
        User: Usuario autenticado.
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = auth_service.verify_token(token)
    if username is None:
        raise credentials_exception
    
    user = auth_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    return user


# ---------------------- ENDPOINTS ---------------------- #

# ------ AUTENTICACIÓN ------ #

@app.post("/auth/register", response_model=UserRead, status_code=201)
def register_user(user_data: UserRegister) -> UserRead:
    """
    Registra un nuevo usuario en el sistema.
    
    Verifica que no existan usuarios duplicados (username o email).
    La contraseña se hashea con bcrypt antes de almacenarla.
    """
    try:
        user = auth_service.create_user(
            username=user_data.username,
            email=str(user_data.email),
            password=user_data.password
        )
        return UserRead(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica un usuario y devuelve un token JWT.
    
    El usuario debe proporcionar username y password válidos.
    El token expira en 30 minutos.
    """
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/users", response_model=List[UserRead])
def list_users():
    """
    Lista todos los usuarios registrados en el sistema.
    
    Devuelve información básica de todos los usuarios (sin contraseñas).
    """
    users = auth_service.list_users()
    return [
        UserRead(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active
        )
        for user in users
    ]


@app.get("/auth/me", response_model=UserRead)
def get_current_user_info(current_user = Depends(get_current_user)):
    """
    Obtiene la información del usuario actualmente autenticado.
    
    Requiere token JWT válido en el header Authorization.
    """
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        is_active=current_user.is_active
    )


# ------ USUARIOS ------ #

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
def crear_producto(
    datos: ProductoCreate,
    current_user = Depends(get_current_user)
) -> ProductoRead:
    """
    Crea un nuevo producto (genérico, electrónico o ropa).
    
    **Requiere autenticación JWT.**
    """
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
def crear_pedido(
    datos: PedidoCreate,
    current_user = Depends(get_current_user)
) -> PedidoRead:
    """
    Crea un nuevo pedido.
    
    **Requiere autenticación JWT.**
    
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
