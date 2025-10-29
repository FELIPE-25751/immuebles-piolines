# 🚀 GUÍA DE DESPLIEGUE - INMUEBLES PIOLINES

## ✅ OPCIÓN 1: RENDER.COM (RECOMENDADA)

### Ventajas:
- ✅ GRATIS con base de datos PostgreSQL incluida
- ✅ SSL/HTTPS automático
- ✅ Dominio personalizado: tu-app.onrender.com
- ✅ Muy profesional
- ✅ Deploy automático desde GitHub

### Pasos:

#### 1. Crear cuenta en Render
- Ve a https://render.com
- Regístrate con GitHub o email

#### 2. Crear repositorio en GitHub
```bash
# En tu terminal de VS Code:
git init
git add .
git commit -m "Initial commit - InmueblesPiolines"
git branch -M main
# Crea un repo en GitHub y luego:
git remote add origin https://github.com/TU-USUARIO/inmuebles-piolines.git
git push -u origin main
```

#### 3. Crear PostgreSQL Database en Render
- Dashboard → New → PostgreSQL
- Nombre: inmuebles-db
- Plan: Free
- Copiar el "Internal Database URL"

#### 4. Crear Web Service en Render
- Dashboard → New → Web Service
- Connect tu repositorio de GitHub
- Configuración:
  - Name: inmuebles-piolines
  - Environment: Python 3
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `gunicorn inmueblesapp.wsgi:application`

#### 5. Variables de entorno en Render
Agregar en Environment:
```
SECRET_KEY=genera-una-clave-secreta-larga-y-aleatoria
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=(pegar el Internal Database URL de PostgreSQL)
```

#### 6. Subir archivo de Firebase
- En Render Dashboard → Environment → Secret Files
- Agregar: `firebase-credentials.json` con el contenido de tu archivo

#### 7. Deploy!
- Click en "Create Web Service"
- Esperar 5-10 minutos
- Tu app estará en: https://inmuebles-piolines.onrender.com

---

## ✅ OPCIÓN 2: PYTHONANYWHERE (MÁS SIMPLE)

### Ventajas:
- ✅ GRATIS 100% sin tarjeta
- ✅ Muy fácil de configurar
- ✅ Panel de control simple
- ❌ Dominio: tuusuario.pythonanywhere.com

### Pasos:

#### 1. Crear cuenta
- Ve a https://www.pythonanywhere.com
- Regístrate gratis

#### 2. Subir archivos
- Menú Files → Upload
- Sube tu carpeta del proyecto (puedes usar ZIP)

#### 3. Configurar Web App
- Menú Web → Add new web app
- Python 3.10
- Manual configuration
- Configurar WSGI file y virtualenv

#### 4. Instalar dependencias
```bash
# En consola de PythonAnywhere:
mkvirtualenv --python=/usr/bin/python3.10 inmuebles-env
pip install -r requirements.txt
```

#### 5. Configurar base de datos SQLite
- Ya está incluida, no necesitas PostgreSQL

---

## ✅ OPCIÓN 3: RAILWAY (MODERNA)

### Ventajas:
- ✅ GRATIS $5 de crédito mensual
- ✅ Deploy con 1 click
- ✅ Muy rápido

### Pasos:

#### 1. Crear cuenta
- Ve a https://railway.app
- Regístrate con GitHub

#### 2. New Project
- Deploy from GitHub repo
- Selecciona tu repositorio

#### 3. Railway detecta automáticamente Django
- Agrega PostgreSQL addon
- Configura variables de entorno

---

## 📝 PREPARACIÓN PARA CUALQUIER OPCIÓN

### 1. Crear archivo .gitignore
```
*.pyc
__pycache__/
db.sqlite3
.env
media/
staticfiles/
firebase-credentials.json
```

### 2. Actualizar settings.py para producción
Ya está configurado con decouple ✅

### 3. Collectstatic
```bash
python manage.py collectstatic
```

### 4. Crear superusuario en producción
```bash
python manage.py createsuperuser
```

---

## 🎯 MI RECOMENDACIÓN

**Para tu presentación académica: RENDER.COM**

Razones:
1. Completamente gratis
2. URL profesional (inmuebles-piolines.onrender.com)
3. Base de datos PostgreSQL real (más profesional que SQLite)
4. SSL/HTTPS incluido
5. Puedes mostrar que usas tecnologías profesionales

---

## 🆘 AYUDA ADICIONAL

Si eliges Render, te ayudaré con:
1. Crear el repositorio de GitHub
2. Configurar las variables de entorno
3. Hacer el primer deploy
4. Crear el superusuario
5. Cargar datos de prueba

**¿Cuál opción eliges?**
