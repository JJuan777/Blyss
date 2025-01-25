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
from .models import Productos, Categorias, Subcategorias, CategoriasProductos, SubcategoriasProductos
from django.core.paginator import Paginator

@login_required
def index(request):
    return render(request, 'Blyss/index.html', {'mensaje': '¡Bienvenido a Blyss!'})

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
            data = json.loads(request.body)

            # Convertir el estado recibido (1 o 0) en un booleano
            estado = data.get("estado", False)

            # Crear el producto
            producto = Productos(
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
            producto.save()

            # Registrar la categoría
            categoria_id = data.get("categoria")
            if categoria_id:
                categoria = Categorias.objects.get(IdCategoria=categoria_id)
                CategoriasProductos.objects.create(IdProducto=producto, IdCategoria=categoria)

            # Registrar la subcategoría
            subcategoria_id = data.get("subcategoria")
            if subcategoria_id:
                subcategoria = Subcategorias.objects.get(IdSubCategoria=subcategoria_id)
                SubcategoriasProductos.objects.create(IdProducto=producto, IdSubcategoria=subcategoria)

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

    context = {
        "producto": producto,
        "categoria_producto": categoria_producto.IdCategoria.IdCategoria if categoria_producto else None,
        "subcategoria_producto": subcategoria_producto.IdSubcategoria.IdSubCategoria if subcategoria_producto else None,
        "categorias": categorias,
        "subcategorias": subcategorias,
    }

    return render(request, "Blyss/Admin/Inventario/Productos/detProducto.html", context)

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