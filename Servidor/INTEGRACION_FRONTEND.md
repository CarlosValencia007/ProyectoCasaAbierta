# Guía de Integración Frontend - Smart Classroom AI

## 🎯 Configuración Inicial

### 1. URL Base del API
```javascript
const API_BASE_URL = "http://localhost:8080/api/v1";
const HEALTH_URL = "http://localhost:8080/health";
```

### 2. Headers Recomendados
```javascript
const headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};
```

---

## 📝 Flujo Completo: Paso a Paso

### PASO 1: Verificar que el Backend está corriendo

```javascript
// Health Check
async function checkBackendHealth() {
  try {
    const response = await fetch('http://localhost:8080/health');
    const data = await response.json();
    console.log('Backend Status:', data.status);
    console.log('Services:', data.services);
    return data.status === 'healthy';
  } catch (error) {
    console.error('Backend no disponible:', error);
    return false;
  }
}
```

---

### PASO 2: Registrar Estudiantes (Una sola vez)

```javascript
async function enrollStudent(studentData, imageFile) {
  // Convertir imagen a base64
  const base64Image = await fileToBase64(imageFile);
  
  const payload = {
    student_id: studentData.studentId,
    name: studentData.name,
    email: studentData.email, // opcional
    image_base64: base64Image
  };
  
  const response = await fetch(`${API_BASE_URL}/enrollment/enroll`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log('Estudiante registrado:', result.data);
    console.log('Foto URL:', result.data.photo_url);
    return result.data;
  } else {
    throw new Error(result.message);
  }
}

// Función helper para convertir File a base64
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      // Eliminar el prefijo "data:image/jpeg;base64,"
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = error => reject(error);
  });
}
```

**Ejemplo de uso en React:**
```jsx
function EnrollmentForm() {
  const [studentData, setStudentData] = useState({
    studentId: '',
    name: '',
    email: ''
  });
  const [photo, setPhoto] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const result = await enrollStudent(studentData, photo);
      alert(`Estudiante ${result.name} registrado exitosamente!`);
      console.log('URL de foto:', result.photo_url);
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="text" 
        placeholder="ID del estudiante"
        value={studentData.studentId}
        onChange={(e) => setStudentData({...studentData, studentId: e.target.value})}
      />
      <input 
        type="text" 
        placeholder="Nombre completo"
        value={studentData.name}
        onChange={(e) => setStudentData({...studentData, name: e.target.value})}
      />
      <input 
        type="file" 
        accept="image/*"
        onChange={(e) => setPhoto(e.target.files[0])}
      />
      <button type="submit">Registrar Estudiante</button>
    </form>
  );
}
```

---

### PASO 3: Crear Sesión de Clase

```javascript
async function createClassSession(classData) {
  const payload = {
    class_id: classData.classId,           // Ej: "MATH-101-2026-01-04"
    class_name: classData.className,       // Ej: "Matemáticas Avanzadas"
    instructor: classData.instructor,      // Ej: "Prof. García"
    room: classData.room,                  // Ej: "Aula 301"
    start_time: new Date().toISOString(),  // Timestamp actual
    metadata: {
      subject: classData.subject,
      level: classData.level
    }
  };
  
  const response = await fetch(`${API_BASE_URL}/classes/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log('Clase creada:', result.data);
    return result.data;
  } else {
    throw new Error(result.message);
  }
}
```

**Ejemplo React:**
```jsx
function CreateClassForm() {
  const handleCreateClass = async () => {
    const classSession = await createClassSession({
      classId: `MATH-101-${new Date().toISOString().split('T')[0]}`,
      className: "Matemáticas Avanzadas",
      instructor: "Prof. García",
      room: "Aula 301",
      subject: "Mathematics",
      level: "Advanced"
    });
    
    // Guardar class_id para usar en asistencia y emociones
    localStorage.setItem('currentClassId', classSession.class_id);
  };
  
  return <button onClick={handleCreateClass}>Iniciar Clase</button>;
}
```

---

### PASO 4: Tomar Asistencia

#### Opción A: Asistencia Individual

```javascript
async function verifyAttendance(classId, imageFile) {
  const base64Image = await fileToBase64(imageFile);
  
  const payload = {
    class_id: classId,
    image_base64: base64Image
  };
  
  const response = await fetch(`${API_BASE_URL}/attendance/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log('Estudiante identificado:', result.data);
    return {
      studentId: result.data.student_id,
      name: result.data.name,
      confidence: result.data.confidence,
      status: result.data.status
    };
  } else {
    throw new Error(result.message);
  }
}
```

**Ejemplo con cámara web:**
```jsx
function AttendanceCapture() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [classId, setClassId] = useState('');
  const [results, setResults] = useState([]);
  
  useEffect(() => {
    // Obtener class_id guardado
    setClassId(localStorage.getItem('currentClassId'));
    
    // Iniciar cámara
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        videoRef.current.srcObject = stream;
      });
  }, []);
  
  const captureAndVerify = async () => {
    // Capturar frame de la cámara
    const canvas = canvasRef.current;
    const video = videoRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    // Convertir canvas a blob
    canvas.toBlob(async (blob) => {
      const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
      
      try {
        const result = await verifyAttendance(classId, file);
        setResults(prev => [...prev, result]);
        alert(`¡Bienvenido ${result.name}!`);
      } catch (error) {
        alert('No se pudo identificar al estudiante');
      }
    }, 'image/jpeg');
  };
  
  return (
    <div>
      <video ref={videoRef} autoPlay />
      <canvas ref={canvasRef} style={{display: 'none'}} />
      <button onClick={captureAndVerify}>Tomar Asistencia</button>
      
      <h3>Asistentes:</h3>
      <ul>
        {results.map((r, i) => (
          <li key={i}>{r.name} - Confianza: {(r.confidence * 100).toFixed(0)}%</li>
        ))}
      </ul>
    </div>
  );
}
```

#### Opción B: Asistencia Masiva

```javascript
async function batchVerifyAttendance(classId, imageFiles) {
  // Convertir todas las imágenes a base64
  const base64Images = await Promise.all(
    imageFiles.map(file => fileToBase64(file))
  );
  
  const payload = {
    class_id: classId,
    images: base64Images
  };
  
  const response = await fetch(`${API_BASE_URL}/attendance/batch-verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const result = await response.json();
  return result.data;
}
```

---

### PASO 5: Analizar Emociones

```javascript
async function analyzeEmotion(classId, imageFile, studentId = null) {
  const base64Image = await fileToBase64(imageFile);
  
  const payload = {
    image_base64: base64Image,
    class_id: classId,
    student_id: studentId // opcional
  };
  
  const response = await fetch(`${API_BASE_URL}/emotions/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const result = await response.json();
  
  if (result.success) {
    return {
      dominantEmotion: result.data.dominant_emotion,
      confidence: result.data.confidence,
      allEmotions: result.data.all_emotions
    };
  }
}
```

**Ejemplo con monitoreo periódico:**
```jsx
function EmotionMonitor() {
  const [emotions, setEmotions] = useState([]);
  const classId = localStorage.getItem('currentClassId');
  
  useEffect(() => {
    // Capturar emoción cada 30 segundos
    const interval = setInterval(async () => {
      const capture = await captureFromCamera();
      const emotion = await analyzeEmotion(classId, capture);
      
      setEmotions(prev => [...prev, {
        time: new Date(),
        emotion: emotion.dominantEmotion,
        confidence: emotion.confidence
      }]);
    }, 30000); // 30 segundos
    
    return () => clearInterval(interval);
  }, [classId]);
  
  return (
    <div>
      <h3>Monitoreo Emocional</h3>
      {emotions.map((e, i) => (
        <div key={i}>
          {e.time.toLocaleTimeString()} - {e.emotion} ({(e.confidence * 100).toFixed(0)}%)
        </div>
      ))}
    </div>
  );
}
```

---

### PASO 6: Obtener Reportes

#### Reporte de Asistencia

```javascript
async function getAttendanceReport(classId) {
  const response = await fetch(
    `${API_BASE_URL}/attendance/report/${classId}`
  );
  const result = await response.json();
  
  if (result.success) {
    return {
      totalEnrolled: result.data.total_enrolled,
      present: result.data.present,
      absent: result.data.absent,
      attendanceRate: result.data.attendance_rate,
      studentsPresent: result.data.students_present,
      studentsAbsent: result.data.students_absent
    };
  }
}
```

#### Resumen Emocional

```javascript
async function getEmotionSummary(classId) {
  const response = await fetch(
    `${API_BASE_URL}/emotions/class-summary/${classId}`
  );
  const result = await response.json();
  
  if (result.success) {
    return {
      emotionDistribution: result.data.emotion_distribution,
      emotionPercentages: result.data.emotion_percentages,
      engagementScore: result.data.engagement_score,
      dominantEmotion: result.data.dominant_emotion
    };
  }
}
```

**Ejemplo de Dashboard:**
```jsx
function ClassDashboard() {
  const [attendanceReport, setAttendanceReport] = useState(null);
  const [emotionSummary, setEmotionSummary] = useState(null);
  const classId = localStorage.getItem('currentClassId');
  
  useEffect(() => {
    const loadReports = async () => {
      const attendance = await getAttendanceReport(classId);
      const emotions = await getEmotionSummary(classId);
      
      setAttendanceReport(attendance);
      setEmotionSummary(emotions);
    };
    
    loadReports();
  }, [classId]);
  
  return (
    <div>
      <h2>Dashboard de Clase</h2>
      
      {attendanceReport && (
        <div>
          <h3>Asistencia</h3>
          <p>Presentes: {attendanceReport.present} / {attendanceReport.totalEnrolled}</p>
          <p>Tasa: {attendanceReport.attendanceRate}%</p>
        </div>
      )}
      
      {emotionSummary && (
        <div>
          <h3>Engagement</h3>
          <p>Score: {emotionSummary.engagementScore}%</p>
          <p>Emoción Dominante: {emotionSummary.dominantEmotion}</p>
        </div>
      )}
    </div>
  );
}
```

---

### PASO 7: Listar Estudiantes

```javascript
async function getStudents() {
  const response = await fetch(`${API_BASE_URL}/enrollment/students`);
  const result = await response.json();
  
  if (result.success) {
    return result.data.students;
  }
}
```

**Ejemplo:**
```jsx
function StudentList() {
  const [students, setStudents] = useState([]);
  
  useEffect(() => {
    getStudents().then(setStudents);
  }, []);
  
  return (
    <div>
      <h2>Estudiantes Registrados</h2>
      <div className="student-grid">
        {students.map(student => (
          <div key={student.student_id} className="student-card">
            {student.photo_url && (
              <img src={student.photo_url} alt={student.name} />
            )}
            <h3>{student.name}</h3>
            <p>ID: {student.student_id}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🔧 Configuración de CORS

El backend ya está configurado para aceptar peticiones desde:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)

Si usas otro puerto, agrégalo al archivo `.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:4200
```

---

## 📦 Estructura de Respuestas

Todas las respuestas siguen este formato:

```json
{
  "success": true|false,
  "message": "Descripción del resultado",
  "data": { /* datos específicos */ }
}
```

---

## ⚠️ Manejo de Errores

```javascript
async function apiCall(url, options) {
  try {
    const response = await fetch(url, options);
    const result = await response.json();
    
    if (!result.success) {
      throw new Error(result.message);
    }
    
    return result.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}
```

---

## 🚀 Checklist de Integración

- [ ] Backend corriendo en `http://localhost:8080`
- [ ] Health check exitoso
- [ ] Registrar al menos 2-3 estudiantes de prueba
- [ ] Crear una sesión de clase
- [ ] Probar toma de asistencia individual
- [ ] Probar análisis emocional
- [ ] Ver reportes en el frontend

---

## 📝 Notas Importantes

1. **Tamaño de Imágenes**: Recomendado < 2MB
2. **Formato**: JPG o PNG
3. **Rostros**: Una cara clara y frontal por imagen
4. **Iluminación**: Buena iluminación para mejor reconocimiento
5. **Timeout**: Considera 10-15 segundos para análisis

---

## 🐛 Troubleshooting

**Error CORS:**
```
Verifica que el frontend esté corriendo en un puerto configurado en CORS_ORIGINS
```

**Error 422:**
```
Verifica que el formato de los datos sea correcto según los schemas
```

**Error "No face detected":**
```
Asegúrate de que la imagen tenga un rostro visible y bien iluminado
```

**Backend lento en primera petición:**
```
Es normal, DeepFace descarga modelos en el primer uso (~500MB)
```
