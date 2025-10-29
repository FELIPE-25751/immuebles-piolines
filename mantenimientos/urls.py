from django.urls import path
from . import views

app_name = 'mantenimientos'

urlpatterns = [
    path('', views.listar_mantenimientos, name='listar'),
    path('detalle/<int:mantenimiento_id>/', views.detalle_mantenimiento, name='detalle'),
    path('solicitar/', views.solicitar_mantenimiento, name='solicitar'),
    path('gestionar/<int:mantenimiento_id>/', views.gestionar_mantenimiento, name='gestionar'),
    path('seguimiento/<int:mantenimiento_id>/', views.agregar_seguimiento, name='seguimiento'),
    path('cancelar/<int:mantenimiento_id>/', views.cancelar_mantenimiento, name='cancelar'),
]
