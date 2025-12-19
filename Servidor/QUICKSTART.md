# Smart Classroom AI - Quick Start Guide

## 🚀 Inicio Rápido (5 minutos)

### 1. Instalación Express
```bash
# Clonar repo
git clone <repo-url>
cd ProyectoCasaAbierta

# Crear venv e instalar
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# EDITAR: SUPABASE_URL, SUPABASE_KEY, SECRET_KEY
```

### 2. Setup Base de Datos
```bash
# Ejecutar script
python app/db/init_db.py

# Copiar el SQL output
# Ir a Supabase → SQL Editor → Pegar y ejecutar
```

### 3. Ejecutar
```bash
python app/main.py

# Abrir: http://localhost:8080/api/v1/docs
```

## 📝 Primer Uso

### A. Registrar Estudiante
```python
import requests
import base64

# Leer imagen
with open("student_photo.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

# Enroll
response = requests.post("http://localhost:8080/api/v1/enrollment/enroll", json={
    "student_id": "2024001",
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "image_base64": f"data:image/jpeg;base64,{image_b64}"
})

print(response.json())
```

### B. Verificar Asistencia
```python
# Capturar foto en clase
with open("classroom_frame.jpg", "rb") as f:
    frame_b64 = base64.b64encode(f.read()).decode()

# Verificar
response = requests.post("http://localhost:8080/api/v1/attendance/verify", json={
    "class_id": "CS101-2024-01-15",
    "image_base64": f"data:image/jpeg;base64,{frame_b64}"
})

result = response.json()
if result["data"]["success"]:
    print(f"✓ Asistencia verificada: {result['data']['student_name']}")
    print(f"  Confidence: {result['data']['confidence']:.2%}")
```

### C. Analizar Emoción
```python
response = requests.post("http://localhost:8080/api/v1/emotions/analyze", json={
    "image_base64": f"data:image/jpeg;base64,{frame_b64}",
    "student_id": "2024001",
    "class_id": "CS101-2024-01-15"
})

emotion = response.json()["data"]
print(f"Emoción dominante: {emotion['dominant_emotion']}")
print(f"Confidence: {emotion['confidence']:.1f}%")
```

## 🔧 Troubleshooting Rápido

### Error: "Face not detected"
- Asegúrate que la imagen tenga buena iluminación
- El rostro debe estar de frente
- Tamaño mínimo: 80x80 pixels

### Error: "Database connection failed"
- Verifica SUPABASE_URL y SUPABASE_KEY en .env
- Verifica que las tablas estén creadas

### Error: "ModuleNotFoundError: deepface"
- Ejecuta: `pip install deepface`
- Si falla con TensorFlow: `pip install tensorflow==2.15.0`

## 📊 Monitoreo

### Health Check
```bash
curl http://localhost:8080/health
```

### Ver Logs
```bash
# En consola se muestran automáticamente
# Para guardar en archivo:
python app/main.py > logs/app.log 2>&1
```

## 🎯 Próximos Pasos
1. Lee el [README.md](README.md) completo
2. Revisa la documentación interactiva: http://localhost:8080/api/v1/docs
3. Explora los ejemplos en `tests/` (cuando estén disponibles)
