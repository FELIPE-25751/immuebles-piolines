from django.urls import path
from . import views

app_name = 'contratos'

urlpatterns = [
    path('', views.listar_contratos, name='listar'),
    path('detalle/<int:contrato_id>/', views.detalle_contrato, name='detalle'),
    path('crear/', views.crear_contrato, name='crear'),
    path('editar/<int:contrato_id>/', views.editar_contrato, name='editar'),
    path('firmar/<int:contrato_id>/', views.firmar_contrato, name='firmar'),
    path('cancelar/<int:contrato_id>/', views.cancelar_contrato, name='cancelar'),
]
