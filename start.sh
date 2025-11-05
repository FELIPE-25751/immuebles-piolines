#!/bin/bash
# Script de inicio para Railway - Ejecuta migraciones y luego inicia el servidor

set -e

# Forzar redeploy Railway - commit de prueba


# Instalar dependencias por si el build no las instaló
echo "Instalando dependencias de requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar makemigrations antes de migrar
echo "Generando nuevas migraciones..."
python manage.py makemigrations --noinput

# Esperar y reintentar migraciones hasta que la base de datos esté lista
for i in {1..10}; do
  echo "Intentando aplicar migraciones (intento $i)..."
  python manage.py migrate --noinput && break
  echo "La base de datos no está lista, reintentando en 5 segundos..."
  sleep 5
done

echo "Asegurando la tabla de caché para rate limiting (si aplica)..."
for i in {1..5}; do
  python manage.py createcachetable ratelimit_cache && break || true
  sleep 2
done

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "Iniciando servidor Gunicorn..."
gunicorn inmueblesapp.wsgi:application --bind 0.0.0.0:${PORT:-8000}
