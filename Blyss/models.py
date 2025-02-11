from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    def create_user(self, correo, nombre, apellidos, password=None, **extra_fields):
        """
        Crea y retorna un usuario con el correo y contraseña proporcionados.
        """
        if not correo:
            raise ValueError("El usuario debe tener un correo electrónico")
        correo = self.normalize_email(correo)
        usuario = self.model(correo=correo, Nombre=nombre, Apellidos=apellidos, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, correo, nombre, apellidos, password=None, **extra_fields):
        """
        Crea y retorna un superusuario con el correo y contraseña proporcionados.
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        return self.create_user(correo, nombre, apellidos, password, **extra_fields)

class Usuarios(AbstractBaseUser):
    IdUsuario = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=100)
    Apellidos = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    Telefono = models.CharField(max_length=20, blank=True, null=True)
    Pais = models.CharField(max_length=50)
    FechaDeNacimiento = models.DateField(null=True, blank=True)
    Genero = models.CharField(max_length=50, blank=True, null=True)
    ImgUsuario = models.BinaryField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['Nombre', 'Apellidos']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.Nombre} {self.Apellidos} ({self.correo})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

class Categorias(models.Model):
    IdCategoria = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=100)
    Descripcion = models.CharField(max_length=200)
    Estado = models.BooleanField(default=True)
    Imagen = models.BinaryField(null=True, blank=True)  # Guardar imagen en formato binario

    def __str__(self):
        return self.Nombre
    
class BannerCategorias(models.Model):
    IdBannerCat = models.AutoField(primary_key=True)
    IdCategoria = models.ForeignKey(Categorias, on_delete=models.CASCADE, related_name="banners")
    ImagenBanner = models.BinaryField(null=True, blank=True)  # Guardar imagen en binario
    Estado = models.BooleanField(default=True)  # Activo/Inactivo
    Orden = models.PositiveIntegerField(default=1)  # Para ordenar los banners
    FechaCreacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación automática

    def __str__(self):
        return f"Banner de {self.IdCategoria.Nombre} (Orden {self.Orden})"

    class Meta:
        ordering = ['Orden']  # Ordenar por número de orden ascendente
    
class Subcategorias(models.Model):
    IdSubCategoria = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=100)
    Descripcion = models.CharField(max_length=200)
    Estado = models.BooleanField(default=True)

    def __str__(self):
        return self.Nombre
    
class Productos(models.Model):
    IdProducto = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=150)
    SKU = models.CharField(max_length=50)
    Precio = models.DecimalField(max_digits=10, decimal_places=2)
    PrecioDescuento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    Stock = models.IntegerField()
    StockMax = models.IntegerField()
    StockMin = models.IntegerField()
    CalificacionPromedio = models.IntegerField(default=0)
    Vistas = models.IntegerField(default=0)
    Estado = models.BooleanField(default=True)
    FechaAgregado = models.DateTimeField(auto_now_add=True)
    Marca = models.CharField(max_length=100)
    Peso = models.DecimalField(max_digits=10, decimal_places=2)
    Descripcion = models.TextField()

    def __str__(self):
        return self.Nombre
    
class CategoriasProductos(models.Model):
    IdCategoriaProducto = models.AutoField(primary_key=True)
    IdProducto = models.ForeignKey('Productos', on_delete=models.CASCADE, related_name="categorias_productos")
    IdCategoria = models.ForeignKey('Categorias', on_delete=models.CASCADE, related_name="categorias_productos")

    def __str__(self):
        return f"{self.IdProducto.Nombre} - {self.IdCategoria.Nombre}"
    
class SubcategoriasProductos(models.Model):
    IdSubcategoriaProducto = models.AutoField(primary_key=True)
    IdProducto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name="subcategorias_productos")
    IdSubcategoria = models.ForeignKey(Subcategorias, on_delete=models.CASCADE, related_name="subcategorias_productos")

    def __str__(self):
        return f"{self.IdProducto.Nombre} - {self.IdSubcategoria.Nombre}"

class ImagenesProducto(models.Model):
    IdImagen = models.AutoField(primary_key=True)  # Identificador único de la imagen
    IdProducto = models.ForeignKey(
        'Productos',  # Referencia al modelo de Productos
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    Imagen = models.BinaryField()  # Campo para almacenar la imagen en formato binario
    EsPrincipal = models.BooleanField(default=False)  # Indicador si es la imagen principal
    FechaAgregado = models.DateTimeField(auto_now_add=True)  # Fecha en que se agregó la imagen

    def __str__(self):
        return f"Imagen de Producto {self.IdProducto.Nombre} (Principal: {self.EsPrincipal})"
    
class Favoritos(models.Model):
    IdFavoritos = models.AutoField(primary_key=True)
    IdUsuario = models.ForeignKey('Usuarios', on_delete=models.CASCADE, related_name='favoritos')
    IdProducto = models.ForeignKey('Productos', on_delete=models.CASCADE, related_name='favoritos')
    FechaAgregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Favorito: {self.IdUsuario.Nombre} - {self.IdProducto.Nombre}"

class Carrito(models.Model):
    IdCarrito = models.AutoField(primary_key=True)  # Identificador único del carrito
    IdUsuario = models.ForeignKey(
        'Usuarios',  # Relación con el modelo Usuarios
        on_delete=models.CASCADE,
        related_name='carritos'
    )
    IdProducto = models.ForeignKey(
        'Productos',  # Relación con el modelo Productos
        on_delete=models.CASCADE,
        related_name='carritos'
    )
    Cantidad = models.PositiveIntegerField(default=1)  # Cantidad de productos en el carrito
    FechaAgregado = models.DateTimeField(auto_now_add=True)  # Fecha y hora en que se agregó el producto

    def __str__(self):
        return f"Carrito - Usuario: {self.IdUsuario.Nombre}, Producto: {self.IdProducto.Nombre}, Cantidad: {self.Cantidad}"
    
class BannerHome(models.Model):
    IdBannerHome = models.AutoField(primary_key=True)
    Img = models.BinaryField()
    Url = models.URLField(max_length=500, blank=True, null=True)  # Nuevo campo para la URL asociada al banner
    Estado = models.BooleanField(default=True)
    EsPrincipal = models.BooleanField(default=False)
    FechaAgregado = models.DateTimeField(default=timezone.now)
    IdUsuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='banners')

    class Meta:
        verbose_name = "Banner Home"
        verbose_name_plural = "Banners Home"

    def __str__(self):
        return f"BannerHome {self.IdBannerHome}"
    
class HistorialVistas(models.Model):
    IdVista = models.AutoField(primary_key=True)
    Usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)  # Usuario que vio el producto
    Producto = models.ForeignKey(Productos, on_delete=models.CASCADE)  # Producto visto
    FechaVista = models.DateTimeField(auto_now_add=True)  # Fecha en que lo vio

    class Meta:
        verbose_name = "Historial de Vista"
        verbose_name_plural = "Historial de Vistas"

    def __str__(self):
        return f"{self.Usuario.Nombre} vio {self.Producto.Nombre} el {self.FechaVista}"

class OfertasHome(models.Model):
    IdOfertasHome = models.AutoField(primary_key=True)  # Identificador único de la oferta
    IdProducto = models.ForeignKey(
        'Productos',  # Relación con el modelo Productos
        on_delete=models.CASCADE,
        related_name='ofertas_home'
    )
    EsPrincipal = models.BooleanField(default=False)  # Indica si es una oferta destacada
    FechaAgregado = models.DateTimeField(auto_now_add=True)  # Fecha de creación de la oferta

    def __str__(self):
        return f"Oferta {self.IdOfertasHome} - Producto {self.IdProducto.Nombre} (Principal: {self.EsPrincipal})"

    class Meta:
        verbose_name = "Oferta Home"
        verbose_name_plural = "Ofertas Home"
        ordering = ['-FechaAgregado']

class BannersItems(models.Model):
    IdBannersItems = models.AutoField(primary_key=True)  # Identificador único
    Titulo = models.CharField(max_length=255)  # Título del banner
    Producto1 = models.ForeignKey('Productos', on_delete=models.CASCADE, related_name='banner_producto1')
    Producto2 = models.ForeignKey('Productos', on_delete=models.CASCADE, related_name='banner_producto2')
    Producto3 = models.ForeignKey('Productos', on_delete=models.CASCADE, related_name='banner_producto3')
    Producto4 = models.ForeignKey('Productos', on_delete=models.CASCADE, related_name='banner_producto4')
    Imagen = models.BinaryField(null=True, blank=True)  # Imagen del banner en binario (varbinary)
    FechaAgregada = models.DateTimeField(auto_now_add=True)  # Fecha de creación del banner
    IdUsuario = models.ForeignKey('Usuarios', on_delete=models.CASCADE, related_name='banners_creados')  # Usuario que creó el banner

    def __str__(self):
        return f"{self.Titulo} - {self.FechaAgregada.strftime('%Y-%m-%d')}"
    
class Direcciones(models.Model):
    IdDirecciones = models.AutoField(primary_key=True)
    Estado = models.CharField(max_length=100)
    CP = models.CharField(max_length=10)
    Municipio = models.CharField(max_length=100)
    Ciudad = models.CharField(max_length=100)
    Colonia = models.CharField(max_length=150)
    Calle = models.CharField(max_length=150)
    Numero_Exterior = models.CharField(max_length=10)
    Numero_Interior = models.CharField(max_length=10, null=True, blank=True)
    Referencias = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.Calle} #{self.Numero_Exterior}, {self.Colonia}, {self.Ciudad}, {self.Estado} - {self.CP}"
    
class DireccionesUsuario(models.Model):
    IdDireccionUsuario = models.AutoField(primary_key=True)
    IdDirecciones = models.ForeignKey('Direcciones', on_delete=models.CASCADE, related_name='usuarios_direccion')
    IdUsuario = models.ForeignKey('Usuarios', on_delete=models.CASCADE, related_name='direcciones_usuario')

    class Meta:
        verbose_name = 'Dirección de Usuario'
        verbose_name_plural = 'Direcciones de Usuarios'
        unique_together = ('IdDirecciones', 'IdUsuario')  # Evita registros duplicados de la misma dirección para el mismo usuario

    def __str__(self):
        return f"Dirección {self.IdDirecciones_id} - Usuario {self.IdUsuario_id}"
    
class Pedido(models.Model):
    IdPedido = models.AutoField(primary_key=True)
    IdUsuario = models.ForeignKey('Usuarios', on_delete=models.CASCADE, related_name='pedidos')
    IdDirecciones = models.ForeignKey(Direcciones, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_envio')
    Estado = models.CharField(max_length=50)  # Ejemplo: "Pendiente", "Pagado", "Enviado"
    FechaPedido = models.DateTimeField(auto_now_add=True)
    Total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Pedido {self.IdPedido} - Usuario {self.IdUsuario.Nombre} {self.IdUsuario.Apellidos} - Dirección {self.IdDirecciones if self.IdDirecciones else 'No asignada'}"

class DetallePedido(models.Model):
    IdDetalle = models.AutoField(primary_key=True)
    IdPedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    IdProducto = models.ForeignKey('Productos', on_delete=models.CASCADE, related_name='detalles_pedido')
    Cantidad = models.PositiveIntegerField()
    PrecioUnitario = models.DecimalField(max_digits=10, decimal_places=2)
    Subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle {self.IdDetalle} - Pedido {self.IdPedido.IdPedido} - Producto {self.IdProducto.Nombre}"

class Pago(models.Model):
    IdPago = models.AutoField(primary_key=True)
    IdPedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='pagos')
    Metodo = models.CharField(max_length=50)  # Ejemplo: "Tarjeta", "PayPal", "MercadoPago"
    FechaPago = models.DateTimeField(auto_now_add=True)
    Monto = models.DecimalField(max_digits=10, decimal_places=2)
    TransaccionId = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Pago {self.IdPago} - Pedido {self.IdPedido.IdPedido} - {self.Metodo}"