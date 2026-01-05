# ⚠️ Pasos Pendientes para Completar el Sistema

## 1. Ejecutar SQL en Supabase (REQUERIDO)

Ve a **Supabase Dashboard → SQL Editor** y ejecuta:

```sql
-- Agregar columna photo_url a la tabla students
ALTER TABLE public.students ADD COLUMN IF NOT EXISTS photo_url TEXT;

-- Refrescar el caché de Supabase
NOTIFY pgrst, 'reload schema';
```

**Cómo llegar:**
1. Abre https://supabase.com/dashboard
2. Selecciona tu proyecto
3. Click en "SQL Editor" en el menú lateral
4. Click en "+ New query"
5. Pega el código SQL de arriba
6. Click en "Run" o presiona Ctrl+Enter

## 2. Verificar el Estado

Una vez ejecutado el SQL, intenta registrar un estudiante nuevamente.

### ✅ Cosas que ya están funcionando:
- Backend corriendo en http://localhost:8080
- Frontend corriendo en http://localhost:5500/test_frontend.html
- Bucket "face-pictures" creado en Supabase Storage (público)
- Código de Storage Service implementado
- Interfaz con captura de cámara lista

### ❌ Problema actual:
```
Error: Could not find the 'photo_url' column of 'students' in the schema cache
```

Este error se soluciona ejecutando el SQL del paso 1.

## 3. Prueba Completa

Después de ejecutar el SQL:

1. Refresca la página: http://localhost:5500/test_frontend.html
2. En "1. Registrar Estudiante":
   - Ingresa ID: `EST-001`
   - Ingresa Nombre: `Juan Pérez`
   - Click en "📷 Activar Cámara"
   - Click en "📸 Capturar Foto"
   - Click en "Registrar Estudiante"

3. Verifica en Supabase:
   - **Storage → face-pictures → students**: Deberías ver la foto
   - **Table Editor → students**: Deberías ver el registro con photo_url

## 4. Si la cámara no se ve:

- Asegúrate de dar permisos a tu navegador para usar la cámara
- Refresca la página con Ctrl+Shift+R (limpia caché)
- Verifica en la consola del navegador (F12) si hay errores
- Prueba con otro navegador (Chrome, Edge, Firefox)

## 5. Comandos útiles para reiniciar servidores:

**Backend (Terminal Python):**
```powershell
cd "C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta\ProyectoCasaAbierta\Servidor"
C:\Users\"ASUS I5"\OneDrive\Desktop\"Casa abierta"\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

**Frontend (Terminal separada):**
```powershell
cd "C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta\ProyectoCasaAbierta\Servidor"
python -m http.server 5500
```

## 6. Siguiente flujo a probar:

Una vez que el registro funcione:

1. ✅ Registrar 2-3 estudiantes
2. Crear una sesión de clase
3. Tomar asistencia con la cámara
4. Analizar emociones
5. Ver reportes

---

**⚡ ACCIÓN INMEDIATA:** Ejecuta el SQL del paso 1 en Supabase para solucionar el error.
