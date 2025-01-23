from django.urls import path
from . import views

urlpatterns = [
    # Agrega las rutas que desees para la app
    path('', views.index, name='index'),  # Ruta principal de la app
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
