from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('', views.listar_pagos, name='listar'),
    path('detalle/<int:pago_id>/', views.detalle_pago, name='detalle'),
    path('registrar/<int:pago_id>/', views.registrar_pago, name='registrar'),
    path('cuenta-cobro/<int:pago_id>/', views.generar_cuenta_cobro, name='cuenta_cobro'),
    path('reportes/', views.reportes_pagos, name='reportes'),
]
