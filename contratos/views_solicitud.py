from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models_solicitud import SolicitudArriendo
from inmuebles.models import Inmueble
from notificaciones.models import Notificacion

@login_required
def solicitar_inmueble(request, inmueble_id):
    inmueble = get_object_or_404(Inmueble, id=inmueble_id, estado='disponible', activo=True)
    user = request.user
    if user.tipo_usuario != 'inquilino':
        messages.error(request, 'Solo los inquilinos pueden solicitar inmuebles.')
        return redirect('inmuebles:detalle', inmueble_id=inmueble.id)
    if request.method == 'POST':
        # Evitar solicitudes duplicadas
        existe = SolicitudArriendo.objects.filter(inmueble=inmueble, inquilino=user, estado='pendiente').exists()
        if existe:
            messages.warning(request, 'Ya has solicitado este inmueble y está pendiente de respuesta.')
        else:
            solicitud = SolicitudArriendo.objects.create(
                inmueble=inmueble,
                inquilino=user,
                propietario=inmueble.propietario,
                mensaje='',
                estado='pendiente',
                fecha_solicitud=timezone.now()
            )
            # Notificar al propietario
            Notificacion.objects.create(
                usuario=inmueble.propietario,
                titulo='Nueva solicitud de arriendo',
                mensaje=f'{user.get_full_name()} ha solicitado arrendar tu inmueble "{inmueble.titulo}".',
                tipo='solicitud',
                enlace=f'/solicitudes/'
            )
            messages.success(request, 'Solicitud enviada correctamente. El propietario será notificado.')
        return redirect('inmuebles:detalle', inmueble_id=inmueble.id)
    return redirect('inmuebles:detalle', inmueble_id=inmueble.id)
