
from django.urls import path
from . import views
from . import views_solicitud
from . import views_propietario

app_name = 'contratos'

urlpatterns = [
    path('', views.listar_contratos, name='listar'),
    path('detalle/<int:contrato_id>/', views.detalle_contrato, name='detalle'),
    path('crear/', views.crear_contrato, name='crear'),
    path('editar/<int:contrato_id>/', views.editar_contrato, name='editar'),
    path('firmar/<int:contrato_id>/', views.firmar_contrato, name='firmar'),
    path('cancelar/<int:contrato_id>/', views.cancelar_contrato, name='cancelar'),
    path('vencer/<int:contrato_id>/', views.vencer_contrato, name='vencer'),
    path('solicitar/<int:inmueble_id>/', views_solicitud.solicitar_inmueble, name='solicitar_inmueble'),
    path('solicitudes/', views_propietario.solicitudes_recibidas, name='solicitudes_recibidas'),
    path('solicitud/<int:solicitud_id>/<str:accion>/', views_propietario.responder_solicitud, name='responder_solicitud'),
]
