# 🚀 GUÍA PASO A PASO - DEPLOY COMPLETO

## ✅ YA TENEMOS:
1. ✅ Firebase Hosting funcionando: https://immuebles-piolines.web.app
2. ✅ Código Django completo y funcionando localmente
3. ✅ Git inicializado y primer commit hecho

---

## 📋 AHORA SIGUE ESTOS PASOS EXACTOS:

### PASO 1: CREAR REPOSITORIO EN GITHUB (5 minutos)

1. **Abre tu navegador** y ve a: https://github.com/new

2. **Llena el formulario:**
   - **Repository name**: `inmuebles-piolines`
   - **Description**: `Sistema de gestión de inmuebles con Django y Firebase`
   - **Visibility**: ✅ Public (o Private si prefieres)
   - ❌ **NO marques** "Add a README file"
   - ❌ **NO marques** "Add .gitignore"
   - ❌ **NO marques** "Choose a license"

3. **Click en**: "Create repository" (botón verde)

4. **Copia la URL** que aparece (se verá así):
   ```
   https://github.com/TU-USUARIO/inmuebles-piolines.git
   ```

### PASO 2: CONECTAR TU CÓDIGO CON GITHUB (2 minutos)

Vuelve a VS Code y ejecuta en la terminal:

```powershell
# Reemplaza TU-USUARIO con tu usuario de GitHub
git remote add origin https://github.com/TU-USUARIO/inmuebles-piolines.git

# Renombrar rama a main
git branch -M main

# Subir código
git push -u origin main
```

**Si pide usuario y contraseña:**
- Usuario: tu usuario de GitHub
- Contraseña: **Personal Access Token** (NO tu contraseña normal)

**Para crear un token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)"
3. Nombre: "InmueblesPiolines"
4. Expiration: 90 days
5. Scopes: ✅ Marcar "repo"
6. "Generate token"
7. **COPIAR Y GUARDAR** el token (no lo volverás a ver)

### PASO 3: CREAR CUENTA EN RENDER (3 minutos)

1. Ve a: https://render.com
2. Click en "Get Started"
3. **Regístrate con GitHub** (más fácil)
4. Autoriza Render a acceder a tus repos

### PASO 4: CREAR BASE DE DATOS POSTGRESQL (3 minutos)

1. En Render Dashboard → Click "New +" → "PostgreSQL"

2. **Configuración:**
   - Name: `inmuebles-db`
   - Database: `inmuebles_db`
   - User: `inmuebles_user` (automático)
   - Region: **Oregon (US West)**
   - PostgreSQL Version: 16
   - Plan: **Free**

3. Click "Create Database"

4. **ESPERA 2-3 minutos** hasta que diga "Available"

5. En la página de tu base de datos:
   - Busca la sección "Connections"
   - **COPIA el "Internal Database URL"**
   - Se ve así: `postgresql://inmuebles_user:PASSWORD@dpg-xxxxx/inmuebles_db`
   - **GUÁRDALO** en un archivo de texto temporal

### PASO 5: CREAR WEB SERVICE (5 minutos)

1. Render Dashboard → "New +" → "Web Service"

2. "Connect a repository" → Busca `inmuebles-piolines` → Click "Connect"

3. **Configuración básica:**
   - **Name**: `inmuebles-piolines`
   - **Region**: Oregon (US West) ← MISMA QUE LA BD
   - **Branch**: `main`
   - **Root Directory**: (dejar vacío)
   - **Runtime**: Python 3
   - **Build Command**:
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**:
     ```
     gunicorn inmueblesapp.wsgi:application
     ```
   - **Plan**: Free

### PASO 6: VARIABLES DE ENTORNO (5 minutos)

En la misma página, scroll down hasta "Environment Variables".

Click "Add Environment Variable" y agrega estas **6 variables**:

#### Variable 1:
- Key: `SECRET_KEY`
- Value: `django-insecure-tu-clave-super-secreta-cambiala-por-algo-aleatorio-12345678`

#### Variable 2:
- Key: `DEBUG`
- Value: `False`

#### Variable 3:
- Key: `ALLOWED_HOSTS`
- Value: `.onrender.com`

#### Variable 4:
- Key: `DATABASE_URL`
- Value: (PEGA EL INTERNAL DATABASE URL QUE COPIASTE)

#### Variable 5:
- Key: `PYTHON_VERSION`
- Value: `3.13.6`

#### Variable 6:
- Key: `FIREBASE_CREDENTIALS_PATH`
- Value: `firebase-credentials.json`

### PASO 7: SUBIR CREDENCIALES DE FIREBASE (3 minutos)

1. En la misma página, scroll más abajo hasta "Secret Files"

2. Click "Add Secret File"

3. **Configuración:**
   - **Filename**: `firebase-credentials.json`
   - **Contents**: (Abre tu archivo local `firebase-credentials.json` y COPIA TODO el contenido)

4. Click "Save"

### PASO 8: ¡DEPLOY! (10-15 minutos)

1. Verifica que todo esté correcto

2. Click en **"Create Web Service"** (botón azul)

3. **ESPERA 10-15 minutos** (toma un café ☕)

4. Verás logs en tiempo real. Busca estos mensajes:
   ```
   ==> Installing dependencies
   ==> Collecting static files
   ==> Running migrations
   ==> Starting server
   ==> Your service is live 🎉
   ```

### PASO 9: CREAR SUPERUSUARIO (2 minutos)

1. En Render Dashboard → Tu web service → "Shell" (menú izquierdo)

2. Ejecuta:
   ```bash
   python manage.py createsuperuser
   ```

3. Completa:
   - Username: `admin`
   - Email: `izmaelh9@gmail.com`
   - Password: (tu contraseña)
   - Password (again): (tu contraseña)

### PASO 10: ¡PROBAR! (5 minutos)

1. Ve a la URL de tu app:
   ```
   https://inmuebles-piolines.onrender.com
   ```

2. **Login con el admin** que creaste

3. **Crear usuarios de prueba:**
   - Ve a: https://inmuebles-piolines.onrender.com/admin
   - Crea un usuario "Propietario"
   - Crea un usuario "Inquilino"

4. **Probar funcionalidades:**
   - Login como propietario
   - Crear un inmueble
   - Ver lista de inmuebles
   - Etc.

---

## 🎉 RESULTADO FINAL

Tendrás DOS sitios funcionando:

### 1. LANDING PAGE (Firebase Hosting):
**URL**: https://immuebles-piolines.web.app
- Página de presentación
- Firebase integrado
- HTTPS automático

### 2. APLICACIÓN COMPLETA (Render):
**URL**: https://inmuebles-piolines.onrender.com
- Django backend funcionando
- Base de datos PostgreSQL
- Todas las funcionalidades activas
- Admin panel
- HTTPS automático

---

## 🔗 CONECTAR AMBOS (OPCIONAL)

Si quieres que la landing page lleve a la app:

1. Edita `public/index.html`
2. Cambia el botón:
   ```html
   <a href="https://inmuebles-piolines.onrender.com" class="btn btn-custom">
       Ir a la Aplicación
   </a>
   ```
3. Deploy:
   ```powershell
   firebase deploy --only hosting
   ```

---

## ⚠️ IMPORTANTE

### Primera carga:
- La app en Render puede tardar **30-60 segundos** la primera vez
- Es normal en el plan Free
- Después será más rápido

### Mantener activo:
- El plan Free de Render se duerme después de 15 minutos sin uso
- Se despierta automáticamente cuando alguien visita

---

## 📞 ¿NECESITAS AYUDA?

Si algo falla en algún paso, dime en cuál paso estás y qué error ves.

**¡ÉXITO! 🚀**
