#!/bin/bash
# Script de inicio para Railway - Ejecuta migraciones y luego inicia el servidor

echo "Ejecutando migraciones..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "Iniciando servidor Gunicorn..."
gunicorn inmueblesapp.wsgi:application --bind 0.0.0.0:${PORT:-8000}
