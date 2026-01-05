/**
 * Smart Classroom AI - Utility Functions
 * Funciones comunes para manejo de cámara, API calls, y utilidades
 */

// Configuración de la API
const API_CONFIG = {
    BASE_URL: 'http://localhost:8080',
    ENDPOINTS: {
        ENROLLMENT: '/api/v1/enrollment/enroll',
        UPDATE_PHOTO: '/api/v1/enrollment/update-photo',
        VERIFY_ATTENDANCE: '/api/v1/attendance/verify',
        BATCH_ATTENDANCE: '/api/v1/attendance/batch-verify',
        ANALYZE_EMOTION: '/api/v1/emotions/analyze',
        BATCH_EMOTIONS: '/api/v1/emotions/batch-analyze',
        HEALTH: '/health'
    }
};

// Variables globales para la cámara
let currentStream = null;
let videoElement = null;
let canvasElement = null;

/**
 * Inicializa la cámara
 * @param {HTMLVideoElement} video - Elemento de video
 * @returns {Promise<MediaStream>}
 */
async function initCamera(video) {
    try {
        videoElement = video;
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            }
        };
        
        currentStream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = currentStream;
        
        return currentStream;
    } catch (error) {
        console.error('Error al acceder a la cámara:', error);
        showMessage('No se pudo acceder a la cámara. Verifica los permisos.', 'error');
        throw error;
    }
}

/**
 * Detiene la cámara
 */
function stopCamera() {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
    }
    if (videoElement) {
        videoElement.srcObject = null;
    }
}

/**
 * Captura una imagen del video
 * @param {HTMLVideoElement} video - Elemento de video
 * @param {HTMLCanvasElement} canvas - Elemento canvas
 * @returns {string} - Imagen en base64
 */
function captureImage(video, canvas) {
    if (!canvas) {
        canvas = document.createElement('canvas');
    }
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Retorna la imagen en formato base64 sin el prefijo "data:image/jpeg;base64,"
    const imageData = canvas.toDataURL('image/jpeg', 0.95);
    return imageData.split(',')[1];
}

/**
 * Convierte un archivo a base64
 * @param {File} file - Archivo a convertir
 * @returns {Promise<string>}
 */
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

/**
 * Realiza una petición a la API
 * @param {string} endpoint - Endpoint de la API
 * @param {Object} data - Datos a enviar
 * @param {string} method - Método HTTP (POST, GET, etc.)
 * @returns {Promise<Object>}
 */
async function apiRequest(endpoint, data = null, method = 'POST') {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`;
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    try {
        showSpinner(true);
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Error en la petición');
        }
        
        return result;
    } catch (error) {
        console.error('Error en la petición:', error);
        throw error;
    } finally {
        showSpinner(false);
    }
}

/**
 * Muestra un mensaje al usuario
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de mensaje (success, error, info)
 */
function showMessage(message, type = 'info') {
    const messageBox = document.getElementById('responseMessage');
    if (!messageBox) return;
    
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`;
    messageBox.style.display = 'block';
    
    // Ocultar después de 5 segundos
    setTimeout(() => {
        messageBox.style.display = 'none';
    }, 5000);
}

/**
 * Muestra u oculta el spinner de carga
 * @param {boolean} show - Mostrar u ocultar
 */
function showSpinner(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = show ? 'block' : 'none';
    }
}

/**
 * Valida una imagen base64
 * @param {string} base64 - Imagen en base64
 * @returns {boolean}
 */
function validateImageBase64(base64) {
    if (!base64 || base64.length < 100) {
        return false;
    }
    return true;
}

/**
 * Formatea una fecha
 * @param {string|Date} date - Fecha a formatear
 * @returns {string}
 */
function formatDate(date) {
    if (!date) return '-';
    const d = new Date(date);
    return d.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Formatea un porcentaje
 * @param {number} value - Valor decimal (0-1)
 * @returns {string}
 */
function formatPercentage(value) {
    return `${(value * 100).toFixed(1)}%`;
}

/**
 * Descarga datos como archivo CSV
 * @param {Array} data - Array de objetos
 * @param {string} filename - Nombre del archivo
 */
function downloadCSV(data, filename) {
    if (!data || data.length === 0) {
        showMessage('No hay datos para exportar', 'error');
        return;
    }
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => {
            const value = row[header];
            return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
        }).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

/**
 * Verifica el estado de salud de la API
 * @returns {Promise<boolean>}
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.HEALTH}`);
        return response.ok;
    } catch (error) {
        console.error('API no disponible:', error);
        return false;
    }
}

/**
 * Inicializa el chequeo de salud de la API al cargar la página
 */
document.addEventListener('DOMContentLoaded', async () => {
    const isHealthy = await checkAPIHealth();
    if (!isHealthy) {
        showMessage('⚠️ El servidor no está disponible. Verifica que esté ejecutándose en http://localhost:8000', 'error');
    }
});

/**
 * Maneja errores de la API
 * @param {Error} error - Error capturado
 */
function handleAPIError(error) {
    console.error('Error de API:', error);
    
    let message = 'Error al procesar la solicitud';
    if (error.message.includes('fetch')) {
        message = 'No se pudo conectar con el servidor. Verifica que esté ejecutándose.';
    } else {
        message = error.message;
    }
    
    showMessage(message, 'error');
}

/**
 * Genera un ID único
 * @returns {string}
 */
function generateUniqueId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Dibuja un rectángulo en el canvas para indicar detección de rostro
 * @param {HTMLCanvasElement} canvas - Canvas donde dibujar
 * @param {Object} faceBox - Coordenadas del rostro {x, y, width, height}
 * @param {string} label - Etiqueta a mostrar
 * @param {string} color - Color del rectángulo
 */
function drawFaceBox(canvas, faceBox, label, color = '#4F46E5') {
    const ctx = canvas.getContext('2d');
    
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.strokeRect(faceBox.x, faceBox.y, faceBox.width, faceBox.height);
    
    // Dibuja la etiqueta
    ctx.fillStyle = color;
    ctx.fillRect(faceBox.x, faceBox.y - 30, faceBox.width, 30);
    
    ctx.fillStyle = 'white';
    ctx.font = '16px Arial';
    ctx.fillText(label, faceBox.x + 5, faceBox.y - 8);
}

/**
 * Redimensiona una imagen base64
 * @param {string} base64 - Imagen en base64
 * @param {number} maxWidth - Ancho máximo
 * @param {number} maxHeight - Alto máximo
 * @returns {Promise<string>}
 */
function resizeImage(base64, maxWidth = 800, maxHeight = 600) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            let width = img.width;
            let height = img.height;
            
            if (width > maxWidth || height > maxHeight) {
                const ratio = Math.min(maxWidth / width, maxHeight / height);
                width *= ratio;
                height *= ratio;
            }
            
            canvas.width = width;
            canvas.height = height;
            
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);
            
            const resizedBase64 = canvas.toDataURL('image/jpeg', 0.9).split(',')[1];
            resolve(resizedBase64);
        };
        img.src = `data:image/jpeg;base64,${base64}`;
    });
}

// Exportar funciones globalmente
window.CameraUtils = {
    initCamera,
    stopCamera,
    captureImage
};

window.APIUtils = {
    apiRequest,
    checkAPIHealth,
    handleAPIError,
    API_CONFIG
};

window.UIUtils = {
    showMessage,
    showSpinner,
    drawFaceBox
};

window.DataUtils = {
    fileToBase64,
    validateImageBase64,
    formatDate,
    formatPercentage,
    downloadCSV,
    generateUniqueId,
    resizeImage
};
