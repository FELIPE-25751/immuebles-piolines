from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Inmueble, ImagenInmueble
from .forms import InmuebleForm, ImagenInmuebleForm, BusquedaInmuebleForm


def listar_inmuebles(request):
    """Vista para listar inmuebles con búsqueda y filtros"""
    inmuebles = Inmueble.objects.filter(activo=True, estado='disponible')
    form = BusquedaInmuebleForm(request.GET)
    
    # Aplicar filtros
    if form.is_valid():
        categoria = form.cleaned_data.get('categoria')
        ciudad = form.cleaned_data.get('ciudad')
        precio_min = form.cleaned_data.get('precio_min')
        precio_max = form.cleaned_data.get('precio_max')
        habitaciones = form.cleaned_data.get('habitaciones')
        banos = form.cleaned_data.get('banos')
        amoblado = form.cleaned_data.get('amoblado')
        mascotas = form.cleaned_data.get('mascotas_permitidas')
        
        if categoria:
            inmuebles = inmuebles.filter(categoria=categoria)
        if ciudad:
            inmuebles = inmuebles.filter(ciudad__icontains=ciudad)
        if precio_min:
            inmuebles = inmuebles.filter(precio_arriendo__gte=precio_min)
        if precio_max:
            inmuebles = inmuebles.filter(precio_arriendo__lte=precio_max)
        if habitaciones:
            inmuebles = inmuebles.filter(habitaciones__gte=habitaciones)
        if banos:
            inmuebles = inmuebles.filter(banos__gte=banos)
        if amoblado:
            inmuebles = inmuebles.filter(amoblado=True)
        if mascotas:
            inmuebles = inmuebles.filter(mascotas_permitidas=True)
    
    # Paginación
    paginator = Paginator(inmuebles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'inmuebles': page_obj,
        'form': form,
    }
    return render(request, 'inmuebles/listar.html', context)


def detalle_inmueble(request, inmueble_id):
    """Vista para ver detalles de un inmueble"""
    inmueble = get_object_or_404(Inmueble, id=inmueble_id, activo=True)
    imagenes = inmueble.get_imagenes()
    caracteristicas = inmueble.caracteristicas.all()
    
    # Inmuebles similares
    similares = Inmueble.objects.filter(
        categoria=inmueble.categoria,
        ciudad=inmueble.ciudad,
        estado='disponible',
        activo=True
    ).exclude(id=inmueble.id)[:4]
    
    context = {
        'inmueble': inmueble,
        'imagenes': imagenes,
        'caracteristicas': caracteristicas,
        'similares': similares,
    }
    return render(request, 'inmuebles/detalle.html', context)


@login_required
def mis_inmuebles(request):
    """Vista para que propietarios vean sus inmuebles"""
    if request.user.tipo_usuario != 'propietario':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('core:dashboard')
    
    inmuebles = Inmueble.objects.filter(propietario=request.user)
    
    # Filtrar por estado si se proporciona
    estado = request.GET.get('estado')
    if estado:
        inmuebles = inmuebles.filter(estado=estado)
    
    paginator = Paginator(inmuebles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'inmuebles': page_obj,
    }
    return render(request, 'inmuebles/mis_inmuebles.html', context)


@login_required
def crear_inmueble(request):
    """Vista para crear un nuevo inmueble"""
    if request.user.tipo_usuario != 'propietario':
        messages.error(request, 'Solo los propietarios pueden registrar inmuebles.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        print(f"=== DEBUG: POST recibido ===")
        print(f"POST data: {request.POST}")
        form = InmuebleForm(request.POST)
        print(f"Form is_valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if form.is_valid():
            try:
                inmueble = form.save(commit=False)
                inmueble.propietario = request.user
                inmueble.save()
                print(f"Inmueble guardado con ID: {inmueble.id}")
                try:
                    inmueble.save_to_firebase()
                    print("Firebase guardado exitosamente")
                except Exception as e:
                    print(f"Error al guardar en Firebase: {e}")
                messages.success(request, 'Inmueble creado exitosamente.')
                return redirect('inmuebles:agregar_imagenes', inmueble_id=inmueble.id)
            except Exception as e:
                print(f"Exception al guardar: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.error(request, f'Error al crear el inmueble: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
            print(f"Errores del formulario: {form.errors.as_json()}")
    else:
        form = InmuebleForm()
    
    return render(request, 'inmuebles/form.html', {'form': form, 'titulo': 'Registrar Inmueble'})


@login_required
def editar_inmueble(request, inmueble_id):
    """Vista para editar un inmueble"""
    inmueble = get_object_or_404(Inmueble, id=inmueble_id, propietario=request.user)
    
    if request.method == 'POST':
        form = InmuebleForm(request.POST, instance=inmueble)
        if form.is_valid():
            inmueble = form.save()
            inmueble.save_to_firebase()
            messages.success(request, 'Inmueble actualizado exitosamente.')
            return redirect('inmuebles:detalle', inmueble_id=inmueble.id)
    else:
        form = InmuebleForm(instance=inmueble)
    
    return render(request, 'inmuebles/form.html', {
        'form': form,
        'titulo': 'Editar Inmueble',
        'inmueble': inmueble
    })


@login_required
def eliminar_inmueble(request, inmueble_id):
    """Vista para eliminar (desactivar) un inmueble"""
    inmueble = get_object_or_404(Inmueble, id=inmueble_id, propietario=request.user)
    
    if request.method == 'POST':
        inmueble.activo = False
        inmueble.save()
        messages.success(request, 'Inmueble eliminado exitosamente.')
        return redirect('inmuebles:mis_inmuebles')
    
    return render(request, 'inmuebles/confirmar_eliminar.html', {'inmueble': inmueble})


@login_required
def agregar_imagenes(request, inmueble_id):
    """Vista para agregar imágenes a un inmueble"""
    inmueble = get_object_or_404(Inmueble, id=inmueble_id, propietario=request.user)
    
    if request.method == 'POST':
        form = ImagenInmuebleForm(request.POST, request.FILES)
        if form.is_valid():
            imagen = form.save(commit=False)
            imagen.inmueble = inmueble
            # Auto-incrementar orden
            ultimo_orden = inmueble.imagenes.count()
            imagen.orden = ultimo_orden
            imagen.save()
            messages.success(request, 'Imagen agregada exitosamente.')
            return redirect('inmuebles:agregar_imagenes', inmueble_id=inmueble.id)
    else:
        form = ImagenInmuebleForm()
    
    imagenes = inmueble.get_imagenes()
    
    return render(request, 'inmuebles/agregar_imagenes.html', {
        'form': form,
        'inmueble': inmueble,
        'imagenes': imagenes
    })


@login_required
def eliminar_imagen(request, imagen_id):
    """Vista para eliminar una imagen"""
    imagen = get_object_or_404(ImagenInmueble, id=imagen_id, inmueble__propietario=request.user)
    inmueble_id = imagen.inmueble.id
    
    if request.method == 'POST':
        imagen.delete()
        messages.success(request, 'Imagen eliminada exitosamente.')
    
    return redirect('inmuebles:agregar_imagenes', inmueble_id=inmueble_id)
