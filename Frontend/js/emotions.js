/**
 * Smart Classroom AI - Emotions Page
 * Manejo de análisis emocional en tiempo real
 */

let isCameraActive = false;
let emotionResults = [];
let currentMode = 'single';
let continuousInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    initEmotionsPage();
});

function initEmotionsPage() {
    const startCameraBtn = document.getElementById('startCameraBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const modeRadios = document.querySelectorAll('input[name="emotionMode"]');
    
    // Event listeners
    startCameraBtn.addEventListener('click', handleStartCamera);
    stopCameraBtn.addEventListener('click', handleStopCamera);
    analyzeBtn.addEventListener('click', handleAnalyzeEmotion);
    
    modeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentMode = e.target.value;
            if (currentMode === 'continuous' && isCameraActive) {
                startContinuousAnalysis();
            } else {
                stopContinuousAnalysis();
            }
        });
    });
}

async function handleStartCamera() {
    const video = document.getElementById('video');
    const startBtn = document.getElementById('startCameraBtn');
    const stopBtn = document.getElementById('stopCameraBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    try {
        await CameraUtils.initCamera(video);
        isCameraActive = true;
        
        // Actualizar UI
        video.style.display = 'block';
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-flex';
        analyzeBtn.disabled = false;
        
        UIUtils.showMessage('Cámara iniciada. Lista para analizar emociones.', 'success');
        
        // Si está en modo continuo, iniciar análisis automático
        if (currentMode === 'continuous') {
            startContinuousAnalysis();
        }
    } catch (error) {
        UIUtils.showMessage('Error al iniciar la cámara: ' + error.message, 'error');
    }
}

function handleStopCamera() {
    CameraUtils.stopCamera();
    stopContinuousAnalysis();
    isCameraActive = false;
    
    const video = document.getElementById('video');
    const startBtn = document.getElementById('startCameraBtn');
    const stopBtn = document.getElementById('stopCameraBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    // Actualizar UI
    video.style.display = 'none';
    startBtn.style.display = 'inline-flex';
    stopBtn.style.display = 'none';
    analyzeBtn.disabled = true;
}

async function handleAnalyzeEmotion() {
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
            await analyzeSingleEmotion(imageBase64);
        } else if (currentMode === 'batch') {
            await analyzeBatchEmotions([imageBase64]);
        }
    } catch (error) {
        APIUtils.handleAPIError(error);
    }
}

async function analyzeSingleEmotion(imageBase64) {
    const studentId = document.getElementById('studentIdEmotion').value.trim();
    const classId = document.getElementById('classIdEmotion').value.trim();
    
    try {
        UIUtils.showMessage('Analizando emoción...', 'info');
        
        // Construir URL con parámetros
        let url = `${APIUtils.API_CONFIG.ENDPOINTS.ANALYZE_EMOTION}?image_base64=${encodeURIComponent(imageBase64)}`;
        if (studentId) url += `&student_id=${encodeURIComponent(studentId)}`;
        if (classId) url += `&class_id=${encodeURIComponent(classId)}`;
        
        const response = await fetch(`${APIUtils.API_CONFIG.BASE_URL}${url}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success && result.data) {
            const emotionData = result.data;
            emotionResults.push(emotionData);
            
            displayEmotionResult(emotionData);
            updateEngagementMetrics();
            
            UIUtils.showMessage(
                `✅ Emoción detectada: ${emotionData.dominant_emotion} (${formatConfidence(emotionData.confidence)})`,
                'success'
            );
        } else {
            UIUtils.showMessage(result.message || 'Error en el análisis', 'error');
        }
    } catch (error) {
        APIUtils.handleAPIError(error);
    }
}

async function analyzeBatchEmotions(images) {
    const classId = document.getElementById('classIdEmotion').value.trim();
    
    if (!classId) {
        UIUtils.showMessage('Por favor ingresa el ID de la clase para análisis grupal', 'error');
        return;
    }
    
    const batchData = {
        images_base64: images,
        class_id: classId
    };
    
    try {
        UIUtils.showMessage('Analizando emociones grupales...', 'info');
        
        const response = await APIUtils.apiRequest(
            APIUtils.API_CONFIG.ENDPOINTS.BATCH_EMOTIONS,
            batchData
        );
        
        if (response.success && response.data) {
            const results = response.data.results || [];
            
            results.forEach(emotionData => {
                if (emotionData) {
                    emotionResults.push(emotionData);
                    displayEmotionResult(emotionData);
                }
            });
            
            updateEngagementMetrics();
            
            UIUtils.showMessage(
                `✅ Analizadas ${response.data.total_analyzed} emociones`,
                'success'
            );
        }
    } catch (error) {
        APIUtils.handleAPIError(error);
    }
}

function startContinuousAnalysis() {
    stopContinuousAnalysis(); // Limpiar cualquier intervalo previo
    
    UIUtils.showMessage('Iniciando monitoreo continuo de emociones...', 'info');
    
    // Analizar cada 3 segundos
    continuousInterval = setInterval(async () => {
        if (!isCameraActive) {
            stopContinuousAnalysis();
            return;
        }
        
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const imageBase64 = CameraUtils.captureImage(video, canvas);
        
        await analyzeSingleEmotion(imageBase64);
    }, 3000);
}

function stopContinuousAnalysis() {
    if (continuousInterval) {
        clearInterval(continuousInterval);
        continuousInterval = null;
    }
}

function displayEmotionResult(emotionData) {
    const resultsContainer = document.getElementById('emotionResults');
    
    // Remover mensaje de estado vacío si existe
    const emptyState = resultsContainer.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const emotionItem = document.createElement('div');
    emotionItem.className = 'emotion-item';
    
    const timestamp = new Date().toLocaleTimeString('es-ES');
    const emotionEmoji = getEmotionEmoji(emotionData.dominant_emotion);
    
    let emotionBarsHTML = '';
    if (emotionData.all_emotions) {
        emotionBarsHTML = '<div class="emotion-bars">';
        for (const [emotion, score] of Object.entries(emotionData.all_emotions)) {
            const percentage = (score * 100).toFixed(1);
            emotionBarsHTML += `
                <div class="emotion-bar">
                    <div class="emotion-bar-label">
                        <span>${getEmotionEmoji(emotion)} ${emotion}</span>
                        <span>${percentage}%</span>
                    </div>
                    <div class="emotion-bar-fill">
                        <div class="emotion-bar-value" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        }
        emotionBarsHTML += '</div>';
    }
    
    emotionItem.innerHTML = `
        <div class="emotion-header">
            <h4>${emotionEmoji} ${emotionData.dominant_emotion}</h4>
            <span class="result-badge badge-success">
                Confianza: ${formatConfidence(emotionData.confidence)}
            </span>
        </div>
        <p><small>${timestamp}</small></p>
        ${emotionBarsHTML}
    `;
    
    resultsContainer.insertBefore(emotionItem, resultsContainer.firstChild);
    
    // Limitar a 10 resultados mostrados
    while (resultsContainer.children.length > 10) {
        resultsContainer.removeChild(resultsContainer.lastChild);
    }
}

function updateEngagementMetrics() {
    if (emotionResults.length === 0) return;
    
    // Mostrar sección de métricas
    const metricsSection = document.getElementById('engagementMetrics');
    if (metricsSection) {
        metricsSection.style.display = 'grid';
    }
    
    // Calcular engagement score (basado en emociones positivas)
    const positiveEmotions = ['happy', 'surprise', 'neutral'];
    const positiveCount = emotionResults.filter(r => 
        positiveEmotions.includes(r.dominant_emotion.toLowerCase())
    ).length;
    
    const engagementScore = ((positiveCount / emotionResults.length) * 100).toFixed(1);
    
    // Encontrar emoción dominante general
    const emotionCounts = {};
    emotionResults.forEach(r => {
        const emotion = r.dominant_emotion;
        emotionCounts[emotion] = (emotionCounts[emotion] || 0) + 1;
    });
    
    const dominantEmotion = Object.keys(emotionCounts).reduce((a, b) => 
        emotionCounts[a] > emotionCounts[b] ? a : b
    );
    
    // Calcular confianza promedio
    const avgConfidence = emotionResults.reduce((sum, r) => 
        sum + (r.confidence || 0), 0
    ) / emotionResults.length;
    
    // Actualizar UI
    const scoreElement = document.getElementById('engagementScore');
    const dominantElement = document.getElementById('dominantEmotion');
    const confidenceElement = document.getElementById('avgConfidence');
    
    if (scoreElement) scoreElement.textContent = `${engagementScore}%`;
    if (dominantElement) {
        dominantElement.textContent = `${getEmotionEmoji(dominantEmotion)} ${dominantEmotion}`;
    }
    if (confidenceElement) {
        confidenceElement.textContent = formatConfidence(avgConfidence);
    }
}

function getEmotionEmoji(emotion) {
    const emojis = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'surprise': '😮',
        'fear': '😨',
        'disgust': '🤢',
        'neutral': '😐'
    };
    return emojis[emotion.toLowerCase()] || '😐';
}

function formatConfidence(confidence) {
    if (!confidence) return '-';
    return `${(confidence * 100).toFixed(1)}%`;
}
