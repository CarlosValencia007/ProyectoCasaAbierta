# Smart Classroom AI - Flujo Detallado del Sistema

## 📋 Índice
1. [Configuración Inicial](#configuración-inicial)
2. [Fase 1: Registro de Estudiantes](#fase-1-registro-de-estudiantes)
3. [Fase 2: Creación de Sesión de Clase](#fase-2-creación-de-sesión-de-clase)
4. [Fase 3: Toma de Asistencia](#fase-3-toma-de-asistencia)
5. [Fase 4: Monitoreo Emocional](#fase-4-monitoreo-emocional)
6. [Fase 5: Reportes y Análisis](#fase-5-reportes-y-análisis)

---

## Configuración Inicial

### Base de Datos Supabase
```sql
-- Tablas existentes:
- students           → Estudiantes registrados (ID, nombre, embedding, photo_url)
- class_sessions     → Sesiones de clase (class_id, fecha, instructor, room)
- attendance         → Registros de asistencia
- emotion_events     → Eventos emocionales detectados
```

### Storage Supabase
- **Bucket:** `face-pictures`
- **Estructura:** `students/{student_id}_{uuid}.jpg`
- **Acceso:** Público

---

## Fase 1: Registro de Estudiantes

### Objetivo
Registrar estudiantes con sus datos biométricos antes de usar el sistema.

### Endpoint
**POST** `/api/v1/enrollment/enroll`

### Request
```json
{
  "student_id": "STU-001",
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "image_base64": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

### Proceso Interno
1. **Validación de imagen**
   - Decodifica base64
   - Verifica formato y tamaño mínimo
   - Valida que contenga un rostro

2. **Subida a Storage**
   ```
   Supabase Storage
   └── face-pictures/
       └── students/
           └── STU-001_a3f5d9e2.jpg
   ```
   - Genera nombre único: `{student_id}_{uuid}.jpg`
   - Sube a bucket público
   - Obtiene URL pública

3. **Generación de Embedding**
   - Usa modelo: **Facenet512** (512 dimensiones)
   - Detector: **RetinaFace**
   - Genera vector numérico que representa el rostro

4. **Guardado en Base de Datos**
   ```sql
   INSERT INTO students (
     student_id,
     name,
     email,
     face_embedding,  -- vector[512]
     photo_url,       -- URL pública
     enrolled_at,
     is_active
   ) VALUES (...)
   ```

### Response
```json
{
  "success": true,
  "message": "Student enrolled successfully",
  "student_id": "STU-001",
  "name": "Juan Pérez",
  "photo_url": "https://...supabase.co/storage/v1/object/public/face-pictures/students/STU-001_a3f5d9e2.jpg",
  "embedding_dimension": 512,
  "enrolled_at": "2026-01-04T10:30:00Z"
}
```

### Endpoints Adicionales
- **GET** `/api/v1/enrollment/students` - Lista todos los estudiantes
- **GET** `/api/v1/enrollment/student/{student_id}` - Obtiene un estudiante
- **PUT** `/api/v1/enrollment/update-photo/{student_id}` - Actualiza foto

---

## Fase 2: Creación de Sesión de Clase

### Objetivo
Crear una sesión de clase antes de tomar asistencia o analizar emociones.

### Tabla en BD
```sql
class_sessions (
  id SERIAL PRIMARY KEY,
  class_id VARCHAR UNIQUE,        -- "MATH-101-2026-01-04"
  class_name VARCHAR,              -- "Matemáticas Avanzadas"
  instructor VARCHAR,              -- "Prof. García"
  room VARCHAR,                    -- "Aula 301"
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  total_students INT DEFAULT 0,
  present_count INT DEFAULT 0,
  attendance_rate FLOAT DEFAULT 0.0,
  created_at TIMESTAMP,
  metadata JSONB
)
```

### Endpoint
**POST** `/api/v1/classes/create`

### Request
```json
{
  "class_id": "MATH-101-2026-01-04",
  "class_name": "Matemáticas Avanzadas",
  "instructor": "Prof. García",
  "room": "Aula 301",
  "start_time": "2026-01-04T08:00:00Z",
  "metadata": {
    "subject": "Mathematics",
    "level": "Advanced"
  }
}
```

### Response
```json
{
  "success": true,
  "message": "Class session created successfully",
  "data": {
    "id": 1,
    "class_id": "MATH-101-2026-01-04",
    "class_name": "Matemáticas Avanzadas",
    "instructor": "Prof. García",
    "room": "Aula 301",
    "start_time": "2026-01-04T08:00:00Z",
    "end_time": null,
    "total_students": 0,
    "present_count": 0,
    "attendance_rate": 0.0,
    "created_at": "2026-01-04T07:45:00Z"
  }
}
```

### Endpoints Adicionales para Classes
- **GET** `/api/v1/classes/list` - Lista todas las sesiones
- **GET** `/api/v1/classes/{class_id}` - Obtiene una sesión específica
- **PUT** `/api/v1/classes/{class_id}` - Actualiza sesión
- **DELETE** `/api/v1/classes/{class_id}` - Elimina sesión
- **GET** `/api/v1/classes/{class_id}/report` - Reporte completo de la clase

---

## Fase 3: Toma de Asistencia

### 3.1 Asistencia Individual

#### Endpoint
**POST** `/api/v1/attendance/verify`

#### Request
```json
{
  "class_id": "MATH-101-2026-01-04",
  "image_base64": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

#### Proceso Interno
1. **Detección de rostro**
   - Usa RetinaFace para detectar cara
   - Valida tamaño mínimo (80px)

2. **Generación de embedding**
   - Crea vector de 512 dimensiones
   - Usa mismo modelo que enrollment

3. **Búsqueda en BD (pgvector)**
   ```sql
   SELECT 
     student_id, 
     name, 
     face_embedding <-> '[0.123, 0.456, ...]' AS distance
   FROM students
   WHERE is_active = true
   ORDER BY distance ASC
   LIMIT 1;
   ```
   - Usa distancia euclidiana
   - Compara con todos los embeddings
   - Encuentra el más similar

4. **Validación de threshold**
   - Si `distance < 0.6` → Match confirmado
   - Si `distance >= 0.6` → No reconocido

5. **Registro de asistencia**
   ```sql
   INSERT INTO attendance (
     student_id,
     class_id,
     status,
     confidence,
     match_distance,
     timestamp
   ) VALUES (...)
   ```

#### Response
```json
{
  "success": true,
  "message": "Attendance verified successfully",
  "data": {
    "student_id": "STU-001",
    "name": "Juan Pérez",
    "status": "present",
    "confidence": 0.95,
    "match_distance": 0.42,
    "timestamp": "2026-01-04T08:15:00Z"
  }
}
```

### 3.2 Asistencia Masiva (Batch)

#### Endpoint
**POST** `/api/v1/attendance/batch-verify`

#### Request
```json
{
  "class_id": "MATH-101-2026-01-04",
  "images": [
    "data:image/jpeg;base64,/9j/4AAQ...",
    "data:image/jpeg;base64,/9j/4BBR...",
    "data:image/jpeg;base64,/9j/4CCS..."
  ]
}
```

#### Proceso
- Procesa cada imagen individualmente
- Identifica múltiples estudiantes
- Registra todas las asistencias
- Máximo: 50 imágenes por batch

#### Response
```json
{
  "success": true,
  "message": "Processed 3 images",
  "data": {
    "class_id": "MATH-101-2026-01-04",
    "total_images": 3,
    "successful_matches": 3,
    "failed_matches": 0,
    "students_identified": [
      {
        "student_id": "STU-001",
        "name": "Juan Pérez",
        "confidence": 0.95
      },
      {
        "student_id": "STU-002",
        "name": "María López",
        "confidence": 0.92
      }
    ]
  }
}
```

---

## Fase 4: Monitoreo Emocional

### 4.1 Análisis Individual

#### Endpoint
**POST** `/api/v1/emotions/analyze`

#### Request
```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQ...",
  "student_id": "STU-001",
  "class_id": "MATH-101-2026-01-04"
}
```

#### Proceso
1. **Detección de rostro**
2. **Análisis emocional con DeepFace**
   - Detecta 7 emociones: `happy`, `sad`, `angry`, `surprise`, `fear`, `disgust`, `neutral`
   - Genera scores de confianza para cada una
   - Identifica emoción dominante

3. **Guardado en BD**
   ```sql
   INSERT INTO emotion_events (
     student_id,
     class_id,
     dominant_emotion,
     confidence,
     emotion_scores,
     detected_at
   ) VALUES (...)
   ```

#### Response
```json
{
  "success": true,
  "message": "Emotion analyzed successfully",
  "data": {
    "dominant_emotion": "happy",
    "confidence": 0.87,
    "all_emotions": {
      "happy": 0.87,
      "neutral": 0.10,
      "surprise": 0.02,
      "sad": 0.01,
      "angry": 0.0,
      "fear": 0.0,
      "disgust": 0.0
    }
  }
}
```

### 4.2 Análisis Masivo

#### Endpoint
**POST** `/api/v1/emotions/batch-analyze`

#### Request
```json
{
  "class_id": "MATH-101-2026-01-04",
  "images_base64": [
    "data:image/jpeg;base64,/9j/4AAQ...",
    "data:image/jpeg;base64,/9j/4BBR..."
  ]
}
```

#### Proceso
- Analiza cada rostro detectado
- Calcula distribución emocional de la clase
- Genera métricas de engagement

---

## Fase 5: Reportes y Análisis

### 5.1 Reporte de Asistencia

#### Endpoint
**GET** `/api/v1/attendance/report/{class_id}`

#### Response
```json
{
  "success": true,
  "message": "Attendance report generated",
  "data": {
    "class_id": "MATH-101-2026-01-04",
    "class_name": "Matemáticas Avanzadas",
    "total_enrolled": 30,
    "present": 28,
    "absent": 2,
    "attendance_rate": 93.3,
    "students_present": [
      {
        "student_id": "STU-001",
        "name": "Juan Pérez",
        "time": "2026-01-04T08:15:00Z",
        "confidence": 0.95
      }
    ],
    "students_absent": [
      {
        "student_id": "STU-029",
        "name": "Carlos Ruiz"
      }
    ]
  }
}
```

### 5.2 Resumen Emocional

#### Endpoint
**GET** `/api/v1/emotions/class-summary/{class_id}`

#### Response
```json
{
  "success": true,
  "message": "Emotion summary generated",
  "data": {
    "class_id": "MATH-101-2026-01-04",
    "total_events": 150,
    "emotion_distribution": {
      "happy": 65,
      "neutral": 50,
      "confused": 20,
      "bored": 10,
      "frustrated": 5
    },
    "emotion_percentages": {
      "happy": 43.3,
      "neutral": 33.3,
      "confused": 13.3,
      "bored": 6.7,
      "frustrated": 3.3
    },
    "engagement_score": 76.6,
    "dominant_emotion": "happy",
    "average_confidence": 0.85
  }
}
```

### 5.3 Historial de Estudiante

#### Endpoint
**GET** `/api/v1/attendance/history/{student_id}`

#### Response
```json
{
  "success": true,
  "data": {
    "student_id": "STU-001",
    "total": 45,
    "records": [
      {
        "class_id": "MATH-101-2026-01-04",
        "status": "present",
        "timestamp": "2026-01-04T08:15:00Z"
      }
    ]
  }
}
```

---

## 🔄 Flujo Completo de una Clase

```
┌─────────────────────────────────────────────────────────────┐
│  ANTES DE LA CLASE                                          │
├─────────────────────────────────────────────────────────────┤
│  1. Registrar estudiantes (una sola vez)                    │
│     POST /api/v1/enrollment/enroll                          │
│                                                             │
│  2. Crear sesión de clase                                   │
│     POST /api/v1/classes/create                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  INICIO DE CLASE (08:00 - 08:15)                           │
├─────────────────────────────────────────────────────────────┤
│  3. Tomar asistencia                                        │
│     Opción A: Individual por estudiante                     │
│     POST /attendance/verify                                 │
│                                                             │
│     Opción B: Foto grupal                                   │
│     POST /attendance/batch-verify                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  DURANTE LA CLASE (cada 5-10 minutos)                      │
├─────────────────────────────────────────────────────────────┤
│  4. Capturar fotos de estudiantes                          │
│     POST /emotions/analyze                                  │
│                                                             │
│  5. Análisis emocional automático                          │
│     - Detecta: engagement, confusión, aburrimiento         │
│     - Guarda eventos en BD                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  FIN DE CLASE (opcional)                                    │
├─────────────────────────────────────────────────────────────┤
│  6. Generar reportes                                        │
│     GET /attendance/report/{class_id}                       │
│     GET /emotions/class-summary/{class_id}                  │
│                                                             │
│  7. Actualizar class_sessions                               │
│     UPDATE class_sessions SET                               │
│       end_time = NOW(),                                     │
│       present_count = ...,                                  │
│       attendance_rate = ...                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Pendientes / Mejoras

### Endpoints Existentes ✅
Todos los endpoints principales están implementados:
- ✅ **Enrollment** - Registro de estudiantes
- ✅ **Classes** - Gestión de sesiones
- ✅ **Attendance** - Toma de asistencia
- ✅ **Emotions** - Análisis emocional
- ✅ **Reports** - Reportes y análisis

### Optimizaciones Sugeridas
1. Caché de embeddings en Redis
2. Procesamiento asíncrono de imágenes con Celery
3. WebSocket para actualizaciones en tiempo real
4. Compresión de imágenes antes de subir a Storage
5. Paginación mejorada para listas grandes

---

## 📚 Referencias

- **DeepFace:** https://github.com/serengil/deepface
- **Supabase Storage:** https://supabase.com/docs/guides/storage
- **pgvector:** https://github.com/pgvector/pgvector
- **FastAPI:** https://fastapi.tiangolo.com/
