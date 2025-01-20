from django.contrib import admin
from django.urls import path, include  # Importa `include`

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Blyss/', include('Blyss.urls')),  # Ruta para la app
]
