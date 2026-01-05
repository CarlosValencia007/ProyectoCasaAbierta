# 🚀 IMPORTANTE COMO EJECUTAR LEER

## 📋 Requisitos Previos

### 1. Python 3.10 o superior
Verifica tu versión:
```bash
python --version
```

### 2. Virtual Environment Configurado
El proyecto usa un virtual environment ubicado en:
```
C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta\venv
```

### 3. Dependencias Instaladas
Si no tienes el venv configurado, instala las dependencias:
```bash
cd "C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta"
python -m venv venv
.\venv\Scripts\Activate.ps1
cd ProyectoCasaAbierta\Servidor
pip install -r requirements.txt
```

---

## 🔧 EJECUTAR EL BACKEND

### Opción 1: Con Virtual Environment (RECOMENDADO)

```powershell
cd "C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta\ProyectoCasaAbierta\Servidor"
C:\Users\"ASUS I5"\OneDrive\Desktop\"Casa abierta"\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Opción 2: Activando el Virtual Environment Primero

```powershell
cd "C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta"
.\venv\Scripts\Activate.ps1
cd ProyectoCasaAbierta\Servidor
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### ✅ Backend Corriendo
El backend estará disponible en:
- **URL Principal**: http://localhost:8080
- **Documentación API**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

---

## 🌐 EJECUTAR EL FRONTEND

### Método 1: Servidor HTTP de Python (RECOMENDADO)

```powershell
cd "C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta\ProyectoCasaAbierta\Frontend"
python -m http.server 5500
```

### Método 2: Live Server de VS Code
1. Instala la extensión "Live Server" en VS Code
2. Abre el archivo `Frontend/index.html`
3. Click derecho → "Open with Live Server"

### ✅ Frontend Corriendo
El frontend estará disponible en:
- **Frontend Principal**: http://localhost:5500/index.html
- **Panel de Testing**: http://localhost:5500/test_frontend.html
- **Quickstart**: http://localhost:5500/quickstart.html

---

## 🎯 ORDEN DE EJECUCIÓN

### 1️⃣ PRIMERO: Iniciar Backend
```powershell
cd "C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta\ProyectoCasaAbierta\Servidor"
C:\Users\"ASUS I5"\OneDrive\Desktop\"Casa abierta"\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

**Espera a ver este mensaje:**
```
✅ Modelos cargados en RAM. El servidor volará 🚀
🚀 Application startup complete
```

### 2️⃣ SEGUNDO: Iniciar Frontend
Abre una **NUEVA terminal** (PowerShell):
```powershell
cd "C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta\ProyectoCasaAbierta\Frontend"
python -m http.server 5500
```

### 3️⃣ TERCERO: Abrir el Navegador
Abre tu navegador y ve a:
```
http://localhost:5500/index.html
```

---

## 🔍 VERIFICAR QUE TODO FUNCIONA

### Test 1: Backend Health Check
Abre en el navegador:
```
http://localhost:8080/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### Test 2: Documentación de la API
```
http://localhost:8080/docs
```

### Test 3: Frontend Cargado
```
http://localhost:5500/index.html
```

Deberías ver la interfaz principal del sistema.

---

## ⚠️ PROBLEMAS COMUNES

### Error: "Port 8080 already in use"
**Solución:** Detén el proceso anterior:
```powershell
netstat -ano | findstr :8080
taskkill /F /PID <PID_DEL_PROCESO>
```

### Error: "Port 5500 already in use"
**Solución:** Usa otro puerto:
```powershell
python -m http.server 5501
```
Luego abre `http://localhost:5501/index.html`

### Error: "ModuleNotFoundError"
**Solución:** Instala las dependencias:
```powershell
cd "C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta"
.\venv\Scripts\Activate.ps1
cd ProyectoCasaAbierta\Servidor
pip install -r requirements.txt
```

### Error: "No module named 'app'"
**Solución:** Asegúrate de estar en el directorio correcto:
```powershell
cd "C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta\ProyectoCasaAbierta\Servidor"
```

---

## 🛑 DETENER LOS SERVIDORES

### Detener Backend
En la terminal del backend, presiona:
```
Ctrl + C
```

### Detener Frontend
En la terminal del frontend, presiona:
```
Ctrl + C
```

### Detener Todos los Procesos Python
```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

## 📝 CONFIGURACIÓN DE SUPABASE

### Variables de Entorno Requeridas
Crea un archivo `.env` en la carpeta `Servidor/` con:

```env
SUPABASE_URL=https://dusciyonacflolbtweob.supabase.co
SUPABASE_KEY=tu_clave_aqui
ENVIRONMENT=development
```

### Configuración de Base de Datos
La base de datos debe tener la extensión pgvector habilitada:

```sql
-- 1. Habilitar pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Cambiar la columna a vector(512) para Facenet512
ALTER TABLE students ALTER COLUMN face_embedding TYPE vector(512);

-- 3. Crear la función RPC para búsqueda de rostros
DROP FUNCTION IF EXISTS match_students_by_embedding(vector, double precision, integer);

CREATE OR REPLACE FUNCTION match_students_by_embedding(
  query_embedding vector(512),
  match_threshold float,
  match_count int
)
RETURNS TABLE(
  student jsonb,
  distance float
)
LANGUAGE SQL STABLE
AS $$
  SELECT
    to_jsonb(students.*) as student,
    (students.face_embedding <=> query_embedding) as distance
  FROM students
  WHERE students.is_active = true
    AND (students.face_embedding <=> query_embedding) < match_threshold
  ORDER BY distance
  LIMIT match_count;
$$;
```

---

## 🎓 FLUJO DE USO

### 1. Registrar Estudiante
- Ve a **Sección 1: Registrar Estudiante**
- Ingresa ID y nombre del estudiante
- Captura foto con la webcam
- Click en "Registrar Estudiante"

### 2. Crear Sesión de Clase
- Ve a **Sección 2: Crear Clase**
- Ingresa nombre de la clase
- Click en "Crear Clase"
- **Guarda el ID de clase generado**

### 3. Verificar Asistencia
- Ve a **Sección 3: Verificar Asistencia**
- Ingresa el ID de clase
- Captura foto del estudiante
- Click en "Verificar Asistencia"
- El sistema reconocerá al estudiante y registrará su asistencia

---

## 📊 ENDPOINTS DISPONIBLES

### Salud del Sistema
```
GET /health
```

### Estudiantes
```
POST /api/v1/enrollment/enroll-v2    # Registrar estudiante
GET  /api/v1/enrollment/students     # Listar estudiantes
```

### Asistencia
```
POST /api/v1/attendance/verify       # Verificar asistencia
GET  /api/v1/attendance/records      # Obtener registros
```

### Clases
```
POST /api/v1/classes/create          # Crear clase
GET  /api/v1/classes/{class_id}      # Obtener información
```

### Emociones
```
POST /api/v1/emotions/detect         # Detectar emociones
GET  /api/v1/emotions/class/{class_id}  # Análisis de clase
```

---

## 🐛 DEBUG MODE

Para más información de debug, activa los logs detallados:

```powershell
$env:LOG_LEVEL="DEBUG"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

---

## ✅ CHECKLIST DE INICIO

- [ ] Python 3.10+ instalado
- [ ] Virtual environment activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Variables de entorno configuradas (`.env`)
- [ ] Supabase configurado (extensión pgvector + función RPC)
- [ ] Backend corriendo en puerto 8080
- [ ] Frontend corriendo en puerto 5500
- [ ] Health check respondiendo correctamente

---

## 🆘 SOPORTE

Si tienes problemas:
1. Revisa los logs del backend en la terminal
2. Abre la consola del navegador (F12) para ver errores del frontend
3. Verifica que Supabase esté configurado correctamente
4. Asegúrate de que los puertos 8080 y 5500 estén libres

---

**¡Sistema Listo para Usar! 🚀**
