from django.urls import path
from . import views

urlpatterns = [
    # Agrega las rutas que desees para la app
    path('', views.index, name='index'),  # Ruta principal de la app
]
