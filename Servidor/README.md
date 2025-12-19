# 🎓 Smart Classroom AI

> **AI-Powered Classroom Attendance & Emotion Analysis System**

Sistema inteligente de asistencia y análisis emocional para aulas de clase mediante Biometría Facial (DeepFace) y Análisis de Estado Emocional en tiempo real.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com)
[![DeepFace](https://img.shields.io/badge/DeepFace-0.0.87-orange.svg)](https://github.com/serengil/deepface)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green.svg)](https://supabase.com)

---

## 📋 Tabla de Contenidos

- [Visión del Proyecto](#-visión-del-proyecto)
- [Arquitectura Técnica](#-arquitectura-técnica)
- [Flujo de Datos](#-flujo-de-datos)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Setup e Instalación](#-setup-e-instalación)
- [Endpoints de la API](#-endpoints-de-la-api)
- [Guía de Desarrollo](#-guía-de-desarrollo)
- [Deployment](#-deployment)
- [Contribución](#-contribución)

---

## 🎯 Visión del Proyecto

### Objetivos
El sistema **Smart Classroom AI** combina **reconocimiento facial** y **análisis emocional** para:

1. ✅ **Validar asistencia automáticamente** usando biometría facial (DeepFace + Facenet)
2. 📊 **Analizar el estado emocional** de los estudiantes (Aburrimiento, Felicidad, Sueño, etc.)
3. 📈 **Generar reportes de engagement** para que los profesores mejoren la calidad de las clases
4. 🚀 **Procesamiento en tiempo real** con soporte multi-rostro

### MVP Features
- ✅ **Enrollment**: Registro de estudiantes con foto → Vector → DB
- ✅ **Verificación**: Asistencia en tiempo real con soporte multi-rostro
- ✅ **Análisis Emocional**: Detección de 7+ emociones durante la clase
- ✅ **Reportes**: Generación de reportes de asistencia y engagement

---

## 🏗️ Arquitectura Técnica

### Arquitectura Híbrida: "Cerebro" + "Memoria"

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│              React/Vue + WebRTC (Video Capture)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Python + FastAPI)                   │
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐                  │
│  │  Face Service   │    │  Emotion Service │                  │
│  │  (DeepFace)     │    │  (DeepFace)      │                  │
│  │  - Embeddings   │    │  - 7 Emotions    │                  │
│  │  - Recognition  │    │  - Confidence    │                  │
│  └─────────────────┘    └──────────────────┘                  │
│                                                                 │
│  ┌─────────────────────────────────────────────┐              │
│  │         Business Logic Services             │              │
│  │  • EnrollmentService                        │              │
│  │  • AttendanceService                        │              │
│  │  • EmotionAnalysisService                   │              │
│  └─────────────────────────────────────────────┘              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPABASE (BaaS)                              │
│                                                                 │
│  ┌─────────────────────────────────────────┐                  │
│  │  PostgreSQL + pgvector Extension        │                  │
│  │  - Vector Similarity Search (Embeddings)│                  │
│  │  - CRUD Operations                       │                  │
│  │  - RPC Functions (Optimized Queries)     │                  │
│  └─────────────────────────────────────────┘                  │
│                                                                 │
│  ┌─────────────────────────────────────────┐                  │
│  │  Edge Functions (Deno)                  │                  │
│  │  - Report Generation (Excel)            │                  │
│  │  - Email Notifications                   │                  │
│  └─────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

### Stack Tecnológico

| Componente | Tecnología | Propósito |
|------------|-----------|-----------|
| **Backend Core** | Python 3.9+ | Lenguaje principal |
| **API Framework** | FastAPI | REST API con validación automática |
| **AI/ML** | DeepFace | Reconocimiento facial y emociones |
| **Face Recognition** | Facenet | Generación de embeddings (128-dim) |
| **Computer Vision** | OpenCV | Procesamiento de imágenes |
| **Database** | Supabase (PostgreSQL) | Almacenamiento persistente |
| **Vector Search** | pgvector | Búsqueda de similitud de embeddings |
| **Containerization** | Docker | Despliegue consistente |
| **Cloud Platform** | Google Cloud Run | Serverless deployment |

---

## 🔄 Flujo de Datos Principal

### 1️⃣ Pipeline de Enrollment
```
1. Frontend captura foto del estudiante
2. Envía imagen (base64) → POST /api/v1/enrollment/enroll
3. Backend:
   - Valida imagen
   - DeepFace genera embedding (128 dimensiones)
4. Guarda en Supabase:
   - Tabla: students
   - Columna: face_embedding (vector(128))
5. Retorna confirmación
```

### 2️⃣ Pipeline de Verificación de Asistencia
```
1. Frontend captura frame de video
2. Envía → POST /api/v1/attendance/verify
3. Backend:
   - DeepFace genera embedding del rostro
   - Consulta pgvector: similitud euclidiana
   - SQL: SELECT * WHERE face_embedding <-> query < 0.6
4. Si match:
   - Marca asistencia en tabla "attendance"
   - Retorna info del estudiante + confidence
5. Frontend muestra confirmación
```

### 3️⃣ Pipeline de Análisis Emocional
```
1. Durante la clase: captura frames periódicos
2. POST /api/v1/emotions/analyze
3. DeepFace analiza emociones:
   - happy, sad, angry, fear, surprise, neutral, disgust
4. Guarda en tabla "emotion_events"
5. Agregación para reportes de engagement
```

---

## 📁 Estructura del Proyecto

```
ProyectoCasaAbierta/
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   │
│   ├── core/                      # Configuración y utilidades
│   │   ├── __init__.py
│   │   ├── config.py              # Settings (Pydantic)
│   │   ├── logger.py              # Logging configuration
│   │   ├── constants.py           # Enums y constantes
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── schemas.py             # Pydantic models
│   │
│   ├── db/                        # Capa de base de datos
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── supabase_client.py    # Cliente Supabase
│   │   ├── crud.py                # Operaciones CRUD
│   │   └── init_db.py             # SQL scripts para setup
│   │
│   ├── services/                  # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── face_service.py        # DeepFace wrapper
│   │   ├── enrollment_service.py  # Enrollment logic
│   │   └── attendance_service.py  # Attendance logic
│   │
│   └── api/                       # Endpoints REST
│       ├── __init__.py
│       ├── health.py              # Health checks
│       ├── enrollment.py          # Enrollment endpoints
│       ├── attendance.py          # Attendance endpoints
│       └── emotions.py            # Emotion analysis endpoints
│
├── weights/                       # Modelos pre-entrenados (DeepFace)
├── uploads/                       # Temporal image storage
│
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container image
├── .env.example                   # Environment variables template
├── .gitignore
├── .dockerignore
└── README.md
```

---

## 🚀 Setup e Instalación

### Prerrequisitos
- Python 3.9+
- PostgreSQL (o cuenta Supabase)
- Docker (opcional, para deployment)
- Git

### 1. Clonar el Repositorio
```bash
git clone https://github.com/Noobex1608/ProyectoCasaAbierta.git
cd ProyectoCasaAbierta
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
# Copiar template
cp .env.example .env

# Editar .env con tus credenciales
# IMPORTANTE: Actualizar SUPABASE_URL, SUPABASE_KEY, DATABASE_URL
```

### 5. Setup de Base de Datos (Supabase)

**Opción A: Supabase Dashboard**
1. Ir a [Supabase Dashboard](https://app.supabase.com)
2. Crear nuevo proyecto
3. Ir a SQL Editor
4. Ejecutar el script en `app/db/init_db.py`

**Opción B: CLI**
```bash
python app/db/init_db.py
# Copiar el SQL output y ejecutarlo en Supabase SQL Editor
```

### 6. Ejecutar el Servidor
```bash
# Desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# O directamente
python app/main.py
```

### 7. Verificar Instalación
```bash
# Health check
curl http://localhost:8080/health

# Documentación interactiva
open http://localhost:8080/api/v1/docs
```

---

## 📡 Endpoints de la API

### Base URL: `http://localhost:8080/api/v1`

### 🏥 Health & Info
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API info |
| GET | `/info` | System configuration |

### 👤 Enrollment
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/enrollment/enroll` | Registrar nuevo estudiante |
| PUT | `/enrollment/update-photo/{student_id}` | Actualizar foto |
| GET | `/enrollment/student/{student_id}` | Obtener info de estudiante |
| GET | `/enrollment/students` | Listar todos los estudiantes |

**Ejemplo - Enroll Student:**
```bash
curl -X POST "http://localhost:8080/api/v1/enrollment/enroll" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "2024001",
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQ..."
  }'
```

### ✅ Attendance
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/attendance/verify` | Verificar asistencia (single) |
| POST | `/attendance/batch-verify` | Verificación batch |
| GET | `/attendance/report/{class_id}` | Reporte de clase |
| GET | `/attendance/history/{student_id}` | Historial de estudiante |

**Ejemplo - Verify Attendance:**
```bash
curl -X POST "http://localhost:8080/api/v1/attendance/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": "CS101-2024-01-15",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQ..."
  }'
```

### 😊 Emotion Analysis
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/emotions/analyze` | Analizar emoción (single) |
| POST | `/emotions/batch-analyze` | Análisis batch |
| GET | `/emotions/class-summary/{class_id}` | Resumen emocional de clase |
| GET | `/emotions/student-timeline/{student_id}` | Timeline de estudiante |

---

## 👨‍💻 Guía de Desarrollo

### Flujo de Trabajo Kanban

#### Board Sugerido (Jira/Trello):
```
Backlog → To Do → In Progress → Code Review → Testing → Done
```

#### Distribución de Equipo (10 desarrolladores)

**Backend Team (7 devs):**
- **Dev 1-2**: Core Services (Face Recognition, Emotion Analysis)
- **Dev 3-4**: API Endpoints (Enrollment, Attendance)
- **Dev 5**: Database Layer (CRUD, Migrations)
- **Dev 6**: Integration & Testing
- **Dev 7**: DevOps & Deployment

**Frontend Team (3 devs):**
- **Dev 1**: Dashboard & Reporting UI
- **Dev 2**: Real-time Camera Capture (WebRTC)
- **Dev 3**: Integration & UX Polish

### Convenciones de Código

#### Python (PEP 8)
```python
# Imports
from typing import List, Dict
from app.core.logger import logger

# Type hints
def process_image(image: np.ndarray) -> List[float]:
    """Process image and return embedding"""
    pass

# Async cuando sea posible
async def verify_student(student_id: str) -> Dict[str, Any]:
    result = await student_crud.find_by_id(student_id)
    return result
```

#### Git Workflow
```bash
# Feature branch
git checkout -b feature/emotion-analysis-batch

# Commits descriptivos
git commit -m "feat(emotions): add batch analysis endpoint"
git commit -m "fix(attendance): handle null confidence values"
git commit -m "docs(readme): update API examples"

# Pull request
git push origin feature/emotion-analysis-batch
```

### Testing
```bash
# Unit tests
pytest tests/test_face_service.py

# Integration tests
pytest tests/test_api_enrollment.py

# Coverage
pytest --cov=app tests/
```

---

## 🐳 Deployment

### Docker Build & Run
```bash
# Build image
docker build -t smart-classroom-ai:latest .

# Run container
docker run -d \
  -p 8080:8080 \
  --env-file .env \
  --name smart-classroom \
  smart-classroom-ai:latest

# Check logs
docker logs -f smart-classroom
```

### Google Cloud Run
```bash
# 1. Build & push
gcloud builds submit --tag gcr.io/PROJECT_ID/smart-classroom-ai

# 2. Deploy
gcloud run deploy smart-classroom-ai \
  --image gcr.io/PROJECT_ID/smart-classroom-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="ENVIRONMENT=production"
```

### Configuración de Producción
```env
# .env (production)
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Security
SECRET_KEY=<STRONG_RANDOM_KEY>

# Thresholds (ajustar según necesidad)
FACE_MATCH_THRESHOLD=0.55  # Más estricto en producción
EMOTION_CONFIDENCE_THRESHOLD=0.75
```

---

## 📊 Esquema de Base de Datos

### Tabla: `students`
```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    face_embedding vector(128) NOT NULL,  -- pgvector
    enrolled_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    extra_data TEXT
);

CREATE INDEX ix_students_face_embedding 
ON students USING ivfflat (face_embedding vector_l2_ops);
```

### Tabla: `attendance`
```sql
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) REFERENCES students(student_id),
    class_id VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'present',
    timestamp TIMESTAMP DEFAULT NOW(),
    confidence FLOAT,
    match_distance FLOAT
);
```

### Tabla: `emotion_events`
```sql
CREATE TABLE emotion_events (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(50) REFERENCES students(student_id),
    class_id VARCHAR(100) NOT NULL,
    dominant_emotion VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    emotion_scores TEXT,  -- JSON
    detected_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🤝 Contribución

### Proceso
1. Fork el repositorio
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

### Code Review Checklist
- [ ] Tests unitarios incluidos
- [ ] Documentación actualizada
- [ ] Logs apropiados
- [ ] Manejo de errores
- [ ] Type hints en funciones públicas
- [ ] No hay hardcoded credentials

---

## 📝 Licencia

Este proyecto es privado y confidencial. Propiedad de [Tu Organización].

---

## 📧 Contacto

**Equipo de Desarrollo:**
- Tech Lead: [Nombre] - [email]
- Backend Lead: [Nombre] - [email]
- Frontend Lead: [Nombre] - [email]

**Issues & Soporte:**
- GitHub Issues: [repo-url]/issues
- Slack: #smart-classroom-dev

---

## 🎯 Roadmap

### Fase 1 (Mes 1) - MVP ✅
- [x] Backend API completo
- [x] Enrollment & Attendance
- [x] Emotion Analysis
- [ ] Frontend básico
- [ ] Tests unitarios

### Fase 2 (Mes 2) - Mejoras
- [ ] Dashboard avanzado
- [ ] Reportes automáticos (Excel/PDF)
- [ ] Notificaciones por email
- [ ] Optimización de performance

### Fase 3 (Mes 3) - Producción
- [ ] Deployment en Cloud Run
- [ ] CI/CD pipeline
- [ ] Monitoreo (Prometheus/Grafana)
- [ ] Documentación completa

---

**Built with ❤️ by Smart Classroom Team**