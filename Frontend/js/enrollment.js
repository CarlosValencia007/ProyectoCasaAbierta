/**
 * Smart Classroom AI - Enrollment Page
 * Manejo de registro de estudiantes con captura de foto
 */

let isCameraActive = false;
let capturedImageBase64 = null;

document.addEventListener('DOMContentLoaded', () => {
    initEnrollmentPage();
});

function initEnrollmentPage() {
    const startCameraBtn = document.getElementById('startCameraBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    const captureBtn = document.getElementById('captureBtn');
    const retakeBtn = document.getElementById('retakeBtn');
    const enrollForm = document.getElementById('enrollmentForm');
    const enrollBtn = document.getElementById('enrollBtn');
    
    // Event listeners
    startCameraBtn.addEventListener('click', handleStartCamera);
    stopCameraBtn.addEventListener('click', handleStopCamera);
    captureBtn.addEventListener('click', handleCapture);
    retakeBtn.addEventListener('click', handleRetake);
    enrollForm.addEventListener('submit', handleEnrollSubmit);
}

async function handleStartCamera() {
    const video = document.getElementById('video');
    const startBtn = document.getElementById('startCameraBtn');
    const stopBtn = document.getElementById('stopCameraBtn');
    const captureBtn = document.getElementById('captureBtn');
    
    try {
        await CameraUtils.initCamera(video);
        isCameraActive = true;
        
        // Actualizar UI
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-flex';
        captureBtn.disabled = false;
        video.style.display = 'block';
        
        UIUtils.showMessage('Cámara iniciada correctamente', 'success');
    } catch (error) {
        UIUtils.showMessage('Error al iniciar la cámara: ' + error.message, 'error');
    }
}

function handleStopCamera() {
    CameraUtils.stopCamera();
    isCameraActive = false;
    
    const video = document.getElementById('video');
    const startBtn = document.getElementById('startCameraBtn');
    const stopBtn = document.getElementById('stopCameraBtn');
    const captureBtn = document.getElementById('captureBtn');
    
    // Actualizar UI
    video.style.display = 'none';
    startBtn.style.display = 'inline-flex';
    stopBtn.style.display = 'none';
    captureBtn.disabled = true;
}

function handleCapture() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const capturedImage = document.getElementById('capturedImage');
    const captureBtn = document.getElementById('captureBtn');
    const retakeBtn = document.getElementById('retakeBtn');
    const enrollBtn = document.getElementById('enrollBtn');
    
    try {
        // Capturar imagen
        capturedImageBase64 = CameraUtils.captureImage(video, canvas);
        
        // Mostrar imagen capturada
        capturedImage.src = `data:image/jpeg;base64,${capturedImageBase64}`;
        capturedImage.style.display = 'block';
        video.style.display = 'none';
        
        // Detener cámara
        CameraUtils.stopCamera();
        isCameraActive = false;
        
        // Actualizar UI
        captureBtn.style.display = 'none';
        retakeBtn.style.display = 'inline-flex';
        document.getElementById('stopCameraBtn').style.display = 'none';
        enrollBtn.disabled = false;
        
        UIUtils.showMessage('Foto capturada exitosamente', 'success');
    } catch (error) {
        UIUtils.showMessage('Error al capturar la imagen: ' + error.message, 'error');
    }
}

function handleRetake() {
    const video = document.getElementById('video');
    const capturedImage = document.getElementById('capturedImage');
    const startBtn = document.getElementById('startCameraBtn');
    const captureBtn = document.getElementById('captureBtn');
    const retakeBtn = document.getElementById('retakeBtn');
    const enrollBtn = document.getElementById('enrollBtn');
    
    // Limpiar imagen capturada
    capturedImageBase64 = null;
    capturedImage.style.display = 'none';
    capturedImage.src = '';
    
    // Actualizar UI
    video.style.display = 'block';
    startBtn.style.display = 'inline-flex';
    captureBtn.style.display = 'inline-flex';
    captureBtn.disabled = true;
    retakeBtn.style.display = 'none';
    enrollBtn.disabled = true;
}

async function handleEnrollSubmit(event) {
    event.preventDefault();
    
    const studentId = document.getElementById('studentId').value.trim();
    const studentName = document.getElementById('studentName').value.trim();
    const studentEmail = document.getElementById('studentEmail').value.trim();
    const metadataText = document.getElementById('metadata').value.trim();
    
    // Validaciones
    if (!studentId || !studentName) {
        UIUtils.showMessage('Por favor completa los campos requeridos', 'error');
        return;
    }
    
    if (!capturedImageBase64) {
        UIUtils.showMessage('Por favor captura una foto del estudiante', 'error');
        return;
    }
    
    // Preparar metadata
    let metadata = null;
    if (metadataText) {
        try {
            metadata = JSON.parse(metadataText);
        } catch (error) {
            UIUtils.showMessage('El formato de metadata debe ser JSON válido', 'error');
            return;
        }
    }
    
    // Preparar datos para la API
    const enrollData = {
        student_id: studentId,
        name: studentName,
        image_base64: capturedImageBase64,
        email: studentEmail || null,
        metadata: metadata
    };
    
    try {
        UIUtils.showMessage('Registrando estudiante...', 'info');
        
        const response = await APIUtils.apiRequest(
            APIUtils.API_CONFIG.ENDPOINTS.ENROLLMENT,
            enrollData
        );
        
        if (response.success) {
            UIUtils.showMessage(
                `✅ Estudiante ${studentName} registrado exitosamente con ID: ${studentId}`,
                'success'
            );
            
            // Limpiar formulario
            document.getElementById('enrollmentForm').reset();
            capturedImageBase64 = null;
            document.getElementById('capturedImage').style.display = 'none';
            document.getElementById('enrollBtn').disabled = true;
            
            // Mostrar datos adicionales si están disponibles
            if (response.data) {
                console.log('Datos de respuesta:', response.data);
            }
        } else {
            UIUtils.showMessage(`Error: ${response.message}`, 'error');
        }
    } catch (error) {
        APIUtils.handleAPIError(error);
    }
}
