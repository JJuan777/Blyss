from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

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

    def __str__(self):
        return self.Nombre
    
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
    IdProducto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name="categorias_productos")
    IdCategoria = models.ForeignKey(Categorias, on_delete=models.CASCADE, related_name="categorias_productos")

    def __str__(self):
        return f"{self.IdProducto.Nombre} - {self.IdCategoria.Nombre}"
    
class SubcategoriasProductos(models.Model):
    IdSubcategoriaProducto = models.AutoField(primary_key=True)
    IdProducto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name="subcategorias_productos")
    IdSubcategoria = models.ForeignKey(Subcategorias, on_delete=models.CASCADE, related_name="subcategorias_productos")

    def __str__(self):
        return f"{self.IdProducto.Nombre} - {self.IdSubcategoria.Nombre}"
