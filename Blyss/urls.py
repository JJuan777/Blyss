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
    path('procesar-compra/', views.procesar_compra, name='procesar_compra'),
        #Categorias
    path('admin/inventario/categorias/', views.categorias_view, name='categorias'),
    path('admin/inventario/obtener-categorias/', views.obtener_categorias, name='obtener_categorias'),
    path('admin/inventario/categorias/add', views.addcategorias_view, name='add_categorias'),
    path('admin/inventario/add-categoria/', views.addcategoria_view, name='add_categoria'),
    path('admin/inventario/categorias/update/<int:id>/', views.updatecategoria_view, name='update_categoria'),
    path('admin/inventario/categorias/view/<int:id>/', views.detcategoria_viewad, name='det_categoria'),
    path('admin/inventario/categorias/delete/<int:id>/', views.deletecategoria_view, name='delete_categoria'),
        #Subcategorias
    path('admin/inventario/subcategorias/', views.subcategorias_view, name='subcategorias'),
    path('admin/inventario/obtener-subcategorias/', views.obtener_subcategorias, name='obtener_subcategorias'),
    path('admin/inventario/subcategorias/add', views.addsubcategorias_view, name='add_subcategorias'),
    path('admin/inventario/add-subcategoria/', views.addsubcategoria_view, name='add_subcategoria'),
    path('admin/inventario/subcategorias/view/<int:id>/', views.detsubcategoria_view, name='det_subcategoria'),
    path('admin/inventario/subcategorias/update/<int:id>/', views.updatesubcategoria_view, name='update_subcategoria'),
    path('admin/inventario/subcategorias/delete/<int:id>/', views.deletesubcategoria_view, name='delete_subcategoria'),
           #Favorites
    path('favoritos/', views.favoritos_view, name='favoritos'),
           #Search
    path('Search/', views.search_view, name='search_view'),
           #Categoria
    path('Categoria/', views.categoria_view, name='categoria_view'),
    path('Blyss/Categoria/view/<int:id>/', views.detcategoria_view, name='detcategoria_view'),
            #Marketing
    path('admin/marketing/', views.marketing_view, name='marketing_view'),
    path('admin/marketing/banners/', views.banners_view, name='banners_view'),
    path('admin/marketing/banners/add', views.addbanner_view, name='addbanner_view'),
    path('admin/marketing/banners/agregar/', views.agregar_banner, name='agregar_banner'),
    path('admin/marketing/banners/eliminar/<int:banner_id>/', views.eliminar_banner, name='eliminar_banner'),
    path('banners/hacer-principal/', views.hacer_principal_banner, name="hacer_principal_banner"),
    path('admin/marketing/secciones/', views.secciones_view, name='secciones_view'),
    path('secciones/eliminar/<int:section_id>/', views.eliminar_seccion, name="eliminar_seccion"),
    path('admin/marketing/secciones/add', views.addseccion_view, name="addseccion"),
    path('admin/marketing/secciones/agregar/', views.agregar_seccion, name="agregar_seccion"),
    path('admin/marketing/secciones/view/<int:id_seccion>/', views.detalle_seccion_view, name="detalle_seccion"),
    path('admin/marketing/secciones/update/<int:id_seccion>/', views.actualizar_seccion, name="actualizar_seccion"),
           #Directorio
    path('Directorio/', views.directorio_view, name='directorio_view'),
    path('api/direcciones/', views.obtener_direcciones_usuario, name='obtener_direcciones_usuario'),
    path('api/agregar_direccion/', views.agregar_direccion, name='agregar_direccion'),
    path('api/actualizar_direccion/<int:id_direccion>/', views.actualizar_direccion, name='actualizar_direccion'),
    path('Directorio/view/<int:id_direccion>/', views.editar_direccion, name='editar_direccion'),
    path('api/actualizar_direccion/<int:id_direccion>/', views.actualizar_direccion, name='actualizar_direccion'),
    path('api/eliminar_direccion/<int:id_direccion>/', views.eliminar_direccion, name='eliminar_direccion'),
            #Carrito
    path('pedidos/', views.pedidos_view, name='pedidos'),
        #Usuarios
    path('admin/usuarios/', views.usuarios_view, name='usuarios'),
    path('admin/usuarios/lista_usuarios', views.lista_usuarios_view, name='lista_usuarios'),
    path('usuarios/ajax/', views.usuarios_lista_ajax, name='usuarios_lista_ajax'),
    path('usuarios/cambiar_estado/', views.cambiar_estado_usuario, name='cambiar_estado_usuario'),
    path('admin/usuarios/view/<int:usuario_id>/', views.usuario_detalle_view, name='usuario_detalle'),
    path('usuarios/actualizar/', views.actualizar_usuario, name='actualizar_usuario'),
            #Roles
    path('admin/usuarios/roles/', views.roles_view, name='roles'),
            #Auditoría
    path('admin/usuarios/auditoria/', views.auditoria_usuarios_view, name='auditoria_usuarios'),
    path('api/usuarios-staff/', views.obtener_usuarios_staff, name='usuarios-staff'),

]
