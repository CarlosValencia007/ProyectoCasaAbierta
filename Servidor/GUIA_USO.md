# 📚 GUÍA DE USO - Smart Classroom AI

## ✅ Pre-requisitos
- ✅ Backend corriendo en: http://localhost:8080
- ✅ Frontend corriendo en: http://localhost:5500
- ✅ Base de datos Supabase configurada
- ✅ Bucket `face-pictures` creado en Supabase Storage

---

## 🎯 FLUJO COMPLETO DE USO

### **PASO 1: Registrar Estudiantes** 📝

1. **Abre el frontend:**
   ```
   http://localhost:5500/test_frontend.html
   ```

2. **Ve a la Sección 1: Enrollment (Registro)**

3. **Registra al menos 2 estudiantes:**

   **Estudiante 1:**
   - ID Estudiante: `EST-001`
   - Nombre: `María García`
   - Email: `maria@ejemplo.com`
   - Click **"📷 Activar Cámara"**
   - Posiciona tu cara frente a la cámara
   - Click **"📸 Capturar Foto"**
   - Verás un preview de la foto
   - Click **"Registrar Estudiante"**
   - Espera el mensaje: ✅ "Student enrolled successfully"

   **Estudiante 2:**
   - ID Estudiante: `EST-002`
   - Nombre: `Juan Pérez`
   - Email: `juan@ejemplo.com`
   - Repite el proceso de captura de foto
   - Click **"Registrar Estudiante"**

4. **Verifica los registros:**
   - Ve a la **Sección 6: Student List**
   - Click **"🔄 Cargar Estudiantes"**
   - Deberías ver los 2 estudiantes registrados con sus fotos

---

### **PASO 2: Crear una Clase** 📅

1. **Ve a la Sección 2: Create Class Session**

2. **Llena el formulario:**
   - Nombre de Clase: `Matemáticas 101`
   - Fecha: `2026-01-04` (hoy)
   - Hora de Inicio: `10:00`
   - Hora de Fin: `12:00`

3. **Click en "Crear Sesión de Clase"**

4. **Resultado esperado:**
   ```json
   {
     "success": true,
     "message": "Class session created",
     "class_id": "550e8400-e29b-41d4-a716-446655440000"
   }
   ```

5. **IMPORTANTE: Copia el `class_id`** - Lo necesitarás para tomar asistencia

---

### **PASO 3: Tomar Asistencia** ✅

1. **Ve a la Sección 3: Verify Attendance**

2. **Ingresa el Class ID:**
   - Pega el `class_id` que copiaste en el paso anterior
   - Ejemplo: `550e8400-e29b-41d4-a716-446655440000`

3. **Tomar asistencia del Estudiante 1:**
   - Click **"📷 Activar Cámara de Asistencia"**
   - Posiciona tu cara (la misma persona que se registró como EST-001)
   - Click **"📸 Capturar para Verificación"**
   - Click **"Verificar Asistencia"**

4. **Resultado esperado:**
   ```json
   {
     "success": true,
     "student_id": "EST-001",
     "name": "María García",
     "confidence": 0.95,
     "status": "present"
   }
   ```

5. **Repite para el Estudiante 2:**
   - Captura otra foto
   - Click **"Verificar Asistencia"**
   - Debe reconocer al segundo estudiante

6. **Prueba con alguien NO registrado:**
   - Captura foto de otra persona
   - Debe decir: "Student not recognized"

---

### **PASO 4: Ver Reportes de Asistencia** 📊

1. **Ve a la Sección 5: Reports**

2. **Ingresa el Class ID:**
   - Pega el mismo `class_id` de antes

3. **Click en "Obtener Reporte de Asistencia"**

4. **Verás el reporte:**
   ```
   📊 Reporte de Asistencia
   
   Clase: Matemáticas 101
   Fecha: 2026-01-04
   
   ✅ Presentes: 2
   ❌ Ausentes: 0
   
   Lista de Asistencia:
   ✅ EST-001 - María García (95% confianza)
   ✅ EST-002 - Juan Pérez (92% confianza)
   ```

---

### **PASO 5: (Opcional) Análisis de Emociones** 😊

1. **Ve a la Sección 4: Emotion Analysis**

2. **Ingresa Student ID:** `EST-001`

3. **Ingresa Class ID:** (el mismo de antes)

4. **Activa la cámara y captura foto**

5. **Click en "Analizar Emoción"**

6. **Resultado esperado:**
   ```json
   {
     "success": true,
     "student_id": "EST-001",
     "emotion": "happy",
     "confidence": 0.85,
     "emotions": {
       "happy": 0.85,
       "neutral": 0.10,
       "surprise": 0.05
     }
   }
   ```

---

## 🔧 Troubleshooting

### ❌ "Backend: Checking..."
**Problema:** El frontend no puede conectar con el backend

**Solución:**
1. Verifica que el backend esté corriendo:
   ```powershell
   netstat -ano | findstr :8080
   ```
2. Si no está corriendo, inícialo:
   ```powershell
   cd "C:\Users\ASUS I5\OneDrive\Desktop\Casa abierta\ProyectoCasaAbierta\Servidor"
   C:\Users\"ASUS I5"\OneDrive\Desktop\"Casa abierta"\venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8080
   ```

### ❌ "Failed to upload photo"
**Problema:** La foto no se guarda en Supabase Storage

**Solución:**
1. Verifica que el bucket `face-pictures` exista en Supabase
2. Verifica que sea **público**
3. Verifica que `SUPABASE_SERVICE_KEY` esté en el `.env`

### ❌ "Camera not accessible"
**Problema:** El navegador no puede acceder a la cámara

**Solución:**
1. Debes usar **http://localhost:5500** (no file://)
2. Acepta los permisos de cámara cuando el navegador los pida
3. En Chrome: Click en el ícono de cámara en la barra de direcciones → Permitir

### ❌ "Student not recognized"
**Problema:** El sistema no reconoce al estudiante

**Posibles causas:**
1. La foto es muy diferente (iluminación, ángulo, expresión)
2. El threshold es muy estricto (actual: 0.6)
3. El estudiante no está registrado

**Solución:**
1. Asegúrate de usar la misma persona que se registró
2. Mejora la iluminación
3. Mira directamente a la cámara
4. Si persiste, ajusta el threshold en `.env`:
   ```
   FACE_MATCH_THRESHOLD=0.7  # Más permisivo (0.0 - 1.0)
   ```

---

## 📝 Notas Importantes

1. **Primera vez que capturas foto:** El navegador pedirá permisos de cámara - debes aceptar

2. **Iluminación:** La calidad del reconocimiento mejora con buena iluminación

3. **Distancia:** Mantén tu rostro a 30-50 cm de la cámara

4. **Ángulo:** Mira directamente a la cámara (evita ángulos extremos)

5. **Expresión:** Trata de mantener una expresión similar entre registro y verificación

6. **Backend logs:** Para ver qué está pasando, revisa la terminal del backend:
   ```
   → POST /api/v1/enrollment/enroll
   ✅ Estudiante EST-001 registrado exitosamente
   ← POST /api/v1/enrollment/enroll [201] 2.543s
   ```

---

## 🎉 ¡Listo!

Ahora tienes un sistema completo de:
- ✅ Registro de estudiantes con reconocimiento facial
- ✅ Creación de sesiones de clase
- ✅ Verificación automática de asistencia
- ✅ Análisis de emociones en tiempo real
- ✅ Reportes de asistencia

**¿Necesitas ayuda?** Revisa los logs del backend en la terminal donde corre uvicorn.
