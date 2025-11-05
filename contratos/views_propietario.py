from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models_solicitud import SolicitudArriendo
from .models import Contrato
from inmuebles.models import Inmueble
from core.models import Usuario
from notificaciones.models import Notificacion

@login_required
def solicitudes_recibidas(request):
    if request.user.tipo_usuario != 'propietario':
        messages.error(request, 'No tienes permisos para ver solicitudes.')
        return redirect('core:dashboard')
    solicitudes = SolicitudArriendo.objects.filter(propietario=request.user).order_by('-fecha_solicitud')
    return render(request, 'contratos/solicitudes_recibidas.html', {'solicitudes': solicitudes})

@login_required
def responder_solicitud(request, solicitud_id, accion):
    solicitud = get_object_or_404(SolicitudArriendo, id=solicitud_id, propietario=request.user, estado='pendiente')
    if accion == 'aceptar':
        solicitud.estado = 'aceptada'
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()
        # Crear contrato automáticamente
        contrato = Contrato.objects.create(
            inmueble=solicitud.inmueble,
            inquilino=solicitud.inquilino,
            estado='borrador',
            fecha_inicio=timezone.now().date(),
            fecha_fin=timezone.now().date() + timezone.timedelta(days=365),
            valor_arriendo=solicitud.inmueble.precio_arriendo,
            valor_administracion=solicitud.inmueble.precio_administracion,
            valor_deposito=solicitud.inmueble.deposito_seguridad,
            dia_pago=5,
            terminos_condiciones='Términos estándar',
            clausulas_especiales='',
            activo=True
        )
        # Notificar a inquilino
        Notificacion.objects.create(
            usuario=solicitud.inquilino,
            titulo='Solicitud aceptada',
            mensaje=f'Tu solicitud para el inmueble "{solicitud.inmueble.titulo}" fue aceptada. Ya puedes firmar el contrato.',
            tipo='contrato',
            enlace=reverse('contratos:detalle', args=[contrato.id])
        )
        messages.success(request, 'Solicitud aceptada y contrato generado.')
    elif accion == 'rechazar':
        solicitud.estado = 'rechazada'
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()
        Notificacion.objects.create(
            usuario=solicitud.inquilino,
            titulo='Solicitud rechazada',
            mensaje=f'Tu solicitud para el inmueble "{solicitud.inmueble.titulo}" fue rechazada.',
            tipo='contrato',
            enlace=reverse('inmuebles:detalle', args=[solicitud.inmueble.id])
        )
        messages.info(request, 'Solicitud rechazada.')
    return redirect('contratos:solicitudes_recibidas')
