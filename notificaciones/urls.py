from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.listar_notificaciones, name='listar'),
    path('leer/<int:notificacion_id>/', views.marcar_como_leida, name='marcar_leida'),
    path('leer-todas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    path('eliminar/<int:notificacion_id>/', views.eliminar_notificacion, name='eliminar'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('api/no-leidas/', views.obtener_no_leidas, name='api_no_leidas'),
]
