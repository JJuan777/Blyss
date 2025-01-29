from django.urls import path
from . import views

urlpatterns = [
    # Agrega las rutas que desees para la app
    path('', views.index, name='index'),  # Ruta principal de la app
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/', views.admin_view, name='admin'),
    #Inevntario
    path('Admin/inventario/', views.inventario_view, name='inventario'),
        #Productos
            #Admin
    path('Admin/inventario/productos', views.productos_view, name='productos'),
    path('Admin/inventario/productos/add', views.addproductos_view, name='add_productos'),
    path("admin/inventario/add-producto/", views.add_producto_view, name="add_producto"),
    path('admin/inventario/obtener-productos/', views.obtener_productos, name='obtener_productos'),
    path('admin/inventario/productos/view/<int:producto_id>/', views.detproducto_view, name='det_producto'),
    path('actualizar-producto/', views.actualizar_producto_view, name='actualizar_producto'),
    path('eliminar-producto/', views.eliminar_producto_view, name='eliminar_producto'),
    path('eliminar-imagen/<int:imagen_id>/', views.eliminar_imagen_view, name='eliminar_imagen'),
    path('cargar-imagen/<int:producto_id>/', views.cargar_imagen_view, name='cargar_imagen'),
            #General
    path('view/<int:producto_id>/', views.producto_view, name='producto'),
    path('favoritos/toggle/', views.toggle_favorites, name='toggle_favorites'),
    path('carrito/add/', views.add_to_cart, name='add_to_cart'),
            #Carrito
    path('carrito/', views.carrito_view, name='carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/total/', views.obtener_total_carrito, name='obtener_total_carrito'),
        #Categorias
    path('admin/inventario/categorias/', views.categorias_view, name='categorias'),
    path('admin/inventario/obtener-categorias/', views.obtener_categorias, name='obtener_categorias'),
    path('admin/inventario/categorias/add', views.addcategorias_view, name='add_categorias'),
    path('admin/inventario/add-categoria/', views.addcategoria_view, name='add_categoria'),
    path('admin/inventario/categorias/update/<int:id>/', views.updatecategoria_view, name='update_categoria'),
    path('admin/inventario/categorias/view/<int:id>/', views.detcategoria_view, name='det_categoria'),
    path('admin/inventario/categorias/delete/<int:id>/', views.deletecategoria_view, name='delete_categoria'),
        #Subcategorias
    path('admin/inventario/subcategorias/', views.subcategorias_view, name='subcategorias'),
    path('admin/inventario/obtener-subcategorias/', views.obtener_subcategorias, name='obtener_subcategorias'),
    path('admin/inventario/subcategorias/add', views.addsubcategorias_view, name='add_subcategorias'),
    path('admin/inventario/add-subcategoria/', views.addsubcategoria_view, name='add_subcategoria'),
    path('admin/inventario/subcategorias/view/<int:id>/', views.detsubcategoria_view, name='det_subcategoria'),
    path('admin/inventario/subcategorias/update/<int:id>/', views.updatesubcategoria_view, name='update_subcategoria'),
    path('admin/inventario/subcategorias/delete/<int:id>/', views.deletesubcategoria_view, name='delete_subcategoria'),


]
