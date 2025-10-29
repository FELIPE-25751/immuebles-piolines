"""
URL configuration for inmueblesapp project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('inmuebles/', include('inmuebles.urls')),
    path('contratos/', include('contratos.urls')),
    path('pagos/', include('pagos.urls')),
    path('mantenimientos/', include('mantenimientos.urls')),
    path('notificaciones/', include('notificaciones.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
