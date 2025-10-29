from django.urls import path
from . import views

app_name = 'inmuebles'

urlpatterns = [
    path('', views.listar_inmuebles, name='listar'),
    path('detalle/<int:inmueble_id>/', views.detalle_inmueble, name='detalle'),
    path('mis-inmuebles/', views.mis_inmuebles, name='mis_inmuebles'),
    path('crear/', views.crear_inmueble, name='crear'),
    path('editar/<int:inmueble_id>/', views.editar_inmueble, name='editar'),
    path('eliminar/<int:inmueble_id>/', views.eliminar_inmueble, name='eliminar'),
    path('imagenes/<int:inmueble_id>/', views.agregar_imagenes, name='agregar_imagenes'),
    path('imagen/eliminar/<int:imagen_id>/', views.eliminar_imagen, name='eliminar_imagen'),
]
