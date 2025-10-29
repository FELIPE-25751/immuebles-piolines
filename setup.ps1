# Script de configuración inicial para InmueblesApp
# Ejecutar en PowerShell

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "InmueblesApp - Configuración Inicial" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python instalado correctamente" -ForegroundColor Green
Write-Host ""

# Crear entorno virtual
Write-Host "2. Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "El entorno virtual ya existe" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✓ Entorno virtual creado" -ForegroundColor Green
}
Write-Host ""

# Activar entorno virtual
Write-Host "3. Activando entorno virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Entorno virtual activado" -ForegroundColor Green
Write-Host ""

# Instalar dependencias
Write-Host "4. Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudieron instalar las dependencias" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencias instaladas" -ForegroundColor Green
Write-Host ""

# Crear archivo .env si no existe
Write-Host "5. Configurando variables de entorno..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Archivo .env creado desde .env.example" -ForegroundColor Green
    Write-Host "  IMPORTANTE: Edita el archivo .env con tus configuraciones" -ForegroundColor Yellow
} else {
    Write-Host "El archivo .env ya existe" -ForegroundColor Yellow
}
Write-Host ""

# Crear directorios necesarios
Write-Host "6. Creando directorios..." -ForegroundColor Yellow
$dirs = @("static", "media", "staticfiles", "media\perfiles", "media\inmuebles", "media\contratos", "media\comprobantes", "media\mantenimientos")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Creado: $dir" -ForegroundColor Green
    }
}
Write-Host ""

# Verificar Firebase credentials
Write-Host "7. Verificando credenciales de Firebase..." -ForegroundColor Yellow
if (!(Test-Path "firebase-credentials.json")) {
    Write-Host "  ⚠ ADVERTENCIA: No se encontró firebase-credentials.json" -ForegroundColor Yellow
    Write-Host "  Necesitas:" -ForegroundColor Yellow
    Write-Host "    1. Crear un proyecto en Firebase Console" -ForegroundColor Cyan
    Write-Host "    2. Ir a Configuración -> Cuentas de servicio" -ForegroundColor Cyan
    Write-Host "    3. Generar nueva clave privada" -ForegroundColor Cyan
    Write-Host "    4. Guardar el archivo como firebase-credentials.json" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Puedes usar firebase-credentials.json.example como referencia" -ForegroundColor Yellow
} else {
    Write-Host "✓ firebase-credentials.json encontrado" -ForegroundColor Green
}
Write-Host ""

# Realizar migraciones
Write-Host "8. Ejecutando migraciones..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Falló la migración de la base de datos" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Migraciones completadas" -ForegroundColor Green
Write-Host ""

# Recolectar archivos estáticos
Write-Host "9. Recolectando archivos estáticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput
Write-Host "✓ Archivos estáticos recolectados" -ForegroundColor Green
Write-Host ""

# Crear superusuario
Write-Host "10. ¿Deseas crear un superusuario ahora? (S/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq "S" -or $response -eq "s") {
    python manage.py createsuperuser
}
Write-Host ""

# Resumen final
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Configuración Completada!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "1. Edita el archivo .env con tus configuraciones" -ForegroundColor White
Write-Host "2. Configura Firebase y coloca las credenciales en firebase-credentials.json" -ForegroundColor White
Write-Host "3. Ejecuta: python manage.py runserver" -ForegroundColor White
Write-Host "4. Abre tu navegador en: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Para iniciar el servidor ahora, ejecuta:" -ForegroundColor Cyan
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "¡Buena suerte con tu presentación! 🚀" -ForegroundColor Green
