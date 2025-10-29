# 🚀 GUÍA RÁPIDA - 10 MINUTOS

## ✅ LO QUE ACABÉ DE HACER:

1. ✅ **Integré Firebase JavaScript** en tu aplicación
   - Ahora tienes notificaciones en tiempo real
   - Firebase funciona en el frontend (navegador)
   
2. ✅ **Preparé archivos para producción**:
   - `requirements.txt` ← Dependencias Python actualizadas
   - `runtime.txt` ← Versión de Python (3.13.6)
   - `Procfile` ← Comando para iniciar servidor
   - `build.sh` ← Script de build automático
   - `.gitignore` ← Archivos a ignorar en Git
   - `settings.py` ← Configurado para PostgreSQL y SQLite

3. ✅ **Firebase está integrado en 2 niveles**:
   - **Backend (Python)**: `firebase-admin` para guardar datos
   - **Frontend (JavaScript)**: Notificaciones en tiempo real

---

## 📋 LO QUE TIENES QUE HACER TÚ (15 PASOS):

### PARTE 1: GIT Y GITHUB (5 minutos)

#### 1️⃣ Abrir PowerShell en VS Code
- Presiona `` Ctrl + ` `` (acento grave)
- O ve a: Terminal → New Terminal

#### 2️⃣ Configurar Git (SOLO LA PRIMERA VEZ)
```powershell
git config --global user.name "TU NOMBRE COMPLETO"
git config --global user.email "tu-email@gmail.com"
```

#### 3️⃣ Inicializar repositorio
```powershell
cd "C:\Users\FELIPE MARTINEZ\Desktop\APLICACION FINAL"
git init
git add .
git commit -m "Aplicacion InmueblesPiolines completa con Firebase"
```

#### 4️⃣ Crear repositorio en GitHub
1. Ve a https://github.com/new
2. Nombre: `inmuebles-piolines`
3. Público
4. NO marcar nada más
5. Click "Create repository"

#### 5️⃣ Subir código a GitHub
```powershell
git remote add origin https://github.com/TU-USUARIO/inmuebles-piolines.git
git branch -M main
git push -u origin main
```
*(Reemplaza TU-USUARIO con tu usuario de GitHub)*

---

### PARTE 2: RENDER (5 minutos)

#### 6️⃣ Crear cuenta en Render
- Ve a https://render.com
- Click "Get Started"
- Regístrate con GitHub (más fácil)

#### 7️⃣ Crear base de datos PostgreSQL
1. Dashboard → "New +" → "PostgreSQL"
2. Name: `inmuebles-db`
3. Plan: **Free**
4. Click "Create Database"
5. **ESPERA 2 minutos**
6. **COPIA el "Internal Database URL"** (lo necesitarás)

#### 8️⃣ Crear Web Service
1. Dashboard → "New +" → "Web Service"
2. "Connect to Git Provider" → GitHub
3. Busca `inmuebles-piolines`
4. Click "Connect"

#### 9️⃣ Configuración básica
- **Name**: `inmuebles-piolines`
- **Region**: Oregon (US West)
- **Branch**: `main`
- **Runtime**: Python 3
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn inmueblesapp.wsgi:application`
- **Plan**: Free

#### 🔟 Variables de entorno
Click "Add Environment Variable" y agrega estas **5 variables**:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | `django-insecure-cambia-esto-por-algo-aleatorio-12345` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `DATABASE_URL` | *(Pega el Internal Database URL que copiaste)* |
| `PYTHON_VERSION` | `3.13.6` |

---

### PARTE 3: FIREBASE Y DEPLOY (5 minutos)

#### 1️⃣1️⃣ Subir credenciales de Firebase
1. En la misma página, scroll down hasta "Secret Files"
2. Click "Add Secret File"
3. **Filename**: `firebase-credentials.json`
4. **Contents**: (Abre tu archivo local `firebase-credentials.json` y COPIA TODO)
5. Click "Save"

#### 1️⃣2️⃣ ¡DEPLOY!
1. Verifica todo esté correcto
2. Click "Create Web Service"
3. **ESPERA 10-15 minutos** (toma café ☕)

#### 1️⃣3️⃣ Verificar logs
Verás logs como:
```
==> Installing dependencies
==> Collecting static files
==> Running migrations
==> Your service is live 🎉
```

#### 1️⃣4️⃣ Crear superusuario
1. En Render Dashboard → Tu service → "Shell"
2. Ejecuta:
```bash
python manage.py createsuperuser
```
3. Completa:
   - Username: `admin`
   - Email: `tu-email@gmail.com`
   - Password: (tu contraseña secreta)

#### 1️⃣5️⃣ ¡PROBAR!
1. Ve a: `https://inmuebles-piolines.onrender.com`
2. Login con el admin que creaste
3. ¡Funciona! 🎉

---

## 🎉 RESULTADO FINAL

Tu aplicación estará disponible en:
- **URL**: `https://inmuebles-piolines.onrender.com`
- **Admin**: `https://inmuebles-piolines.onrender.com/admin`
- **HTTPS**: ✅ Incluido
- **Firebase**: ✅ Funcionando
- **Base de datos**: ✅ PostgreSQL en la nube

---

## 📱 PARA TU PRESENTACIÓN

### Lo que puedes mostrar:
1. ✅ Aplicación web en vivo en Internet
2. ✅ Login con diferentes roles (propietario/inquilino)
3. ✅ CRUD de inmuebles
4. ✅ Sistema de contratos
5. ✅ Gestión de pagos
6. ✅ Mantenimientos
7. ✅ Notificaciones en tiempo real con Firebase
8. ✅ Base de datos PostgreSQL (profesional)
9. ✅ HTTPS/SSL (seguro)
10. ✅ Deploy automático con GitHub

### Usuarios para demo:
Después del deploy, crea estos usuarios desde el admin:

**Propietario**:
- Username: `propietario1`
- Password: `demo123`
- Tipo: Propietario

**Inquilino**:
- Username: `inquilino1`
- Password: `demo123`
- Tipo: Inquilino

---

## ⚠️ IMPORTANTE

### Archivo firebase-credentials.json
- ❌ NO subir a GitHub (ya está en .gitignore)
- ✅ Solo subirlo como "Secret File" en Render

### Primera visita
- La primera vez que alguien visite tu app, puede tardar 30-60 segundos
- Es normal en el plan Free de Render
- Después será rápido

### Actualizaciones
Cada vez que hagas cambios:
```powershell
git add .
git commit -m "Descripción del cambio"
git push
```
Render se actualizará automáticamente 🚀

---

## 🆘 PROBLEMAS COMUNES

### "git: command not found"
**Solución**: Instala Git desde https://git-scm.com/download/win

### "Permission denied" en GitHub
**Solución**: Usa Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Selecciona "repo"
4. Usa el token como contraseña

### "Build failed" en Render
**Solución**: Verifica que:
- `requirements.txt` esté completo
- `build.sh` tenga permisos (Render lo arregla automáticamente)
- `Procfile` esté correcto

### "Application error" después del deploy
**Solución**: Revisa los logs en Render y verifica:
- `DATABASE_URL` esté correcto
- Variables de entorno estén todas
- `firebase-credentials.json` esté en Secret Files

---

## ✨ ¡LISTO!

Ahora tienes:
- ✅ Código en GitHub
- ✅ App en producción
- ✅ Base de datos en la nube
- ✅ Firebase integrado
- ✅ HTTPS automático
- ✅ Deploy automático

**¡Éxito en tu presentación! 🚀🎓**

---

## 📞 SIGUIENTE PASO

**AHORA MISMO, EJECUTA EN TU TERMINAL:**

```powershell
# Paso 1: Ir a tu carpeta
cd "C:\Users\FELIPE MARTINEZ\Desktop\APLICACION FINAL"

# Paso 2: Ver status
git status
```

**¿Ya tienes Git instalado? Responde "SÍ" o "NO"**
