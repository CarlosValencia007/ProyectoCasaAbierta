# 🎥 Smart Classroom AI - Demo y Testing

Este documento proporciona ejemplos de uso y casos de prueba para el frontend.

## 📋 Casos de Prueba

### 1. Enrollment (Registro de Estudiantes)

#### Test Case 1: Registro Exitoso
```
Datos:
- ID: EST001
- Nombre: Juan Pérez García
- Email: juan.perez@ejemplo.com
- Metadata: {"carrera": "Ingeniería", "semestre": 5}

Resultado Esperado:
✅ Estudiante registrado exitosamente
```

#### Test Case 2: Registro sin Email
```
Datos:
- ID: EST002
- Nombre: María García López
- Email: (vacío)
- Metadata: (vacío)

Resultado Esperado:
✅ Estudiante registrado exitosamente (email y metadata son opcionales)
```

#### Test Case 3: Error - Campos Vacíos
```
Datos:
- ID: (vacío)
- Nombre: (vacío)

Resultado Esperado:
❌ Error: "Por favor completa los campos requeridos"
```

#### Test Case 4: Error - Sin Foto
```
Datos:
- ID: EST003
- Nombre: Carlos López
- Foto: No capturada

Resultado Esperado:
❌ Error: "Por favor captura una foto del estudiante"
```

#### Test Case 5: Metadata Inválida
```
Datos:
- ID: EST004
- Nombre: Ana Martínez
- Metadata: {carrera: Ingeniería} (JSON inválido)

Resultado Esperado:
❌ Error: "El formato de metadata debe ser JSON válido"
```

### 2. Attendance (Verificación de Asistencia)

#### Test Case 1: Verificación Individual Exitosa
```
Datos:
- Class ID: CLASE-2025-001
- Modo: Individual
- Usuario: Previamente registrado

Resultado Esperado:
✅ Asistencia verificada con nombre, ID y confianza
```

#### Test Case 2: Estudiante No Reconocido
```
Datos:
- Class ID: CLASE-2025-001
- Modo: Individual
- Usuario: No registrado

Resultado Esperado:
❌ "No se reconoció ningún estudiante"
```

#### Test Case 3: Verificación sin Class ID
```
Datos:
- Class ID: (vacío)

Resultado Esperado:
❌ Error: "Por favor ingresa el ID de la clase"
```

#### Test Case 4: Modo Grupal
```
Datos:
- Class ID: CLASE-2025-002
- Modo: Grupal
- Usuarios: Múltiples rostros en la imagen

Resultado Esperado:
✅ Procesadas X imágenes, Y reconocidos
```

### 3. Emotions (Análisis Emocional)

#### Test Case 1: Análisis Individual
```
Datos:
- Modo: Individual
- Expresión: Sonriendo

Resultado Esperado:
✅ Emoción: happy con alta confianza (>70%)
```

#### Test Case 2: Análisis con IDs
```
Datos:
- Student ID: EST001
- Class ID: CLASE-2025-001
- Modo: Individual

Resultado Esperado:
✅ Emoción detectada y guardada en BD
```

#### Test Case 3: Modo Continuo
```
Datos:
- Modo: Continuo
- Duración: 30 segundos

Resultado Esperado:
✅ Múltiples análisis automáticos cada 3 segundos
✅ Métricas actualizadas continuamente
```

#### Test Case 4: Cambio de Emociones
```
Secuencia:
1. Expresión neutral → Resultado: neutral
2. Sonreír → Resultado: happy
3. Fruncir el ceño → Resultado: angry/sad

Resultado Esperado:
✅ Sistema detecta cambios en tiempo real
```

### 4. Dashboard

#### Test Case 1: Carga Inicial
```
Acción: Abrir dashboard

Resultado Esperado:
✅ Métricas generales mostradas
✅ Gráficos renderizados
✅ Datos de ejemplo cargados
```

#### Test Case 2: Exportación CSV
```
Acción: Click en "Exportar Asistencia"

Resultado Esperado:
✅ Archivo CSV descargado
✅ Mensaje de confirmación
```

## 🎬 Flujos de Demostración

### Flujo 1: Demo Completa (5 minutos)

1. **Inicio** (30 seg)
   - Mostrar página principal
   - Explicar las 4 funcionalidades principales

2. **Enrollment** (1 min)
   - Registrar estudiante de prueba
   - Mostrar captura de foto
   - Confirmar registro exitoso

3. **Attendance** (1.5 min)
   - Verificar asistencia del estudiante registrado
   - Mostrar reconocimiento facial
   - Ver historial de verificaciones

4. **Emotions** (1.5 min)
   - Analizar emoción actual
   - Cambiar expresión facial
   - Mostrar modo continuo
   - Ver distribución de emociones

5. **Dashboard** (30 seg)
   - Mostrar métricas generales
   - Explicar gráficos
   - Exportar datos

### Flujo 2: Demo Técnica (10 minutos)

1. **Arquitectura** (2 min)
   - Explicar comunicación Frontend-Backend
   - Mostrar estructura de archivos
   - Revisar configuración de API

2. **Enrollment Técnico** (2 min)
   - Mostrar captura de imagen con Canvas
   - Explicar conversión a Base64
   - Ver request/response en DevTools

3. **Attendance Técnico** (2 min)
   - Explicar proceso de reconocimiento
   - Mostrar confianza de matching
   - Ver logs del servidor

4. **Emotions Técnico** (2 min)
   - Explicar modelo DeepFace
   - Mostrar scores de cada emoción
   - Calcular engagement score

5. **Integración** (2 min)
   - Mostrar endpoints de la API
   - Explicar manejo de errores
   - Ver documentación de Swagger

### Flujo 3: Demo para Cliente (3 minutos)

1. **Problema** (30 seg)
   - Asistencia manual toma tiempo
   - Difícil medir engagement de estudiantes
   - No hay datos objetivos

2. **Solución** (1 min)
   - Registro facial automático
   - Verificación en segundos
   - Análisis emocional en tiempo real

3. **Beneficios** (1 min)
   - Ahorro de tiempo (90%)
   - Datos precisos y objetivos
   - Mejora de calidad educativa

4. **Demo en Vivo** (30 seg)
   - Verificación de asistencia
   - Análisis emocional rápido

## 🧪 Pruebas de Calidad

### Pruebas de Usabilidad

1. **Navegación**
   - ✓ Menú funciona correctamente
   - ✓ Links llevan a páginas correctas
   - ✓ Botón atrás del navegador funciona

2. **Formularios**
   - ✓ Validación de campos
   - ✓ Mensajes de error claros
   - ✓ Feedback visual al usuario

3. **Cámara**
   - ✓ Se solicitan permisos correctamente
   - ✓ Video se muestra sin delay
   - ✓ Captura funciona consistentemente

### Pruebas de Rendimiento

1. **Tiempo de Carga**
   - ✓ Página principal < 1 segundo
   - ✓ Assets se cargan correctamente

2. **Tiempo de Respuesta**
   - ✓ Enrollment: < 3 segundos
   - ✓ Attendance: < 2 segundos
   - ✓ Emotions: < 2 segundos

3. **Uso de Recursos**
   - ✓ Memoria < 100MB
   - ✓ CPU < 30% durante análisis

### Pruebas de Compatibilidad

1. **Navegadores**
   - ✓ Chrome 120+
   - ✓ Firefox 120+
   - ✓ Edge 120+
   - ✓ Safari 17+

2. **Resoluciones**
   - ✓ 1920x1080 (Full HD)
   - ✓ 1366x768 (HD)
   - ✓ 768x1024 (Tablet)
   - ⚠️ 375x667 (Mobile - limitado)

3. **Sistemas Operativos**
   - ✓ Windows 10/11
   - ✓ macOS 13+
   - ✓ Linux (Ubuntu 22.04+)

## 📸 Mejores Prácticas para Captura

### Iluminación
- ✅ Luz frontal suave
- ✅ Evitar contraluz
- ✅ Luz natural o LED blanca
- ❌ Luz muy fuerte o sombras duras

### Posición
- ✅ Rostro centrado
- ✅ Distancia: 50cm - 1m
- ✅ Mirada a la cámara
- ❌ Rostro de lado o inclinado

### Fondo
- ✅ Fondo uniforme
- ✅ Contraste con el rostro
- ❌ Fondo muy ocupado
- ❌ Otras personas en el fondo

### Accesorios
- ✅ Sin gafas (preferible)
- ⚠️ Gafas transparentes (aceptable)
- ❌ Lentes oscuros
- ❌ Gorras o sombreros

## 🎯 KPIs del Sistema

### Métricas de Éxito

1. **Tasa de Reconocimiento**
   - Objetivo: > 95%
   - Medición: Estudiantes reconocidos / Total de intentos

2. **Tiempo Promedio de Verificación**
   - Objetivo: < 2 segundos
   - Medición: Desde captura hasta confirmación

3. **Precisión de Emociones**
   - Objetivo: > 80%
   - Medición: Confianza promedio del modelo

4. **Engagement Score**
   - Objetivo: > 70%
   - Medición: % de emociones positivas

5. **Satisfacción del Usuario**
   - Objetivo: > 4/5
   - Medición: Encuesta post-uso

## 🐛 Bugs Conocidos

### Menores
- Dashboard usa datos mock (no conectado a BD)
- Modo batch no implementado completamente en frontend
- Exportación PDF pendiente

### En Corrección
- Ninguno actualmente

## 🔮 Próximas Features

1. **Corto Plazo (1-2 semanas)**
   - Integración completa con endpoints de reportes
   - Mejoras en UI/UX responsive
   - Modo oscuro

2. **Mediano Plazo (1 mes)**
   - Sistema de autenticación
   - Historial de sesiones
   - Notificaciones en tiempo real

3. **Largo Plazo (3 meses)**
   - PWA (Progressive Web App)
   - Modo offline
   - Machine Learning en el navegador

## 📞 Contacto para Feedback

Si encuentras algún problema o tienes sugerencias:
- Documentar el bug con pasos para reproducir
- Incluir capturas de pantalla
- Especificar navegador y versión
- Enviar logs de la consola (F12)

---

**Última actualización:** Diciembre 2025
