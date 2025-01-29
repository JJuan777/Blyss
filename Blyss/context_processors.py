from django.db.models import Sum  # Importa correctamente Sum
from .models import Carrito

def carrito_context(request):
    if request.user.is_authenticated:
        total_items = Carrito.objects.filter(IdUsuario=request.user).aggregate(total_items=Sum('Cantidad'))['total_items'] or 0
    else:
        total_items = 0  # Si el usuario no está autenticado, no tiene carrito

    return {
        'total_items_carrito': total_items
    }
