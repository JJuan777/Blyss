from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from .models import Usuarios
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Productos, Categorias, Subcategorias, CategoriasProductos, SubcategoriasProductos, ImagenesProducto, Favoritos, Carrito
from .models import BannersItems, BannerCategorias, BannerHome, OfertasHome, Direcciones, DireccionesUsuario, Pedido, DetallePedido, Pago
from django.core.paginator import Paginator
from django.db.models import F
import base64
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum
from django.db.models import Q
from django.db.models import F, ExpressionWrapper, FloatField
from django.utils import timezone
import uuid
from django.db.models import Prefetch
from .models import Usuarios, UsuarioRol, Roles, UsuarioPermiso, Permisos
from django.utils.timezone import localtime

def index(request):
    # 1️⃣ **Banners ordenados: el principal primero, luego por fecha**
    banners = list(BannerHome.objects.filter(Estado=True).order_by('-EsPrincipal', '-FechaAgregado'))

    # 2️⃣ **Sección: Último Favorito**
    ultimo_favorito = Favoritos.objects.order_by('-FechaAgregado').first()
    dynamic_product = None
    product_img_base64 = None
    descuento = None

    if ultimo_favorito:
        dynamic_product = ultimo_favorito.IdProducto
        imagen = dynamic_product.imagenes.filter(EsPrincipal=True).first() or dynamic_product.imagenes.first()
        product_img_base64 = imagen.Imagen if imagen else None  # Imagen en base64

        if dynamic_product.PrecioDescuento and dynamic_product.Precio > dynamic_product.PrecioDescuento:
            descuento = round(100 - (dynamic_product.PrecioDescuento * 100 / dynamic_product.Precio))

    # 3️⃣ **Sección: Productos Recomendados (Calificación + Vistas)**
    productos_recomendados = Productos.objects.filter(Estado=True).order_by('-CalificacionPromedio', '-Vistas')[:8]
    productos_con_imagenes = []

    for producto in productos_recomendados:
        img_producto = producto.imagenes.filter(EsPrincipal=True).first() or producto.imagenes.first()
        img_base64 = img_producto.Imagen if img_producto else None

        descuento_producto = None
        if producto.PrecioDescuento and producto.Precio > producto.PrecioDescuento:
            descuento_producto = round(100 - (producto.PrecioDescuento * 100 / producto.Precio))

        productos_con_imagenes.append({
            'producto': producto,
            'img_base64': img_base64,
            'descuento': descuento_producto
        })

    # 5️⃣ **Sección: Cómpralo de Nuevo (Último producto comprado)**
    producto_comprado = None
    producto_comprado_img = None

    if request.user.is_authenticated:
        usuario_actual = request.user

        # Obtener el último pedido pagado del usuario
        ultimo_pedido = Pedido.objects.filter(IdUsuario=usuario_actual, Estado="En camino").order_by('-FechaPedido').first()

        if ultimo_pedido:
            ultimo_detalle = DetallePedido.objects.filter(IdPedido=ultimo_pedido).order_by('-IdDetalle').first()

            if ultimo_detalle:
                producto_comprado = ultimo_detalle.IdProducto
                img_producto = producto_comprado.imagenes.filter(EsPrincipal=True).first() or producto_comprado.imagenes.first()
                producto_comprado_img = img_producto.Imagen if img_producto else None

    # 4️⃣ **Sección: Ofertas Destacadas**
    oferta_principal = OfertasHome.objects.filter(EsPrincipal=True).first()
    producto_principal = oferta_principal.IdProducto if oferta_principal else None
    producto_principal_img = None
    descuento_principal = None

    if producto_principal:
        img_principal = producto_principal.imagenes.filter(EsPrincipal=True).first() or producto_principal.imagenes.first()
        producto_principal_img = img_principal.Imagen if img_principal else None

        if producto_principal.PrecioDescuento and producto_principal.Precio > producto_principal.PrecioDescuento:
            descuento_principal = round(100 - (producto_principal.PrecioDescuento * 100 / producto_principal.Precio))

    # Productos en oferta (excepto el principal)
    productos_en_oferta = OfertasHome.objects.exclude(IdProducto=producto_principal).order_by('-FechaAgregado')[:8]
    productos_en_carrusel = []

    for oferta in productos_en_oferta:
        producto = oferta.IdProducto
        img_producto = producto.imagenes.filter(EsPrincipal=True).first() or producto.imagenes.first()
        img_base64 = img_producto.Imagen if img_producto else None

        descuento_producto = None
        if producto.PrecioDescuento and producto.Precio > producto.PrecioDescuento:
            descuento_producto = round(100 - (producto.PrecioDescuento * 100 / producto.Precio))

        productos_en_carrusel.append({
            'producto': producto,
            'img_base64': img_base64,
            'descuento': descuento_producto
        })

    # 5️⃣ **Sección: Basado en tu Carrito (Solo si el usuario está autenticado)**
    productos_carrito = []

    if request.user.is_authenticated:
        usuario_actual = request.user
        productos_en_carrito = Carrito.objects.filter(IdUsuario=usuario_actual)

        categorias_ids = set()
        subcategorias_ids = set()

        for item in productos_en_carrito:
            producto = item.IdProducto

            categorias = CategoriasProductos.objects.filter(IdProducto=producto).values_list('IdCategoria', flat=True)
            subcategorias = SubcategoriasProductos.objects.filter(IdProducto=producto).values_list('IdSubcategoria', flat=True)

            categorias_ids.update(categorias)
            subcategorias_ids.update(subcategorias)

        productos_relacionados = Productos.objects.filter(
            Estado=True,
            categorias_productos__IdCategoria__in=categorias_ids,
            subcategorias_productos__IdSubcategoria__in=subcategorias_ids
        ).exclude(
            IdProducto__in=productos_en_carrito.values_list('IdProducto', flat=True)
        ).distinct()[:8]

        for prod in productos_relacionados:
            img_producto = prod.imagenes.filter(EsPrincipal=True).first() or prod.imagenes.first()
            img_base64 = img_producto.Imagen if img_producto else None

            descuento_producto = None
            if prod.PrecioDescuento and prod.Precio > prod.PrecioDescuento:
                descuento_producto = round(100 - (prod.PrecioDescuento * 100 / prod.Precio))

            productos_carrito.append({
                'producto': prod,
                'img_base64': img_base64,
                'descuento': descuento_producto
            })

    # 6️⃣ **Sección: Banners Dinámicos**
    banners_items = BannersItems.objects.order_by('-FechaAgregada')[:3]
    banners_data = []

    for banner in banners_items:
        imagen_banner = banner.Imagen if banner.Imagen else None
        productos = [banner.Producto1, banner.Producto2, banner.Producto3, banner.Producto4]

        productos_info = []
        for producto in productos:
            img_producto = producto.imagenes.filter(EsPrincipal=True).first() or producto.imagenes.first()
            img_base64 = img_producto.Imagen if img_producto else None

            productos_info.append({
                'producto': producto,
                'img_base64': img_base64
            })

        banners_data.append({
            'titulo': banner.Titulo,
            'imagen_banner': imagen_banner,
            'productos': productos_info
        })

    # **📌 Contexto de la Vista**
    context = {
        'banners': banners,
        'dynamic_product': dynamic_product,
        'product_img_base64': product_img_base64,
        'descuento': descuento,
        'productos_recomendados': productos_con_imagenes,
        'producto_principal': producto_principal,
        'producto_principal_img': producto_principal_img,
        'descuento_principal': descuento_principal,
        'productos_en_carrusel': productos_en_carrusel,
        'productos_carrito': productos_carrito if request.user.is_authenticated else None,
        'banners_data': banners_data,  # Sección de banners dinámicos
        'producto_comprado': producto_comprado,
        'producto_comprado_img': producto_comprado_img,
    }

    return render(request, 'Blyss/index.html', context)

def registro_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

        # Verificar que todos los campos estén completos
        if not all([nombre, apellidos, correo, password, fecha_nacimiento]):
            return JsonResponse({'status': 'error', 'message': 'Todos los campos son requeridos.'})

        # Validar formato del correo
        try:
            validate_email(correo)
        except ValidationError:
            return JsonResponse({'status': 'error', 'message': 'El correo electrónico no es válido.'})

        # Validar longitud de la contraseña
        if len(password) < 6:
            return JsonResponse({'status': 'error', 'message': 'La contraseña debe tener al menos 6 caracteres.'})

        # Validar si el correo ya está registrado
        if Usuarios.objects.filter(correo=correo).exists():
            return JsonResponse({'status': 'error', 'message': 'El correo ya está registrado.'})

        # Validar formato de la fecha de nacimiento
        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Fecha de nacimiento no válida.'})

        # Validar que la fecha de nacimiento sea razonable (mayor de 18 años)
        hoy = datetime.today().date()
        if (hoy.year - fecha_nacimiento.year) < 18:
            return JsonResponse({'status': 'error', 'message': 'Debes tener al menos 18 años.'})

        # Crear el usuario
        usuario = Usuarios.objects.create(
            Nombre=nombre,
            Apellidos=apellidos,
            correo=correo,
            password=make_password(password),
            FechaDeNacimiento=fecha_nacimiento
        )
        return JsonResponse({'status': 'success', 'message': 'Usuario registrado exitosamente.'})

    return render(request, 'Blyss/register.html')

# Configuración
MAX_ATTEMPTS = 5  # Número máximo de intentos permitidos
BLOCK_DURATION = 600  # Duración del bloqueo en segundos (10 minutos)

def get_client_ip(request):
    """Obtiene la IP del cliente desde el encabezado de la solicitud."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def login_view(request):
    ip = get_client_ip(request)  # Obtener la IP del cliente
    key = f"login_attempts_{ip}"  # Clave para rastrear intentos fallidos
    attempts = cache.get(key, 0)  # Recuperar intentos fallidos de la caché

    if attempts >= MAX_ATTEMPTS:
        # Bloquear acceso por exceder intentos fallidos
        return JsonResponse({
            'status': 'error',
            'message': 'Demasiados intentos fallidos. Inténtalo de nuevo en 10 minutos.'
        })

    if request.method == 'POST':
        correo = request.POST.get('correo')
        password = request.POST.get('password')

        if not correo or not password:
            return JsonResponse({'status': 'error', 'message': 'Todos los campos son requeridos.'})

        usuario = authenticate(request, username=correo, password=password)
        if usuario is not None:
            # Inicio de sesión exitoso
            login(request, usuario)
            cache.delete(key)  # Reiniciar intentos fallidos al iniciar sesión
            return JsonResponse({'status': 'success', 'message': 'Inicio de sesión exitoso.'})
        else:
            # Incrementar contador de intentos fallidos
            attempts += 1
            cache.set(key, attempts, BLOCK_DURATION)
            return JsonResponse({
                'status': 'error',
                'message': f'Credenciales inválidas. Intentos restantes: {MAX_ATTEMPTS - attempts}'
            })

    return render(request, 'Blyss/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def admin_view(request):
    return render(request, 'Blyss/Admin/index.html')

@login_required
def inventario_view(request):
    # Obtener el total de productos
    total_productos = Productos.objects.count()

    # Obtener el total de categorías
    total_categorias = CategoriasProductos.objects.values('IdCategoria').distinct().count()

    # Obtener el número de categorías agregadas en los últimos 7 días
    ultima_semana = now() - timedelta(days=7)
    nuevas_categorias = CategoriasProductos.objects.filter(IdProducto__FechaAgregado__gte=ultima_semana).values('IdCategoria').distinct().count()

    # Obtener el último producto agregado
    ultimo_producto = Productos.objects.order_by('-FechaAgregado').first()
    
    # Calcular el tiempo transcurrido
    if ultimo_producto:
        diferencia_tiempo = now() - ultimo_producto.FechaAgregado
        if diferencia_tiempo.days > 0:
            tiempo_transcurrido = f"Hace {diferencia_tiempo.days} días"
        elif diferencia_tiempo.seconds >= 3600:
            tiempo_transcurrido = f"Hace {diferencia_tiempo.seconds // 3600} horas"
        elif diferencia_tiempo.seconds >= 60:
            tiempo_transcurrido = f"Hace {diferencia_tiempo.seconds // 60} minutos"
        else:
            tiempo_transcurrido = "Hace unos segundos"

        # Limitar el nombre del producto a 30 caracteres y agregar "..."
        nombre_producto = ultimo_producto.Nombre
        if len(nombre_producto) > 30:
            nombre_producto = nombre_producto[:30] + "..."
        
        producto_id = ultimo_producto.IdProducto  # Obtener el ID del producto

    else:
        ultimo_producto = None
        tiempo_transcurrido = "No hay productos recientes"
        nombre_producto = None
        producto_id = None  # Evitar errores en la plantilla si no hay productos

    return render(request, 'Blyss/Admin/Inventario/index.html', {
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'nuevas_categorias': nuevas_categorias,
        'ultimo_producto': ultimo_producto,
        'nombre_producto': nombre_producto,
        'producto_id': producto_id,  # Pasamos el ID al contexto
        'tiempo_transcurrido': tiempo_transcurrido
    })

@login_required
def productos_view(request):
    return render(request, 'Blyss/Admin/Inventario/Productos/Productos.html')

@login_required
def obtener_productos(request):
    productos = Productos.objects.all()

    # Obtener los parámetros de ordenación
    order_by = request.GET.get('order_by', 'Nombre')  # Por defecto, ordenar por Nombre
    order_direction = request.GET.get('order_direction', 'asc')  # Dirección predeterminada: ascendente

    # Aplica la dirección de ordenación
    if order_direction == 'desc':
        order_by = f"-{order_by}"

    productos = productos.order_by(order_by)

    # Paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(productos, 20)

    try:
        productos_page = paginator.page(page_number)
    except:
        return JsonResponse({'productos': [], 'has_next': False, 'has_prev': False})

    productos_data = []
    
    for producto in productos_page:
        # Obtener la imagen principal en base64
        imagen_principal = producto.imagenes.filter(EsPrincipal=True).first()
        if not imagen_principal:
            imagen_principal = producto.imagenes.order_by('-FechaAgregado').first()
        
        imagen_base64 = None
        if imagen_principal and imagen_principal.Imagen:
            imagen_base64 = base64.b64encode(imagen_principal.Imagen).decode("utf-8")

        productos_data.append({
            'IdProducto': producto.IdProducto,
            'nombre': producto.Nombre,
            'sku': producto.SKU,
            'stock': producto.Stock,
            'precio': producto.Precio,
            'marca': producto.Marca,
            'estado': 'Activo' if producto.Estado else 'Inactivo',
            'imagen': f"data:image/jpeg;base64,{imagen_base64}" if imagen_base64 else None
        })

    return JsonResponse({
        'productos': productos_data,
        'has_next': productos_page.has_next(),
        'has_prev': productos_page.has_previous(),
        'current_page': productos_page.number,
        'total_pages': paginator.num_pages,
    })

@login_required
def addproductos_view(request):
    categorias = Categorias.objects.filter(Estado=True)  # Solo categorías activas
    subcategorias = Subcategorias.objects.filter(Estado=True)  # Solo categorías activas
    return render(request, 'Blyss/Admin/Inventario/Productos/addProducto.html', {'categorias': categorias, 'subcategorias': subcategorias})

@csrf_exempt
def add_producto_view(request):
    if request.method == "POST":
        try:
            # Procesar los datos del formulario
            data = request.POST
            estado = data.get("estado") == "1"

            # Crear el producto
            producto = Productos.objects.create(
                Nombre=data.get("nombre"),
                SKU=data.get("sku"),
                Precio=data.get("precio"),
                PrecioDescuento=data.get("precio_descuento") or 0.0,
                Stock=data.get("stock"),
                StockMax=data.get("stock_max"),
                StockMin=data.get("stock_min"),
                Estado=estado,
                Marca=data.get("marca"),
                Peso=data.get("peso"),
                Descripcion=data.get("descripcion"),
            )

            # Registrar la categoría
            categoria_id = data.get("categoria")
            if categoria_id:
                producto.categorias_productos.create(IdCategoria_id=categoria_id)

            # Registrar la subcategoría
            subcategoria_id = data.get("subcategoria")
            if subcategoria_id:
                producto.subcategorias_productos.create(IdSubcategoria_id=subcategoria_id)

            # Procesar las imágenes cargadas
            for imagen in request.FILES.getlist("imagenes"):
                if ImagenesProducto.objects.filter(IdProducto=producto).count() >= 10:
                    break  # No permitir más de 10 imágenes

                ImagenesProducto.objects.create(
                    IdProducto=producto,
                    Imagen=imagen.read(),
                    EsPrincipal=False,  # Se pueden ajustar reglas para seleccionar la imagen principal
                )

            return JsonResponse({"success": True, "message": "Producto registrado exitosamente"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)

@login_required
def detproducto_view(request, producto_id):
    # Obtener el producto
    producto = get_object_or_404(Productos, pk=producto_id)

    # Obtener la categoría y subcategoría asociadas al producto
    categoria_producto = CategoriasProductos.objects.filter(IdProducto=producto).first()
    subcategoria_producto = SubcategoriasProductos.objects.filter(IdProducto=producto).first()

    # Obtener todas las categorías y subcategorías
    categorias = Categorias.objects.all()
    subcategorias = Subcategorias.objects.all()

    # Obtener las imágenes asociadas al producto
    imagenes_producto = ImagenesProducto.objects.filter(IdProducto=producto)

    context = {
        "producto": producto,
        "categoria_producto": categoria_producto.IdCategoria.IdCategoria if categoria_producto else None,
        "subcategoria_producto": subcategoria_producto.IdSubcategoria.IdSubCategoria if subcategoria_producto else None,
        "categorias": categorias,
        "subcategorias": subcategorias,
        "imagenes_producto": imagenes_producto,
    }

    return render(request, "Blyss/Admin/Inventario/Productos/detProducto.html", context)
    
@login_required
def cargar_imagen_view(request, producto_id):
    if request.method == "POST":
        try:
            producto = get_object_or_404(Productos, pk=producto_id)

            # Verificar el límite de imágenes
            total_imagenes = ImagenesProducto.objects.filter(IdProducto=producto).count()
            imagenes_subidas = request.FILES.getlist("imagenes")  # Obtener todas las imágenes enviadas

            if total_imagenes + len(imagenes_subidas) > 10:
                return JsonResponse({"success": False, "message": "No puedes cargar más de 10 imágenes para este producto."})

            # Verificar si ya existe una imagen principal
            ya_tiene_principal = ImagenesProducto.objects.filter(IdProducto=producto, EsPrincipal=True).exists()

            imagenes_guardadas = []
            for imagen in imagenes_subidas:
                es_principal = request.POST.get("es_principal") == "true"

                # Si ya hay una imagen principal, no permitir otra
                if es_principal and ya_tiene_principal:
                    continue  

                nueva_imagen = ImagenesProducto.objects.create(
                    IdProducto=producto,
                    Imagen=imagen.read(),
                    EsPrincipal=es_principal,
                )
                imagenes_guardadas.append({
                    "IdImagen": nueva_imagen.IdImagen,
                    "EsPrincipal": nueva_imagen.EsPrincipal,
                    "FechaAgregado": nueva_imagen.FechaAgregado.strftime("%d/%m/%Y %H:%M")
                })

                if es_principal:
                    ya_tiene_principal = True  # Evitar que se guarden más imágenes principales

            return JsonResponse({"success": True, "message": "Imágenes cargadas correctamente.", "imagenes": imagenes_guardadas})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido."})

@csrf_exempt
def eliminar_imagen_view(request, imagen_id):
    if request.method == "POST":
        try:
            # Obtener la imagen por su ID
            imagen = get_object_or_404(ImagenesProducto, pk=imagen_id)
            imagen.delete()

            return JsonResponse({"success": True, "message": "Imagen eliminada correctamente."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Método no permitido."})

@login_required
@csrf_exempt
def actualizar_producto_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            producto_id = data.get("producto_id")
            producto = get_object_or_404(Productos, pk=producto_id)

            # Actualizar los campos básicos del producto
            producto.Nombre = data.get("nombre", producto.Nombre)
            producto.SKU = data.get("sku", producto.SKU)
            producto.Precio = data.get("precio", producto.Precio)
            producto.PrecioDescuento = data.get("precio_descuento", producto.PrecioDescuento)
            producto.Stock = data.get("stock", producto.Stock)
            producto.Descripcion = data.get("descripcion", producto.Descripcion)
            producto.Estado = data.get("estado", producto.Estado)
            producto.save()

            # Actualizar categoría del producto
            categoria_id = data.get("categoria_id")
            if categoria_id:
                categoria = get_object_or_404(Categorias, pk=categoria_id)
                CategoriasProductos.objects.update_or_create(
                    IdProducto=producto,
                    defaults={"IdCategoria": categoria},
                )

            # Actualizar subcategoría del producto
            subcategoria_id = data.get("subcategoria_id")
            if subcategoria_id:
                subcategoria = get_object_or_404(Subcategorias, pk=subcategoria_id)
                SubcategoriasProductos.objects.update_or_create(
                    IdProducto=producto,
                    defaults={"IdSubcategoria": subcategoria},
                )

            return JsonResponse({"success": True, "message": "Producto actualizado correctamente."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido."})

@csrf_exempt
def eliminar_producto_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            producto_id = data.get("producto_id")

            # Verificar que el producto existe
            producto = get_object_or_404(Productos, pk=producto_id)

            # Eliminar el producto
            producto.delete()

            return JsonResponse({"success": True, "message": "Producto eliminado correctamente."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido."})

@login_required
def categorias_view(request):
    return render(request, 'Blyss/Admin/Inventario/Categorias/index.html')

@login_required
def obtener_categorias(request):
    categorias = Categorias.objects.all()

    # Parámetros de ordenación
    order_by = request.GET.get('order_by', 'Nombre')  # Ordenar por Nombre por defecto
    order_direction = request.GET.get('order_direction', 'asc')  # Dirección predeterminada: ascendente

    if order_direction == 'desc':
        order_by = f"-{order_by}"

    categorias = categorias.order_by(order_by)

    # Paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(categorias, 20)  # 20 categorías por página

    try:
        categorias_page = paginator.page(page_number)
    except:
        return JsonResponse({'categorias': [], 'has_next': False, 'has_prev': False})

    categorias_data = [
        {
            'id': categoria.IdCategoria,
            'nombre': categoria.Nombre,
            'descripcion': categoria.Descripcion,
            'estado': 'Activo' if categoria.Estado else 'Inactivo',
        }
        for categoria in categorias_page
    ]

    return JsonResponse({
        'categorias': categorias_data,
        'has_next': categorias_page.has_next(),
        'has_prev': categorias_page.has_previous(),
        'current_page': categorias_page.number,
        'total_pages': paginator.num_pages,
    })

@login_required
def addcategorias_view(request):
    return render(request, 'Blyss/Admin/Inventario/Categorias/addCategorias.html')

@csrf_exempt
@login_required
def addcategoria_view(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            estado = request.POST.get('estado', 'True') == 'True'  # Convierte string en booleano
            imagen = request.FILES.get('imagen', None)  # Obtener archivo de imagen

            # Validaciones básicas
            if not nombre:
                return JsonResponse({'success': False, 'message': 'El nombre es obligatorio.'})
            if len(nombre) > 100:
                return JsonResponse({'success': False, 'message': 'El nombre no puede exceder los 100 caracteres.'})
            if len(descripcion) > 200:
                return JsonResponse({'success': False, 'message': 'La descripción no puede exceder los 200 caracteres.'})

            # Guardar la imagen en formato binario
            imagen_data = imagen.read() if imagen else None

            # Crear la categoría
            categoria = Categorias.objects.create(
                Nombre=nombre,
                Descripcion=descripcion,
                Estado=estado,
                Imagen=imagen_data
            )

            return JsonResponse({'success': True, 'message': 'Categoría creada exitosamente.', 'categoria_id': categoria.IdCategoria})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al crear la categoría: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def detcategoria_viewad(request, id):
    # Obtener la categoría o devolver un error 404 si no existe
    categoria = get_object_or_404(Categorias, IdCategoria=id)

    return render(request, 'Blyss/Admin/Inventario/Categorias/detCategorias.html', {
        'categoria': categoria
    })

@csrf_exempt
@login_required
def updatecategoria_view(request, id):
    if request.method == 'POST':
        try:
            categoria = Categorias.objects.get(IdCategoria=id)

            # Obtener datos del formulario
            nombre = request.POST.get("nombre", "").strip()
            descripcion = request.POST.get("descripcion", "").strip()
            estado = request.POST.get("estado", "True") == "True"
            imagen = request.FILES.get("imagen", None)
            eliminar_imagen = request.POST.get("eliminar_imagen", "False") == "True"  # Bandera de eliminación

            # Validaciones
            if not nombre:
                return JsonResponse({'success': False, 'message': 'El nombre es obligatorio.'})
            if len(nombre) > 100:
                return JsonResponse({'success': False, 'message': 'El nombre no puede exceder los 100 caracteres.'})
            if len(descripcion) > 200:
                return JsonResponse({'success': False, 'message': 'La descripción no puede exceder los 200 caracteres.'})

            # Actualizar datos
            categoria.Nombre = nombre
            categoria.Descripcion = descripcion
            categoria.Estado = estado

            # Manejo de imágenes
            if eliminar_imagen:
                categoria.Imagen = None  # Eliminar imagen si el usuario la quitó
            elif imagen:
                categoria.Imagen = imagen.read()  # Guardar la nueva imagen

            categoria.save()

            return JsonResponse({'success': True, 'message': 'Categoría actualizada correctamente.'})
        except Categorias.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'La categoría no existe.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
@csrf_exempt
def deletecategoria_view(request, id):
    if request.method == "DELETE":
        try:
            # Obtener la categoría
            categoria = Categorias.objects.get(IdCategoria=id)
            categoria.delete()

            return JsonResponse({"success": True, "message": "Categoría eliminada correctamente."})
        except Categorias.DoesNotExist:
            return JsonResponse({"success": False, "message": "La categoría no existe."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido."})

@login_required
def subcategorias_view(request):
    return render(request, 'Blyss/Admin/Inventario/SubCategorias/index.html')

@login_required
def obtener_subcategorias(request):
    subcategorias = Subcategorias.objects.all()

    # Parámetros de ordenación
    order_by = request.GET.get('order_by', 'Nombre')  # Por defecto, ordenar por Nombre
    order_direction = request.GET.get('order_direction', 'asc')  # Dirección por defecto: ascendente

    if order_direction == 'desc':
        order_by = f"-{order_by}"

    subcategorias = subcategorias.order_by(order_by)

    # Paginación
    page_number = request.GET.get('page', 1)
    paginator = Paginator(subcategorias, 20)  # 20 subcategorías por página

    try:
        subcategorias_page = paginator.page(page_number)
    except:
        return JsonResponse({'subcategorias': [], 'has_next': False, 'has_prev': False})

    subcategorias_data = [
        {
            'id': subcategoria.IdSubCategoria,
            'nombre': subcategoria.Nombre,
            'descripcion': subcategoria.Descripcion,
            'estado': 'Activo' if subcategoria.Estado else 'Inactivo',
        }
        for subcategoria in subcategorias_page
    ]

    return JsonResponse({
        'subcategorias': subcategorias_data,
        'has_next': subcategorias_page.has_next(),
        'has_prev': subcategorias_page.has_previous(),
        'current_page': subcategorias_page.number,
        'total_pages': paginator.num_pages,
    })

@login_required
def addsubcategorias_view(request):
    return render(request, 'Blyss/Admin/Inventario/SubCategorias/addSubCategoria.html')

@login_required
@csrf_exempt
def addsubcategoria_view(request):
    if request.method == 'POST':
        try:
            # Obtener datos enviados por AJAX
            data = json.loads(request.body)
            nombre = data.get('nombre', '').strip()
            descripcion = data.get('descripcion', '').strip()
            estado = data.get('estado', True)  # Por defecto, estado activo

            # Validaciones básicas
            if not nombre:
                return JsonResponse({'success': False, 'message': 'El nombre es obligatorio.'})
            if len(nombre) > 100:
                return JsonResponse({'success': False, 'message': 'El nombre no puede exceder los 100 caracteres.'})
            if len(descripcion) > 200:
                return JsonResponse({'success': False, 'message': 'La descripción no puede exceder los 200 caracteres.'})

            # Crear subcategoría
            subcategoria = Subcategorias.objects.create(
                Nombre=nombre,
                Descripcion=descripcion,
                Estado=estado
            )

            return JsonResponse({'success': True, 'message': 'Subcategoría creada exitosamente.', 'id': subcategoria.IdSubCategoria})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al crear la subcategoría: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
@csrf_exempt
def updatesubcategoria_view(request, id):
    if request.method == "POST":
        try:
            subcategoria = Subcategorias.objects.get(IdSubCategoria=id)
            data = json.loads(request.body)
            subcategoria.Nombre = data.get("nombre", subcategoria.Nombre).strip()
            subcategoria.Descripcion = data.get("descripcion", subcategoria.Descripcion).strip()
            subcategoria.Estado = data.get("estado", "True") == "True"
            subcategoria.save()
            return JsonResponse({"success": True, "message": "Subcategoría actualizada correctamente."})
        except Subcategorias.DoesNotExist:
            return JsonResponse({"success": False, "message": "La subcategoría no existe."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Método no permitido."})

@login_required
@csrf_exempt
def deletesubcategoria_view(request, id):
    if request.method == "DELETE":
        try:
            subcategoria = Subcategorias.objects.get(IdSubCategoria=id)
            subcategoria.delete()
            return JsonResponse({"success": True, "message": "Subcategoría eliminada correctamente."})
        except Subcategorias.DoesNotExist:
            return JsonResponse({"success": False, "message": "La subcategoría no existe."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Método no permitido."})

@login_required
def detsubcategoria_view(request, id):
    # Obtener la subcategoría por su ID o devolver un 404 si no existe
    subcategoria = get_object_or_404(Subcategorias, IdSubCategoria=id)

    # Renderizar la plantilla con los detalles de la subcategoría
    return render(request, 'Blyss/Admin/Inventario/Subcategorias/detSubcategoria.html', {
        'subcategoria': subcategoria
    })

@login_required
def producto_view(request, producto_id):
    # Obtén el producto actual
    producto = get_object_or_404(Productos, pk=producto_id)

    # Calcula el porcentaje de descuento correctamente
    porcentaje_descuento = None
    if producto.PrecioDescuento and producto.Precio > producto.PrecioDescuento:
        porcentaje_descuento = round(((producto.Precio - producto.PrecioDescuento) / producto.Precio) * 100)

    # Obtén todas las categorías del producto actual
    categorias_ids = list(producto.categorias_productos.values_list('IdCategoria', flat=True))

    # Obtén todas las subcategorías del producto actual
    subcategorias_ids = list(producto.subcategorias_productos.values_list('IdSubcategoria', flat=True))

    # Encuentra productos relacionados (categorías y subcategorías)
    productos_relacionados = Productos.objects.filter(
        categorias_productos__IdCategoria__in=categorias_ids
    ).exclude(IdProducto=producto.IdProducto)

    subproductos_relacionados = Productos.objects.filter(
        subcategorias_productos__IdSubcategoria__in=subcategorias_ids
    ).exclude(IdProducto=producto.IdProducto)

    # Combinar y limitar los resultados a 4 productos
    productos_relacionados = (productos_relacionados | subproductos_relacionados).distinct()[:4]

    # Verifica si el usuario tiene productos en su carrito
    tiene_carrito = Carrito.objects.filter(IdUsuario=request.user, IdProducto=producto).exists()

    # Verifica si el producto actual está en los favoritos del usuario
    usuario = request.user
    en_favoritos = usuario.favoritos.filter(IdProducto=producto).exists()

    return render(request, 'Blyss/Producto/index.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
        'porcentaje_descuento': porcentaje_descuento,  # Pasa el porcentaje al contexto
        'en_favoritos': en_favoritos,  # Agrega esta variable al contexto
        'tiene_carrito': tiene_carrito,  # Verificar si el producto está en el carrito
    })

@login_required
def toggle_favorites(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')

        # Verifica si el producto existe
        producto = Productos.objects.filter(IdProducto=producto_id).first()
        if not producto:
            return JsonResponse({'success': False, 'message': 'El producto no existe.'}, status=404)

        # Verifica si el producto ya está en favoritos
        usuario = request.user
        favorito = Favoritos.objects.filter(IdUsuario=usuario, IdProducto=producto).first()

        if favorito:
            # Si ya está en favoritos, elimínalo
            favorito.delete()
            return JsonResponse({'success': True, 'message': 'Producto eliminado de favoritos.', 'favorito': False})
        else:
            # Si no está en favoritos, añádelo
            Favoritos.objects.create(IdUsuario=usuario, IdProducto=producto)
            return JsonResponse({'success': True, 'message': 'Producto añadido a favoritos.', 'favorito': True})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))

        # Verifica si el producto existe
        producto = Productos.objects.filter(IdProducto=producto_id).first()
        if not producto:
            return JsonResponse({'success': False, 'message': 'El producto no existe.'}, status=404)

        # Verifica que la cantidad no exceda el stock
        if cantidad > producto.Stock:
            return JsonResponse({'success': False, 'message': 'Cantidad excede el stock disponible.'}, status=400)

        # Agregar al carrito o actualizar cantidad si ya existe
        carrito_item, created = Carrito.objects.get_or_create(
            IdUsuario=request.user,
            IdProducto=producto,
            defaults={'Cantidad': cantidad}
        )
        if not created:
            # Si el producto ya está en el carrito, incrementa la cantidad
            nueva_cantidad = carrito_item.Cantidad + cantidad
            if nueva_cantidad > producto.Stock:
                nueva_cantidad = producto.Stock  # No puede exceder el stock
            carrito_item.Cantidad = nueva_cantidad
            carrito_item.save()

            return JsonResponse({
                'success': True,
                'message': f'Cantidad actualizada: {nueva_cantidad} unidades en el carrito.',
                'nueva_cantidad': nueva_cantidad
            })

        return JsonResponse({'success': True, 'message': 'Producto añadido al carrito.'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@login_required
def carrito_view(request):
    usuario = request.user
    
    # Obtener los productos en el carrito del usuario junto con su imagen principal
    carrito_items = Carrito.objects.filter(IdUsuario=usuario).select_related('IdProducto')

    # Calcular subtotal, descuento y total
    subtotal = sum(item.IdProducto.Precio * item.Cantidad for item in carrito_items)
    total = sum(item.IdProducto.PrecioDescuento * item.Cantidad for item in carrito_items)
    descuento_total = subtotal - total

    # Obtener la imagen en base64
    for item in carrito_items:
        imagen_principal = item.IdProducto.imagenes.filter(EsPrincipal=True).first()
        if not imagen_principal:
            imagen_principal = item.IdProducto.imagenes.order_by('-FechaAgregado').first()

        if imagen_principal and imagen_principal.Imagen:
            item.imagen_base64 = base64.b64encode(imagen_principal.Imagen).decode("utf-8")
        else:
            item.imagen_base64 = None

    # Obtener las direcciones del usuario
    direcciones = DireccionesUsuario.objects.filter(IdUsuario=usuario).select_related('IdDirecciones')

    return render(request, 'Blyss/Producto/Carrito.html', {
        'carrito_items': carrito_items,
        'subtotal': subtotal,
        'descuento_total': descuento_total,
        'total': total,
        'direcciones': direcciones  # Se envían las direcciones a la plantilla
    })

@login_required
def eliminar_del_carrito(request, producto_id):
    usuario = request.user

    # Buscar el producto en el carrito del usuario
    carrito_item = get_object_or_404(Carrito, IdUsuario=usuario, IdProducto=producto_id)
    
    # Eliminar el producto del carrito
    carrito_item.delete()
    
    return JsonResponse({'success': True, 'message': 'Producto eliminado del carrito'})

@login_required
def obtener_total_carrito(request):
    if request.user.is_authenticated:
        total_items = Carrito.objects.filter(IdUsuario=request.user).aggregate(total_items=Sum('Cantidad'))['total_items'] or 0
    else:
        total_items = 0

    return JsonResponse({'total_items': total_items})

@login_required
def favoritos_view(request):
    favoritos = Favoritos.objects.filter(IdUsuario=request.user).select_related('IdProducto')
    productos_favoritos = {favorito.IdProducto.IdProducto for favorito in favoritos}  # Conjunto con los IDs de productos favoritos

    productos = Productos.objects.all()  # Obtener todos los productos para mostrarlos en la vista

    return render(request, 'Blyss/Favoritos/index.html', {
        'favoritos': favoritos,
        'productos': productos,
        'productos_favoritos': productos_favoritos
    })

def search_view(request):
    query = request.GET.get('q', '')  
    order = request.GET.get('order', 'asc')  
    offset = int(request.GET.get('offset', 0))  
    limit = 15  
    min_price = request.GET.get('min_price')  
    max_price = request.GET.get('max_price')  
    min_rating = request.GET.get('min_rating')  
    on_sale = request.GET.get('on_sale') == "true"  

    productos = []
    categorias_relacionadas = []
    subcategorias_relacionadas = []

    # 🔹 Filtros por query
    if query.lower() == "all":
        productos = list(Productos.objects.filter(Estado=True))

    elif query.lower() == "all500":
        productos = list(Productos.objects.filter(Estado=True, Precio__lte=500))

    elif query.lower() == "all_5stars":
        productos = list(Productos.objects.filter(Estado=True, CalificacionPromedio__gte=4.5))

    elif query.lower() == "all_on_sale":
        productos = list(Productos.objects.filter(Estado=True, PrecioDescuento__gt=0))

    elif query:
        productos = list(Productos.objects.filter(Nombre__icontains=query, Estado=True))

        categorias = Categorias.objects.filter(Nombre__icontains=query)
        subcategorias = Subcategorias.objects.filter(Nombre__icontains=query)

        productos_por_categoria = list(Productos.objects.filter(
            categorias_productos__IdCategoria__in=categorias, Estado=True
        ))

        productos_por_subcategoria = list(Productos.objects.filter(
            subcategorias_productos__IdSubcategoria__in=subcategorias, Estado=True
        ))

        productos = list(set(productos + productos_por_categoria + productos_por_subcategoria))

        categorias_relacionadas = Categorias.objects.filter(
            IdCategoria__in=CategoriasProductos.objects.filter(IdProducto__in=[p.IdProducto for p in productos]).values_list('IdCategoria', flat=True)
        )

        subcategorias_relacionadas = Subcategorias.objects.filter(
            IdSubCategoria__in=SubcategoriasProductos.objects.filter(IdProducto__in=[p.IdProducto for p in productos]).values_list('IdSubcategoria', flat=True)
        )

    # 🔹 Definir precio final y aplicar filtro de productos en oferta
    for producto in productos:
        producto.precio_final = producto.PrecioDescuento if producto.PrecioDescuento and producto.PrecioDescuento > 0 else producto.Precio

    if on_sale and query.lower() != "all_on_sale":
        productos = [p for p in productos if p.PrecioDescuento and p.PrecioDescuento > 0]

    if query.lower() not in ["all500", "all_5stars", "all_on_sale"]:
        if min_price:
            productos = [p for p in productos if p.precio_final >= float(min_price)]
        if max_price:
            productos = [p for p in productos if p.precio_final <= float(max_price)]

    if min_rating and query.lower() != "all_5stars":
        productos = [p for p in productos if p.CalificacionPromedio >= float(min_rating)]

    # 🔹 Ordenación en Python en lugar de `.order_by('precio_final')`
    productos.sort(key=lambda p: p.precio_final, reverse=(order == 'desc'))

    # 🔹 Aplicar paginación
    productos_paginados = productos[offset:offset + limit]
    hay_mas = len(productos) > offset + limit  

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        productos_data = []
        for p in productos_paginados:
            imagen = None
            if p.imagenes.exists():
                primera_imagen = p.imagenes.first().Imagen
                imagen_base64 = base64.b64encode(primera_imagen).decode('utf-8')
                imagen = f"data:image/png;base64,{imagen_base64}"

            productos_data.append({
                "id": p.IdProducto,
                "nombre": p.Nombre,
                "marca": p.Marca,
                "precio": float(p.precio_final),
                "precio_original": float(p.Precio),
                "precio_descuento": float(p.PrecioDescuento) if p.PrecioDescuento and p.PrecioDescuento > 0 else None,
                "porcentaje_descuento": round(100 - (float(p.PrecioDescuento) / float(p.Precio) * 100)) if p.PrecioDescuento and p.PrecioDescuento > 0 else None,
                "calificacion": p.CalificacionPromedio,
                "imagen": imagen
            })

        return JsonResponse({"productos": productos_data, "hay_mas": hay_mas})

    return render(request, 'Blyss/Search/index.html', {
        'productos': productos_paginados,
        'query': query,
        'order': order,
        'categorias_relacionadas': categorias_relacionadas,
        'subcategorias_relacionadas': subcategorias_relacionadas
    })

def categoria_view(request):
    categorias = Categorias.objects.filter(Estado=True)  # Solo categorías activas
    return render(request, 'Blyss/Categoria/index.html', {'categorias': categorias})

def detcategoria_view(request, id):
    categoria = get_object_or_404(Categorias, IdCategoria=id)
    banners = BannerCategorias.objects.filter(IdCategoria=categoria, Estado=True).order_by('Orden')

    productos = Productos.objects.filter(categorias_productos__IdCategoria=categoria, Estado=True).distinct()

    # Carruseles categorizados
    carruseles = {
        "🌟 Mejor Valorados": productos.order_by('-CalificacionPromedio')[:10],
        "🔥 Más Vistos": productos.order_by('-Vistas')[:10],
        "🆕 Más Recientes": productos.order_by('-FechaAgregado')[:10],
        "💰 En Oferta": productos.filter(PrecioDescuento__isnull=False).order_by('-PrecioDescuento')[:10],
        "📉 Precio Más Bajo": productos.order_by('Precio')[:10],
        "🎯 Mayor Descuento": productos.filter(PrecioDescuento__isnull=False).annotate(
            porcentaje_descuento=ExpressionWrapper((1 - (F('PrecioDescuento') / F('Precio'))) * 100, output_field=FloatField())
        ).order_by('-porcentaje_descuento')[:10]
    }

    return render(request, 'Blyss/Categoria/detCategoria.html', {
        'categoria': categoria,
        'banners': banners,
        'carruseles': carruseles
    })

@login_required
def marketing_view(request):
    return render(request, 'Blyss/Admin/Marketing/index.html')

@login_required
def banners_view(request):
    # Obtener todos los banners activos
    banners = BannerHome.objects.filter(Estado=True).order_by('-FechaAgregado')

    return render(request, 'Blyss/Admin/Marketing/Banners/index.html', {
        'banners': banners
    })

def addbanner_view(request):
    return render(request, 'Blyss/Admin/Marketing/Banners/addBanner.html')

@csrf_exempt
def agregar_banner(request):
    if request.method == "POST" and request.FILES.get("image"):
        try:
            # Obtener usuario autenticado o el primer usuario registrado
            usuario_actual = request.user if request.user.is_authenticated else Usuarios.objects.first()

            # Leer el archivo y almacenarlo en binario
            imagen_binaria = request.FILES["image"].read()

            # Obtener la URL ingresada en el formulario
            banner_url = request.POST.get("bannerUrl", "").strip()

            # Verificar si hay algún banner principal registrado
            existe_principal = BannerHome.objects.filter(EsPrincipal=True).exists()

            # Obtener la selección del usuario en el formulario
            es_principal = request.POST.get("isPrincipal", "false") == "true"

            # Si el usuario NO seleccionó "Principal" pero NO hay ningún banner principal, lo asignamos como principal automáticamente
            if not existe_principal:
                es_principal = True

            # Si el nuevo banner es principal, desactivar el anterior principal (si existe)
            if es_principal:
                BannerHome.objects.filter(EsPrincipal=True).update(EsPrincipal=False)

            # Crear nuevo banner con URL
            nuevo_banner = BannerHome.objects.create(
                Img=imagen_binaria,
                Url=banner_url if banner_url else None,  # Guardar la URL si fue proporcionada
                Estado=True,
                EsPrincipal=es_principal,  # Se asigna según la lógica anterior
                FechaAgregado=timezone.now(),
                IdUsuario=usuario_actual
            )

            return JsonResponse({
                "success": True,
                "message": "Banner agregado correctamente.",
                "banner_id": nuevo_banner.IdBannerHome
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": f"Error al agregar el banner: {str(e)}"})

    return JsonResponse({"success": False, "error": "No se recibió ninguna imagen."})


@csrf_exempt
def eliminar_banner(request, banner_id):
    if request.method == "DELETE":
        try:
            banner = BannerHome.objects.get(IdBannerHome=banner_id)
            es_principal = banner.EsPrincipal  # Verificar si es el principal antes de eliminarlo

            banner.delete()

            # Si el banner eliminado era el principal, asignar el más antiguo como nuevo principal
            if es_principal:
                banner_mas_antiguo = BannerHome.objects.order_by("FechaAgregado").first()
                if banner_mas_antiguo:
                    banner_mas_antiguo.EsPrincipal = True
                    banner_mas_antiguo.save()

            return JsonResponse({"success": True, "message": "Banner eliminado correctamente."})

        except BannerHome.DoesNotExist:
            return JsonResponse({"success": False, "message": "El banner no existe."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"})
    
    return JsonResponse({"success": False, "message": "Método no permitido."})

@csrf_exempt
def hacer_principal_banner(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            banner_id = data.get("banner_id")

            # Desactivar todos los banners principales
            BannerHome.objects.filter(EsPrincipal=True).update(EsPrincipal=False)

            # Activar el nuevo banner principal
            BannerHome.objects.filter(IdBannerHome=banner_id).update(EsPrincipal=True)

            return JsonResponse({"success": True, "message": "El banner ha sido actualizado como principal."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})

@login_required
def secciones_view(request):
    banners_items = BannersItems.objects.all().order_by('-FechaAgregada')
    return render(request, 'Blyss/Admin/Marketing/Secciones/index.html', {'banners_items': banners_items})

@csrf_exempt
def eliminar_seccion(request, section_id):
    if request.method == "DELETE":
        try:
            BannersItems.objects.get(IdBannersItems=section_id).delete()
            return JsonResponse({"success": True, "message": "Sección eliminada correctamente."})
        except BannersItems.DoesNotExist:
            return JsonResponse({"success": False, "error": "Sección no encontrada."})

    return JsonResponse({"success": False, "error": "Método no permitido."})

@login_required
def addseccion_view(request):
    productos = Productos.objects.filter(Estado=True)  # Filtrar solo los productos activos
    return render(request, 'Blyss/Admin/Marketing/Secciones/addSeccion.html', {'productos': productos})

@csrf_exempt
@login_required
def agregar_seccion(request):
    if request.method == "POST":
        try:
            titulo = request.POST.get("titulo")
            producto1_id = request.POST.get("producto1")
            producto2_id = request.POST.get("producto2")
            producto3_id = request.POST.get("producto3")
            producto4_id = request.POST.get("producto4")
            imagen = request.FILES.get("imagen")

            # Validación de campos obligatorios
            if not titulo or not producto1_id or not producto2_id or not producto3_id or not producto4_id or not imagen:
                return JsonResponse({"success": False, "error": "Todos los campos son obligatorios."})

            # Obtener usuario actual
            usuario_actual = request.user

            # Guardar en base de datos
            nueva_seccion = BannersItems.objects.create(
                Titulo=titulo,
                Producto1_id=producto1_id,
                Producto2_id=producto2_id,
                Producto3_id=producto3_id,
                Producto4_id=producto4_id,
                Imagen=imagen.read(),  # Almacenar la imagen como binario
                FechaAgregada=timezone.now(),
                IdUsuario=usuario_actual
            )

            return JsonResponse({
                "success": True,
                "message": "Sección agregada correctamente.",
                "seccion_id": nueva_seccion.IdBannersItems
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": f"Error al agregar la sección: {str(e)}"})

    return JsonResponse({"success": False, "error": "Método no permitido."})

@login_required
def detalle_seccion_view(request, id_seccion):
    # Filtrar solo los productos activos
    productos = Productos.objects.filter(Estado=True)
    
    # Obtener el objeto o mostrar error 404 si no existe
    seccion = get_object_or_404(BannersItems, IdBannersItems=id_seccion)
    
    # Crear el contexto con ambos objetos
    context = {
        "seccion": seccion,
        "productos": productos,
    }
    
    return render(request, 'Blyss/Admin/Marketing/Secciones/detSeccion.html', context)

@csrf_exempt
def actualizar_seccion(request, id_seccion):
    if request.method == "POST":
        try:
            # Comprobar si la solicitud tiene una imagen
            if request.FILES.get("imagen"):
                imagen_archivo = request.FILES["imagen"].read()
            else:
                imagen_archivo = None

            # Obtener la sección a actualizar
            seccion = get_object_or_404(BannersItems, IdBannersItems=id_seccion)

            # Obtener los datos del request (excepto archivos)
            titulo = request.POST.get("titulo")
            producto1_id = request.POST.get("producto1")
            producto2_id = request.POST.get("producto2")
            producto3_id = request.POST.get("producto3")
            producto4_id = request.POST.get("producto4")

            # Validar que los productos existan en la BD
            producto1 = get_object_or_404(Productos, IdProducto=producto1_id)
            producto2 = get_object_or_404(Productos, IdProducto=producto2_id)
            producto3 = get_object_or_404(Productos, IdProducto=producto3_id)
            producto4 = get_object_or_404(Productos, IdProducto=producto4_id)

            # Actualizar los datos de la sección
            seccion.Titulo = titulo
            seccion.Producto1 = producto1
            seccion.Producto2 = producto2
            seccion.Producto3 = producto3
            seccion.Producto4 = producto4

            # Si se subió una nueva imagen, actualizarla
            if imagen_archivo:
                seccion.Imagen = imagen_archivo

            seccion.save()

            return JsonResponse({"success": True, "message": "Sección actualizada correctamente"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})

@login_required
def directorio_view(request):
    return render(request, 'Blyss/Directorio/index.html')

@login_required
def obtener_direcciones_usuario(request):
    usuario = request.user
    direcciones = DireccionesUsuario.objects.filter(IdUsuario=usuario).select_related('IdDirecciones')

    direcciones_data = [
        {
            "id": direccion.IdDirecciones.IdDirecciones,
            "estado": direccion.IdDirecciones.Estado,
            "cp": direccion.IdDirecciones.CP,
            "municipio": direccion.IdDirecciones.Municipio,
            "ciudad": direccion.IdDirecciones.Ciudad,
            "colonia": direccion.IdDirecciones.Colonia,
            "calle": direccion.IdDirecciones.Calle,
            "numero_exterior": direccion.IdDirecciones.Numero_Exterior,
            "numero_interior": direccion.IdDirecciones.Numero_Interior or "",
            "referencias": direccion.IdDirecciones.Referencias or ""
        }
        for direccion in direcciones
    ]

    return JsonResponse({"direcciones": direcciones_data})

@login_required
@csrf_exempt  # Permite recibir peticiones POST sin CSRF Token (solo para pruebas, en producción usa CSRF)
def agregar_direccion(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            usuario = request.user  # Usuario autenticado

            # Crear la dirección
            nueva_direccion = Direcciones.objects.create(
                Estado=data["estado"],
                CP=data["cp"],
                Municipio=data["municipio"],
                Ciudad=data["ciudad"],
                Colonia=data["colonia"],
                Calle=data["calle"],
                Numero_Exterior=data["numero_exterior"],
                Numero_Interior=data.get("numero_interior", ""),
                Referencias=data.get("referencias", "")
            )

            # Relacionar la dirección con el usuario
            DireccionesUsuario.objects.create(IdDirecciones=nueva_direccion, IdUsuario=usuario)

            return JsonResponse({"success": True, "message": "Dirección agregada correctamente"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)

@login_required
@csrf_exempt  # Solo para pruebas, en producción usa CSRF Token
def actualizar_direccion(request, id_direccion):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            direccion = Direcciones.objects.get(IdDirecciones=id_direccion)
            direccion.Estado = data["estado"]
            direccion.CP = data["cp"]
            direccion.Municipio = data["municipio"]
            direccion.Ciudad = data["ciudad"]
            direccion.Colonia = data["colonia"]
            direccion.Calle = data["calle"]
            direccion.Numero_Exterior = data["numero_exterior"]
            direccion.Numero_Interior = data.get("numero_interior", "")
            direccion.Referencias = data.get("referencias", "")
            direccion.save()

            return JsonResponse({"success": True, "message": "Dirección actualizada correctamente"})

        except Direcciones.DoesNotExist:
            return JsonResponse({"success": False, "message": "Dirección no encontrada"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)

@login_required
def editar_direccion(request, id_direccion):
    direccion = get_object_or_404(Direcciones, pk=id_direccion)
    
    # Si la petición es AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            "id": direccion.IdDirecciones,
            "estado": direccion.Estado,
            "cp": direccion.CP,
            "municipio": direccion.Municipio,
            "ciudad": direccion.Ciudad,
            "colonia": direccion.Colonia,
            "calle": direccion.Calle,
            "numero_exterior": direccion.Numero_Exterior,
            "numero_interior": direccion.Numero_Interior or "",
            "referencias": direccion.Referencias or ""
        })

    # Si es una petición normal, renderizar la plantilla con los datos
    return render(request, 'Blyss/Directorio/detDireccion.html', {"direccion": direccion})

@csrf_exempt
@login_required
def actualizar_direccion(request, id_direccion):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            direccion = get_object_or_404(Direcciones, pk=id_direccion)

            # Actualizar los campos
            direccion.Estado = data["estado"]
            direccion.CP = data["cp"]
            direccion.Municipio = data["municipio"]
            direccion.Ciudad = data["ciudad"]
            direccion.Colonia = data["colonia"]
            direccion.Calle = data["calle"]
            direccion.Numero_Exterior = data["numero_exterior"]
            direccion.Numero_Interior = data.get("numero_interior", "")
            direccion.Referencias = data.get("referencias", "")

            direccion.save()

            return JsonResponse({"success": True, "message": "Dirección actualizada correctamente"})
        
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)

@csrf_exempt
@login_required
def eliminar_direccion(request, id_direccion):
    if request.method == "DELETE":
        try:
            direccion = get_object_or_404(Direcciones, pk=id_direccion)
            direccion.delete()

            return JsonResponse({"success": True, "message": "Dirección eliminada correctamente"})
        
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)

@login_required
@csrf_exempt  # Solo para pruebas. En producción, usa el CSRF token en el fetch
def procesar_compra(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Convertir el JSON recibido
            usuario = request.user
            metodo_pago = data.get("metodo_pago")

            carrito_items = Carrito.objects.filter(IdUsuario=usuario)

            if not carrito_items.exists():
                return JsonResponse({"success": False, "message": "El carrito está vacío"}, status=400)

            # Crear el pedido
            nuevo_pedido = Pedido.objects.create(
                IdUsuario=usuario,
                Estado="En camino",
                FechaPedido=now(),
                Total=sum(item.IdProducto.PrecioDescuento * item.Cantidad for item in carrito_items)
            )

            # Guardar detalles del pedido
            for item in carrito_items:
                DetallePedido.objects.create(
                    IdPedido=nuevo_pedido,
                    IdProducto=item.IdProducto,
                    Cantidad=item.Cantidad,
                    PrecioUnitario=item.IdProducto.PrecioDescuento,
                    Subtotal=item.IdProducto.PrecioDescuento * item.Cantidad
                )

                # Reducir stock
                producto = item.IdProducto
                producto.Stock -= item.Cantidad
                producto.save()

            # Registrar el pago
            Pago.objects.create(
                IdPedido=nuevo_pedido,
                Metodo=metodo_pago,
                FechaPago=now(),
                Monto=nuevo_pedido.Total,
                TransaccionId=str(uuid.uuid4())  # ID único de transacción
            )

            # Vaciar el carrito
            carrito_items.delete()

            return JsonResponse({"success": True, "message": "Compra realizada con éxito", "pedido_id": nuevo_pedido.IdPedido})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Error al decodificar JSON"}, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error interno: {str(e)}"}, status=500)

    return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)

@login_required
def pedidos_view(request):
    pedidos = Pedido.objects.filter(IdUsuario=request.user).order_by('-FechaPedido').prefetch_related(
        Prefetch('detalles', queryset=DetallePedido.objects.select_related('IdProducto'))
    )

    for pedido in pedidos:
        for detalle in pedido.detalles.all():
            if detalle.IdProducto:
                imagen_principal = detalle.IdProducto.imagenes.filter(EsPrincipal=True).first()

                if not imagen_principal:
                    imagen_principal = detalle.IdProducto.imagenes.order_by('FechaAgregado').first()

                detalle.imagen_base64 = (
                    base64.b64encode(imagen_principal.Imagen).decode("utf-8")
                    if imagen_principal and imagen_principal.Imagen else None
                )

    return render(request, 'Blyss/Pedidos/index.html', {'pedidos': pedidos})

@login_required
def usuarios_view(request):
    return render(request, 'Blyss/Admin/Usuarios/index.html')

@login_required
def lista_usuarios_view(request):
    return render(request, 'Blyss/Admin/Usuarios/ListaUsuarios/index.html')

@login_required
def usuarios_lista_ajax(request):
    page_number = request.GET.get('page', 1)  # Obtiene el número de página de la solicitud
    usuarios_list = Usuarios.objects.all().order_by('Nombre')

    paginator = Paginator(usuarios_list, 10)  # Paginación de 10 usuarios por página
    usuarios = paginator.get_page(page_number)

    data = {
        'usuarios': [
            {
                'id': usuario.IdUsuario,  # Se agrega el ID del usuario
                'nombre_completo': f"{usuario.Nombre} {usuario.Apellidos}",
                'correo': usuario.correo,
                'telefono': usuario.Telefono if usuario.Telefono else "N/A",
                'is_active': usuario.is_active
            }
            for usuario in usuarios
        ],
        'has_previous': usuarios.has_previous(),
        'has_next': usuarios.has_next(),
        'previous_page_number': usuarios.previous_page_number() if usuarios.has_previous() else None,
        'next_page_number': usuarios.next_page_number() if usuarios.has_next() else None,
        'current_page': usuarios.number,
        'total_pages': paginator.num_pages,
    }

    return JsonResponse(data)

@csrf_exempt  # Para permitir peticiones AJAX sin CSRF token
@login_required
def cambiar_estado_usuario(request):
    if request.method == "POST":
        try:
            user_id = request.POST.get("user_id")
            usuario = Usuarios.objects.get(IdUsuario=user_id)

            usuario.is_active = not usuario.is_active  # Alterna el estado
            usuario.save()

            return JsonResponse({"success": True, "is_active": usuario.is_active})
        except Usuarios.DoesNotExist:
            return JsonResponse({"success": False, "error": "Usuario no encontrado"})
    
    return JsonResponse({"success": False, "error": "Método no permitido"})

@login_required
def usuario_detalle_view(request, usuario_id):
    usuario = get_object_or_404(Usuarios, IdUsuario=usuario_id)  # Obtiene el usuario o muestra error 404
    return render(request, 'Blyss/Admin/Usuarios/ListaUsuarios/detUsuarios.html', {'usuario': usuario})

@csrf_exempt
@login_required
def actualizar_usuario(request):
    if request.method == "POST":
        try:
            user_id = request.POST.get("user_id")
            
            if not user_id:
                return JsonResponse({"success": False, "error": "ID de usuario no proporcionado"})

            usuario = Usuarios.objects.get(IdUsuario=user_id)

            # Lista de campos permitidos para edición
            campos_permitidos = ["Telefono", "Pais", "FechaDeNacimiento", "Genero", "is_active"]

            for campo in campos_permitidos:
                if campo in request.POST:
                    valor = request.POST[campo]
                    if campo == "is_active":
                        valor = valor.lower() == "true"
                    setattr(usuario, campo, valor)

            usuario.save()
            return JsonResponse({"success": True})

        except Usuarios.DoesNotExist:
            return JsonResponse({"success": False, "error": "Usuario no encontrado"})

    return JsonResponse({"success": False, "error": "Método no permitido"})

@login_required
def roles_view(request):
    return render(request, 'Blyss/Admin/Usuarios/Roles/index.html')

@login_required
def obtener_usuarios_staff(request):
    usuarios = Usuarios.objects.filter(is_staff=True).values('IdUsuario', 'Nombre', 'Apellidos', 'correo', 'Telefono', 'last_login')

    usuarios_lista = []
    for usuario in usuarios:
        roles = UsuarioRol.objects.filter(Usuario_id=usuario['IdUsuario']).select_related('Rol')
        permisos = UsuarioPermiso.objects.filter(Usuario_id=usuario['IdUsuario']).select_related('Permiso')

        roles_lista = [rol.Rol.Descripcion for rol in roles]
        permisos_lista = [permiso.Permiso.Descripcion for permiso in permisos]

        # Convertir last_login a la hora local
        last_login = localtime(usuario['last_login']).strftime("%Y-%m-%d %H:%M") if usuario['last_login'] else "Nunca"

        usuarios_lista.append({
            'id': usuario['IdUsuario'],  # ID del usuario para la tabla
            'nombre_completo': f"{usuario['Nombre']} {usuario['Apellidos']}",
            'correo': usuario['correo'],
            'telefono': usuario['Telefono'] or "N/A",
            'roles_permisos': ", ".join(roles_lista + permisos_lista) if roles_lista or permisos_lista else "Sin asignar",
            'last_login': last_login  # Último inicio de sesión
        })

    return JsonResponse({'data': usuarios_lista})


@login_required
def usuario_roldet_view(request, usuario_id):
    usuario = get_object_or_404(Usuarios, IdUsuario=usuario_id)
    roles = Roles.objects.all()
    rol_asignado = usuario.roles_asignados.first()  # Obtiene el primer rol asignado (si existe)

    return render(request, 'Blyss/Admin/Usuarios/Roles/detUsuarioRol.html', {
        'usuario': usuario,
        'roles': roles,
        'rol_asignado': rol_asignado  # Pasamos el rol asignado correctamente
    })

@login_required
def actualizar_usuario_rol(request):
    if request.method == "POST":
        usuario_id = request.POST.get("usuario_id")
        rol_id = request.POST.get("rol_id")

        if not usuario_id:
            return JsonResponse({"success": False, "message": "ID de usuario no recibido."}, status=400)

        try:
            usuario = get_object_or_404(Usuarios, IdUsuario=int(usuario_id))

            # Eliminar roles anteriores
            UsuarioRol.objects.filter(Usuario=usuario).delete()

            if rol_id:  # Si se seleccionó un nuevo rol
                rol = get_object_or_404(Roles, IdRol=int(rol_id))
                UsuarioRol.objects.create(Usuario=usuario, Rol=rol, AsignadoPor=request.user)

            return JsonResponse({"success": True, "message": "Rol actualizado correctamente."})

        except ValueError:
            return JsonResponse({"success": False, "message": "ID de usuario o rol no válido."}, status=400)

    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)

@login_required
def obtener_permisos_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuarios, IdUsuario=usuario_id)
    permisos = UsuarioPermiso.objects.filter(Usuario=usuario).select_related("Permiso")

    data = [
        {
            "id": permiso.Permiso.IdPermiso,
            "descripcion": permiso.Permiso.Descripcion,
            "fecha": localtime(permiso.FechaAsignado).strftime("%Y-%m-%d %H:%M")
        }
        for permiso in permisos
    ]

    return JsonResponse({"success": True, "permisos": data})


@login_required
def obtener_permisos_disponibles(request, usuario_id):
    usuario = get_object_or_404(Usuarios, IdUsuario=usuario_id)
    permisos_asignados = UsuarioPermiso.objects.filter(Usuario=usuario).values_list('Permiso__IdPermiso', flat=True)
    
    permisos_disponibles = Permisos.objects.exclude(IdPermiso__in=permisos_asignados)
    data = [{"id": permiso.IdPermiso, "descripcion": permiso.Descripcion} for permiso in permisos_disponibles]

    return JsonResponse({"success": True, "permisos": data})

@login_required
def asignar_permiso_usuario(request):
    if request.method == "POST":
        usuario_id = request.POST.get("usuario_id")
        permiso_id = request.POST.get("permiso_id")

        usuario = get_object_or_404(Usuarios, IdUsuario=usuario_id)
        permiso = get_object_or_404(Permisos, IdPermiso=permiso_id)

        # Verificar que el usuario no tenga ya el permiso
        if not UsuarioPermiso.objects.filter(Usuario=usuario, Permiso=permiso).exists():
            UsuarioPermiso.objects.create(Usuario=usuario, Permiso=permiso, AsignadoPor=request.user)
            return JsonResponse({"success": True, "message": "Permiso asignado correctamente."})
        else:
            return JsonResponse({"success": False, "message": "El usuario ya tiene este permiso."}, status=400)

    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)

@login_required
def quitar_permiso_usuario(request):
    if request.method == "POST":
        usuario_id = request.POST.get("usuario_id")
        permiso_id = request.POST.get("permiso_id")

        usuario = get_object_or_404(Usuarios, IdUsuario=usuario_id)
        permiso = get_object_or_404(Permisos, IdPermiso=permiso_id)

        usuario_permiso = UsuarioPermiso.objects.filter(Usuario=usuario, Permiso=permiso)
        if usuario_permiso.exists():
            usuario_permiso.delete()
            return JsonResponse({"success": True, "message": "Permiso eliminado correctamente."})
        else:
            return JsonResponse({"success": False, "message": "El usuario no tiene este permiso."}, status=400)

    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)

@login_required
def auditoria_usuarios_view(request):
    return render(request, 'Blyss/Admin/Usuarios/Auditoria/index.html')