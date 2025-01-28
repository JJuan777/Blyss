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
from django.core.paginator import Paginator

@login_required
def index(request):
    # Consulta los productos activos
    productos = Productos.objects.filter(Estado=True).order_by('Nombre')  # Solo productos con Estado=True
    return render(request, 'Blyss/index.html', {
        'mensaje': '¡Bienvenido a Blyss!',
        'productos': productos
    })

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
    return render(request, 'Blyss/Admin/Inventario/index.html')

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

    productos_data = [
        {
            'IdProducto': producto.IdProducto,
            'nombre': producto.Nombre,
            'sku': producto.SKU,
            'stock': producto.Stock,
            'precio': producto.Precio,
            'marca': producto.Marca,
            'estado': 'Activo' if producto.Estado else 'Inactivo',
        }
        for producto in productos_page
    ]

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

            # Verificar el límite de 10 imágenes
            if ImagenesProducto.objects.filter(IdProducto=producto).count() >= 10:
                return JsonResponse({"success": False, "message": "No puedes cargar más de 10 imágenes para este producto."})

            # Verificar si ya existe una imagen principal
            if request.POST.get("es_principal") == "true" and ImagenesProducto.objects.filter(IdProducto=producto, EsPrincipal=True).exists():
                return JsonResponse({"success": False, "message": "El producto ya tiene una imagen principal."})

            # Procesar la imagen cargada
            imagen = request.FILES.get("imagen")
            if not imagen:
                return JsonResponse({"success": False, "message": "Debes seleccionar una imagen."})

            # Guardar la imagen en la base de datos
            ImagenesProducto.objects.create(
                IdProducto=producto,
                Imagen=imagen.read(),
                EsPrincipal=request.POST.get("es_principal") == "true",
            )

            return JsonResponse({"success": True, "message": "Imagen cargada correctamente."})
        except ValidationError as e:
            return JsonResponse({"success": False, "message": str(e)})
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

@login_required
@csrf_exempt
def addcategoria_view(request):
    if request.method == 'POST':
        try:
            # Decodifica el cuerpo de la solicitud JSON
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

            # Crear la categoría
            categoria = Categorias.objects.create(
                Nombre=nombre,
                Descripcion=descripcion,
                Estado=estado,
            )

            return JsonResponse({'success': True, 'message': 'Categoría creada exitosamente.', 'categoria_id': categoria.IdCategoria})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al crear la categoría: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@login_required
def detcategoria_view(request, id):
    # Obtener la categoría o devolver un error 404 si no existe
    categoria = get_object_or_404(Categorias, IdCategoria=id)

    return render(request, 'Blyss/Admin/Inventario/Categorias/detCategorias.html', {
        'categoria': categoria
    })

@login_required
@csrf_exempt
def updatecategoria_view(request, id):
    if request.method == 'POST':
        try:
            # Obtener la categoría
            categoria = Categorias.objects.get(IdCategoria=id)

            # Obtener datos enviados
            data = json.loads(request.body)
            nombre = data.get('nombre', '').strip()
            descripcion = data.get('descripcion', '').strip()
            estado = data.get('estado', 'True') == 'True'  # Convertir a booleano

            # Validar y actualizar
            if not nombre:
                return JsonResponse({'success': False, 'message': 'El nombre es obligatorio.'})
            if len(nombre) > 100:
                return JsonResponse({'success': False, 'message': 'El nombre no puede exceder los 100 caracteres.'})
            if len(descripcion) > 200:
                return JsonResponse({'success': False, 'message': 'La descripción no puede exceder los 200 caracteres.'})

            categoria.Nombre = nombre
            categoria.Descripcion = descripcion
            categoria.Estado = estado
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
    tiene_carrito = Carrito.objects.filter(IdUsuario=request.user).exists()

    # Verifica si el producto actual está en los favoritos del usuario
    usuario = request.user
    en_favoritos = usuario.favoritos.filter(IdProducto=producto).exists()

    return render(request, 'Blyss/Producto/index.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
        'en_favoritos': en_favoritos,  # Agrega esta variable al contexto
        'tiene_carrito': tiene_carrito,  # Enviar al template
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