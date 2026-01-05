# 🎓 Smart Classroom AI - Frontend

Frontend básico para el sistema de asistencia inteligente con reconocimiento facial y análisis emocional.

## 📁 Estructura del Proyecto

```
Frontend/
├── index.html              # Página principal
├── enrollment.html         # Registro de estudiantes
├── attendance.html         # Verificación de asistencia
├── emotions.html           # Análisis emocional
├── dashboard.html          # Dashboard con reportes
├── css/
│   └── styles.css          # Estilos globales
└── js/
    ├── utils.js            # Utilidades comunes
    ├── enrollment.js       # Lógica de enrollment
    ├── attendance.js       # Lógica de attendance
    ├── emotions.js         # Lógica de emotions
    └── dashboard.js        # Lógica de dashboard
```

## 🚀 Inicio Rápido

### Prerrequisitos

1. **Servidor Backend ejecutándose** en `http://localhost:8000`
   ```bash
   cd ProyectoCasaAbierta/Servidor
   python -m uvicorn app.main:app --reload
   ```

2. **Navegador web moderno** con soporte para:
   - WebRTC (acceso a cámara)
   - Canvas API
   - ES6+ JavaScript

### Instalación

1. **Opción 1: Abrir directamente con Live Server (VS Code)**
   - Instala la extensión "Live Server" en VS Code
   - Haz clic derecho en `index.html`
   - Selecciona "Open with Live Server"

2. **Opción 2: Usar Python HTTP Server**
   ```bash
   cd Frontend
   python -m http.server 8080
   ```
   Luego abre: `http://localhost:8080`

3. **Opción 3: Abrir directamente el archivo**
   - Haz doble clic en `index.html`
   - Nota: Algunas funciones pueden no funcionar por restricciones CORS

## 📖 Guía de Uso

### 1. 👤 Enrollment (Registro de Estudiantes)

**Flujo:**
1. Navega a la página "Enrollment"
2. Completa el formulario:
   - ID del Estudiante (requerido)
   - Nombre Completo (requerido)
   - Email (opcional)
   - Metadata en formato JSON (opcional)
3. Haz clic en "Iniciar Cámara"
4. Posiciona tu rostro frente a la cámara
5. Haz clic en "Capturar Foto"
6. Revisa la foto capturada
7. Haz clic en "Registrar Estudiante"

**Endpoints utilizados:**
- `POST /enrollment/enroll`

**Consejos:**
- Asegúrate de tener buena iluminación
- Mira directamente a la cámara
- Evita accesorios que cubran el rostro
- El rostro debe estar centrado

### 2. ✅ Attendance (Verificación de Asistencia)

**Flujo:**
1. Navega a la página "Attendance"
2. Ingresa el ID de la clase (ej: `CLASE-2025-001`)
3. Selecciona el modo:
   - **Modo Individual**: Verifica un estudiante a la vez
   - **Modo Grupal**: Puede detectar múltiples rostros
4. Haz clic en "Iniciar Cámara"
5. Haz clic en "Verificar Asistencia"
6. Observa los resultados en tiempo real

**Endpoints utilizados:**
- `POST /attendance/verify` (modo individual)
- `POST /attendance/batch-verify` (modo grupal)

**Características:**
- Reconocimiento facial en tiempo real
- Contador de estudiantes reconocidos
- Historial de verificaciones
- Confianza de reconocimiento

### 3. 😊 Emotions (Análisis Emocional)

**Flujo:**
1. Navega a la página "Emotions"
2. (Opcional) Ingresa ID de clase y estudiante
3. Selecciona el modo de análisis:
   - **Individual**: Un análisis por clic
   - **Grupal**: Múltiples rostros
   - **Continuo**: Análisis automático cada 3 segundos
4. Haz clic en "Iniciar Cámara"
5. Haz clic en "Analizar Emociones"
6. Observa las emociones detectadas

**Endpoints utilizados:**
- `POST /emotions/analyze` (análisis individual)
- `POST /emotions/batch-analyze` (análisis grupal)

**Emociones detectadas:**
- 😊 Feliz (happy)
- 😢 Triste (sad)
- 😠 Enojado (angry)
- 😮 Sorprendido (surprise)
- 😨 Temeroso (fear)
- 🤢 Disgusto (disgust)
- 😐 Neutral (neutral)

**Métricas calculadas:**
- Engagement Score (% emociones positivas)
- Emoción dominante
- Confianza promedio

### 4. 📊 Dashboard (Reportes)

**Flujo:**
1. Navega a la página "Dashboard"
2. Los datos se cargan automáticamente
3. Filtra por clase o período (opcional)
4. Haz clic en "Actualizar" para refrescar
5. Exporta reportes en CSV

**Características:**
- Métricas generales (estudiantes, asistencias, tasa)
- Gráficos de distribución emocional
- Tendencias de asistencia
- Estudiantes recientes
- Alertas de engagement
- Exportación de datos

**Nota:** Actualmente el dashboard usa datos de ejemplo. En producción se conectaría a endpoints específicos del backend.

## 🔧 Configuración

### Cambiar URL del Backend

Edita el archivo `js/utils.js`:

```javascript
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',  // Cambia esta URL
    // ...
};
```

### Ajustar Calidad de Imagen

En `js/utils.js`, modifica la función `captureImage`:

```javascript
const imageData = canvas.toDataURL('image/jpeg', 0.95);  // 0.95 = 95% calidad
```

### Intervalo de Análisis Continuo

En `js/emotions.js`, ajusta el intervalo:

```javascript
continuousInterval = setInterval(async () => {
    // ...
}, 3000);  // Milisegundos (3000 = 3 segundos)
```

## 🎨 Personalización

### Colores

Edita las variables CSS en `css/styles.css`:

```css
:root {
    --primary-color: #4F46E5;      /* Azul principal */
    --secondary-color: #06B6D4;    /* Cyan */
    --success-color: #10B981;      /* Verde */
    --danger-color: #EF4444;       /* Rojo */
    --warning-color: #F59E0B;      /* Amarillo */
}
```

### Estilos

Todos los estilos están centralizados en `css/styles.css`. El diseño es responsive y se adapta a diferentes tamaños de pantalla.

## 🔒 Permisos de Cámara

El navegador solicitará permiso para acceder a la cámara. Asegúrate de:

1. **Permitir el acceso** cuando se solicite
2. Si usas HTTPS, los permisos son más seguros
3. En HTTP local (`localhost`), generalmente funciona sin problemas

**Solución de problemas:**
- Chrome: Configuración → Privacidad → Configuración de sitio → Cámara
- Firefox: Configuración → Privacidad y seguridad → Permisos → Cámara
- Edge: Configuración → Permisos del sitio → Cámara

## 📱 Compatibilidad

### Navegadores Soportados
- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Edge 79+
- ✅ Safari 11+
- ✅ Opera 47+

### Dispositivos
- ✅ Computadoras de escritorio
- ✅ Laptops
- ✅ Tablets
- ✅ Smartphones (con limitaciones de UI)

## 🐛 Solución de Problemas

### Error: "No se pudo conectar con el servidor"
- Verifica que el backend esté ejecutándose en `http://localhost:8000`
- Prueba acceder a `http://localhost:8000/health` en el navegador

### Error: "No se pudo acceder a la cámara"
- Verifica los permisos del navegador
- Asegúrate de que ninguna otra aplicación esté usando la cámara
- Intenta reiniciar el navegador

### La imagen no se captura correctamente
- Espera a que el video esté completamente cargado
- Asegúrate de tener buena iluminación
- Verifica que el navegador soporte Canvas API

### CORS Error
- Asegúrate de que el backend tenga configurado CORS correctamente
- El backend debe permitir `http://localhost` en los orígenes

## 🚧 Limitaciones Conocidas

1. **Dashboard**: Actualmente usa datos de ejemplo (mock data)
2. **Batch Processing**: Limitado a una imagen a la vez en el frontend
3. **Exportación PDF**: No implementada (solo CSV disponible)
4. **Persistencia**: No hay almacenamiento local de datos
5. **Autenticación**: No implementada en esta versión MVP

## 🔜 Mejoras Futuras

- [ ] Integración completa con endpoints de reportes del backend
- [ ] Almacenamiento local con IndexedDB
- [ ] Sistema de autenticación de usuarios
- [ ] Exportación de reportes en PDF
- [ ] Modo oscuro
- [ ] Internacionalización (i18n)
- [ ] PWA (Progressive Web App)
- [ ] WebSocket para actualizaciones en tiempo real
- [ ] Historial de sesiones

## 📄 Licencia

Este proyecto es parte del MVP de Smart Classroom AI.

## 🤝 Contribución

Para contribuir:
1. Haz un fork del proyecto
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Envía un pull request

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:
- Abre un issue en el repositorio
- Contacta al equipo de desarrollo

---

**Nota:** Este es un frontend básico para MVP. Para producción se recomienda usar frameworks modernos como React, Vue o Angular.
