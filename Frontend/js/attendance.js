/**
 * Smart Classroom AI - Attendance Page
 * Manejo de verificación de asistencia con reconocimiento facial
 */

let isCameraActive = false;
let recognizedStudents = [];
let currentMode = 'single';

document.addEventListener('DOMContentLoaded', () => {
    initAttendancePage();
});

function initAttendancePage() {
    const startCameraBtn = document.getElementById('startCameraBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    const verifyBtn = document.getElementById('verifyBtn');
    const modeRadios = document.querySelectorAll('input[name="mode"]');
    
    // Event listeners
    startCameraBtn.addEventListener('click', handleStartCamera);
    stopCameraBtn.addEventListener('click', handleStopCamera);
    verifyBtn.addEventListener('click', handleVerifyAttendance);
    
    modeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentMode = e.target.value;
        });
    });
}

async function handleStartCamera() {
    const video = document.getElementById('video');
    const startBtn = document.getElementById('startCameraBtn');
    const stopBtn = document.getElementById('stopCameraBtn');
    const verifyBtn = document.getElementById('verifyBtn');
    const cameraStatus = document.getElementById('cameraStatus');
    
    try {
        await CameraUtils.initCamera(video);
        isCameraActive = true;
        
        // Actualizar UI
        video.style.display = 'block';
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-flex';
        verifyBtn.disabled = false;
        cameraStatus.textContent = '📷 Cámara activa';
        cameraStatus.style.color = 'var(--success-color)';
        
        UIUtils.showMessage('Cámara iniciada. Lista para verificar asistencia.', 'success');
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
    const verifyBtn = document.getElementById('verifyBtn');
    const cameraStatus = document.getElementById('cameraStatus');
    
    // Actualizar UI
    video.style.display = 'none';
    startBtn.style.display = 'inline-flex';
    stopBtn.style.display = 'none';
    verifyBtn.disabled = true;
    cameraStatus.textContent = '📷 Cámara desactivada';
    cameraStatus.style.color = 'var(--text-light)';
}

async function handleVerifyAttendance() {
    const classId = document.getElementById('classId').value.trim();
    
    if (!classId) {
        UIUtils.showMessage('Por favor ingresa el ID de la clase', 'error');
        return;
    }
    
    if (!isCameraActive) {
        UIUtils.showMessage('Por favor inicia la cámara primero', 'error');
        return;
    }
    
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    
    try {
        // Capturar imagen
        const imageBase64 = CameraUtils.captureImage(video, canvas);
        
        if (currentMode === 'single') {
            await verifySingleAttendance(classId, imageBase64);
        } else {
            await verifyBatchAttendance(classId, [imageBase64]);
        }
    } catch (error) {
        APIUtils.handleAPIError(error);
    }
}

async function verifySingleAttendance(classId, imageBase64) {
    const verifyData = {
        class_id: classId,
        image_base64: imageBase64
    };
    
    try {
        UIUtils.showMessage('Verificando asistencia...', 'info');
        
        const response = await APIUtils.apiRequest(
            APIUtils.API_CONFIG.ENDPOINTS.VERIFY_ATTENDANCE,
            verifyData
        );
        
        if (response.success && response.data) {
            const result = response.data;
            
            if (result.recognized) {
                recognizedStudents.push(result);
                addAttendanceResult(result, true);
                updateRecognizedCount();
                UIUtils.showMessage(
                    `✅ Asistencia verificada: ${result.student_name || result.student_id}`,
                    'success'
                );
            } else {
                addAttendanceResult(result, false);
                UIUtils.showMessage('❌ No se reconoció ningún estudiante', 'error');
            }
        } else {
            UIUtils.showMessage(response.message || 'Error en la verificación', 'error');
        }
    } catch (error) {
        APIUtils.handleAPIError(error);
    }
}

async function verifyBatchAttendance(classId, images) {
    const batchData = {
        class_id: classId,
        images: images
    };
    
    try {
        UIUtils.showMessage('Verificando asistencia grupal...', 'info');
        
        const response = await APIUtils.apiRequest(
            APIUtils.API_CONFIG.ENDPOINTS.BATCH_ATTENDANCE,
            batchData
        );
        
        if (response.success && response.data) {
            const results = response.data.results || [];
            
            results.forEach(result => {
                if (result.recognized) {
                    recognizedStudents.push(result);
                    addAttendanceResult(result, true);
                } else {
                    addAttendanceResult(result, false);
                }
            });
            
            updateRecognizedCount();
            UIUtils.showMessage(
                `✅ Procesadas ${response.data.total_images} imágenes. ` +
                `Reconocidos: ${response.data.recognized_count}`,
                'success'
            );
        }
    } catch (error) {
        APIUtils.handleAPIError(error);
    }
}

function addAttendanceResult(result, success) {
    const resultsContainer = document.getElementById('attendanceResults');
    
    // Remover mensaje de estado vacío si existe
    const emptyState = resultsContainer.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    
    const timestamp = new Date().toLocaleTimeString('es-ES');
    
    if (success) {
        resultItem.innerHTML = `
            <div class="result-info">
                <strong>${result.student_name || result.student_id}</strong>
                <p>ID: ${result.student_id} | Confianza: ${formatConfidence(result.confidence)}</p>
                <small>${timestamp}</small>
            </div>
            <span class="result-badge badge-success">✅ Verificado</span>
        `;
    } else {
        resultItem.innerHTML = `
            <div class="result-info">
                <strong>No reconocido</strong>
                <p>${result.message || 'No se encontró coincidencia'}</p>
                <small>${timestamp}</small>
            </div>
            <span class="result-badge badge-error">❌ Fallido</span>
        `;
    }
    
    resultsContainer.insertBefore(resultItem, resultsContainer.firstChild);
}

function updateRecognizedCount() {
    const countElement = document.getElementById('recognizedCount');
    const counterDiv = document.getElementById('verificationCount');
    
    if (countElement && counterDiv) {
        countElement.textContent = recognizedStudents.length;
        counterDiv.style.display = 'block';
    }
}

function formatConfidence(confidence) {
    if (!confidence) return '-';
    return `${(confidence * 100).toFixed(1)}%`;
}
