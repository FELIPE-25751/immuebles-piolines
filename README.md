# InmueblesApp - Sistema de Gestión de Inmuebles

## 📋 Descripción

InmueblesApp es una aplicación web completa para la gestión de inmuebles en arriendo, desarrollada con Django y Firebase. Permite a propietarios administrar sus propiedades y a inquilinos gestionar sus arriendos de forma digital y eficiente.

## ✨ Características Principales

### 🔐 Sistema de Autenticación
- Registro de usuarios con perfiles diferenciados (Propietario/Inquilino)
- Acceso seguro con autenticación de Django
- Integración con Firebase Authentication
- Gestión de perfiles de usuario

### 🏠 Gestión de Inmuebles
- Registro completo de propiedades (Casa, Apartamento, Local, Oficina, etc.)
- Galería de imágenes para cada inmueble
- Estados de disponibilidad (Disponible, Arrendado, En Mantenimiento)
- Búsqueda y filtrado avanzado
- Vistas diferenciadas para propietarios e inquilinos

### 📄 Gestión de Contratos
- Creación de contratos digitales
- Firma digital con validación de IP y user-agent
- Estados de contrato (Borrador, Activo, Vencido, Finalizado)
- Generación automática de pagos mensuales
- Asignación entre propietarios e inquilinos

### 💰 Sistema de Pagos
- Generación automática de cuentas de cobro
- Registro de pagos con comprobantes
- Cálculo automático de moras
- Reportes de pagos pendientes y vencidos
- Generación de cuentas de cobro en PDF

### 🔧 Gestión de Mantenimientos
- Solicitud de mantenimiento por inquilinos
- Seguimiento de estados (Pendiente, En Proceso, Completado)
- Sistema de prioridades (Baja, Media, Alta, Urgente)
- Comentarios y seguimiento
- Gestión de costos

### 🔔 Sistema de Notificaciones
- Notificaciones en tiempo real
- Configuración personalizada por tipo
- API REST para consultas
- Integración con Firebase Firestore

### 📊 Dashboard y Reportes
- Panel de control con estadísticas
- Reportes financieros para propietarios
- Visualización de métricas clave
- Accesos rápidos a funciones principales

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.x + Django 4.2
- **Base de Datos:** SQLite (desarrollo) / Firebase Firestore (producción)
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Autenticación:** Django Authentication + Firebase Auth
- **Reportes:** ReportLab (generación de PDFs)
- **Icons:** Font Awesome 6

## 📦 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Cuenta de Firebase (para configuración de Firebase)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
```powershell
cd "C:\Users\FELIPE MARTINEZ\Desktop\APLICACION FINAL"
```

2. **Crear entorno virtual**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Instalar dependencias**
```powershell
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Copiar el archivo `.env.example` a `.env`:
```powershell
Copy-Item .env.example .env
```

Editar el archivo `.env` y configurar:
```
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. **Configurar Firebase**

a. Ir a [Firebase Console](https://console.firebase.google.com/)
b. Crear un nuevo proyecto o usar uno existente
c. Ir a "Configuración del proyecto" → "Cuentas de servicio"
d. Generar nueva clave privada
e. Descargar el archivo JSON
f. Guardar el archivo como `firebase-credentials.json` en la raíz del proyecto

6. **Crear carpetas estáticas**
```powershell
mkdir static, media, staticfiles
```

7. **Realizar migraciones**
```powershell
python manage.py makemigrations
python manage.py migrate
```

8. **Crear superusuario**
```powershell
python manage.py createsuperuser
```

Sigue las instrucciones para crear el usuario administrador.

9. **Recolectar archivos estáticos**
```powershell
python manage.py collectstatic --noinput
```

10. **Ejecutar el servidor**
```powershell
python manage.py runserver
```

La aplicación estará disponible en: `http://localhost:8000`

## 🎯 Uso de la Aplicación

### Para Propietarios

1. **Registrarse** como tipo "Propietario"
2. **Acceder al Dashboard** para ver estadísticas
3. **Registrar Inmuebles:**
   - Ir a "Nuevo Inmueble"
   - Completar formulario con datos de la propiedad
   - Subir imágenes
4. **Crear Contratos:**
   - Ir a "Nuevo Contrato"
   - Seleccionar inmueble e inquilino
   - Completar términos y condiciones
   - Firmar digitalmente
5. **Gestionar Pagos:**
   - Ver pagos pendientes
   - Generar cuentas de cobro
   - Revisar reportes

### Para Inquilinos

1. **Registrarse** como tipo "Inquilino"
2. **Buscar Inmuebles** disponibles
3. **Firmar Contratos** asignados
4. **Registrar Pagos:**
   - Ir a "Mis Pagos"
   - Registrar pago realizado
   - Subir comprobante
5. **Solicitar Mantenimiento:**
   - Ir a "Solicitar Mantenimiento"
   - Describir el problema
   - Adjuntar fotos si es necesario

## 🔧 Administración

Acceder al panel de administración de Django:
```
http://localhost:8000/admin
```

Usar las credenciales del superusuario creado.

## 📁 Estructura del Proyecto

```
APLICACION FINAL/
├── inmueblesapp/          # Configuración principal
│   ├── settings.py        # Configuración de Django
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # WSGI config
├── core/                  # App de autenticación
│   ├── models.py         # Modelo Usuario
│   ├── views.py          # Vistas de auth
│   └── forms.py          # Formularios
├── inmuebles/            # App de inmuebles
├── contratos/            # App de contratos
├── pagos/               # App de pagos
├── mantenimientos/      # App de mantenimientos
├── notificaciones/      # App de notificaciones
├── templates/           # Plantillas HTML
├── static/              # Archivos estáticos
├── media/              # Archivos subidos
├── requirements.txt    # Dependencias
├── manage.py          # CLI de Django
└── README.md          # Este archivo
```

## 🌐 Variables de Entorno

```env
SECRET_KEY=              # Clave secreta de Django
DEBUG=True              # Modo debug (False en producción)
ALLOWED_HOSTS=          # Hosts permitidos
FIREBASE_CREDENTIALS_PATH=  # Ruta a credenciales Firebase
```

## 🚀 Deployment

### Para producción:

1. Cambiar `DEBUG=False` en `.env`
2. Configurar `ALLOWED_HOSTS` con tu dominio
3. Usar base de datos PostgreSQL o MySQL
4. Configurar servidor web (Nginx + Gunicorn)
5. Habilitar HTTPS con certificado SSL

Comando para ejecutar con Gunicorn:
```bash
gunicorn inmueblesapp.wsgi:application --bind 0.0.0.0:8000
```

## 📝 Notas Importantes

- **Seguridad:** Cambiar la `SECRET_KEY` en producción
- **Firebase:** Mantener las credenciales seguras y no subirlas a repositorios públicos
- **Backups:** Realizar respaldos regulares de la base de datos
- **Logs:** Revisar logs para detectar errores

## 🐛 Solución de Problemas

### Error de Firebase
Si ves errores relacionados con Firebase:
1. Verificar que el archivo `firebase-credentials.json` existe
2. Verificar que las credenciales sean válidas
3. Verificar que Firebase esté habilitado en el proyecto

### Error de Migraciones
```powershell
python manage.py migrate --run-syncdb
```

### Error de Permisos
```powershell
python manage.py collectstatic --clear
```

## 👥 Roles de Usuario

### Propietario
- Gestionar inmuebles
- Crear contratos
- Gestionar pagos
- Aprobar mantenimientos
- Ver reportes

### Inquilino
- Ver inmuebles disponibles
- Firmar contratos
- Registrar pagos
- Solicitar mantenimientos
- Recibir notificaciones

## 📊 Características Técnicas

- **Responsive Design:** Compatible con móviles, tablets y desktop
- **AJAX:** Actualización de notificaciones en tiempo real
- **REST API:** Endpoints para consultas de datos
- **Seguridad:** Validación de permisos por rol
- **Accesibilidad:** Diseño accesible según estándares WCAG

## 📞 Soporte

Para reportar problemas o sugerencias:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo

## 📄 Licencia

Este proyecto fue desarrollado con fines educativos.

## 🙏 Agradecimientos

Desarrollado por Felipe Martínez para presentación al instructor.

---

**Versión:** 1.0.0  
**Fecha:** Octubre 2025  
**Estado:** Producción Ready ✅
