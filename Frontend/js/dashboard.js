/**
 * Smart Classroom AI - Dashboard Page
 * Visualización de reportes y estadísticas
 */

let allData = {
    students: [],
    attendance: [],
    emotions: []
};

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    loadDashboardData();
});

function initDashboard() {
    const refreshBtn = document.getElementById('refreshBtn');
    const exportAttendanceBtn = document.getElementById('exportAttendanceBtn');
    const exportEmotionsBtn = document.getElementById('exportEmotionsBtn');
    const exportFullReportBtn = document.getElementById('exportFullReportBtn');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadDashboardData);
    }
    
    if (exportAttendanceBtn) {
        exportAttendanceBtn.addEventListener('click', exportAttendanceData);
    }
    
    if (exportEmotionsBtn) {
        exportEmotionsBtn.addEventListener('click', exportEmotionsData);
    }
    
    if (exportFullReportBtn) {
        exportFullReportBtn.addEventListener('click', exportFullReport);
    }
}

async function loadDashboardData() {
    UIUtils.showMessage('Cargando datos del dashboard...', 'info');
    
    try {
        // En un escenario real, aquí harías peticiones a endpoints específicos
        // Por ahora, generaremos datos de ejemplo para demostración
        
        // Simular datos para demostración
        allData = generateMockData();
        
        updateMetricsOverview();
        updateAttendanceByClass();
        updateEmotionDistribution();
        updateAttendanceTrend();
        updateRecentStudents();
        updateEngagementAlerts();
        
        UIUtils.showMessage('Dashboard actualizado correctamente', 'success');
    } catch (error) {
        APIUtils.handleAPIError(error);
    }
}

function generateMockData() {
    // Datos de ejemplo para demostración
    const students = [
        { id: 'EST001', name: 'Juan Pérez', email: 'juan@ejemplo.com', enrolled_date: '2025-01-15' },
        { id: 'EST002', name: 'María García', email: 'maria@ejemplo.com', enrolled_date: '2025-01-15' },
        { id: 'EST003', name: 'Carlos López', email: 'carlos@ejemplo.com', enrolled_date: '2025-01-16' },
        { id: 'EST004', name: 'Ana Martínez', email: 'ana@ejemplo.com', enrolled_date: '2025-01-16' },
        { id: 'EST005', name: 'Luis Rodríguez', email: 'luis@ejemplo.com', enrolled_date: '2025-01-17' }
    ];
    
    const attendance = [
        { student_id: 'EST001', class_id: 'CLASE-001', date: '2025-01-20', verified: true },
        { student_id: 'EST002', class_id: 'CLASE-001', date: '2025-01-20', verified: true },
        { student_id: 'EST003', class_id: 'CLASE-001', date: '2025-01-20', verified: true },
        { student_id: 'EST001', class_id: 'CLASE-002', date: '2025-01-21', verified: true },
        { student_id: 'EST004', class_id: 'CLASE-002', date: '2025-01-21', verified: true }
    ];
    
    const emotions = [
        { emotion: 'happy', count: 45, percentage: 0.35 },
        { emotion: 'neutral', count: 40, percentage: 0.31 },
        { emotion: 'surprise', count: 20, percentage: 0.16 },
        { emotion: 'sad', count: 15, percentage: 0.12 },
        { emotion: 'angry', count: 8, percentage: 0.06 }
    ];
    
    return { students, attendance, emotions };
}

function updateMetricsOverview() {
    const totalStudentsEl = document.getElementById('totalStudents');
    const todayAttendanceEl = document.getElementById('todayAttendance');
    const attendanceRateEl = document.getElementById('attendanceRate');
    const engagementScoreEl = document.getElementById('engagementScore');
    
    if (totalStudentsEl) {
        totalStudentsEl.textContent = allData.students.length;
    }
    
    if (todayAttendanceEl) {
        const today = new Date().toISOString().split('T')[0];
        const todayCount = allData.attendance.filter(a => a.date.startsWith(today)).length;
        todayAttendanceEl.textContent = todayCount;
    }
    
    if (attendanceRateEl) {
        const rate = allData.students.length > 0 
            ? (allData.attendance.length / (allData.students.length * 2)) * 100 
            : 0;
        attendanceRateEl.textContent = `${rate.toFixed(1)}%`;
    }
    
    if (engagementScoreEl) {
        const positiveEmotions = allData.emotions.filter(e => 
            ['happy', 'surprise', 'neutral'].includes(e.emotion)
        );
        const totalPositive = positiveEmotions.reduce((sum, e) => sum + e.count, 0);
        const totalEmotions = allData.emotions.reduce((sum, e) => sum + e.count, 0);
        const score = totalEmotions > 0 ? (totalPositive / totalEmotions) * 100 : 0;
        engagementScoreEl.textContent = `${score.toFixed(1)}%`;
    }
}

function updateAttendanceByClass() {
    const container = document.getElementById('attendanceByClass');
    if (!container) return;
    
    // Agrupar asistencia por clase
    const classCounts = {};
    allData.attendance.forEach(a => {
        classCounts[a.class_id] = (classCounts[a.class_id] || 0) + 1;
    });
    
    container.innerHTML = '';
    
    if (Object.keys(classCounts).length === 0) {
        container.innerHTML = '<p class="empty-state">No hay datos de asistencia</p>';
        return;
    }
    
    Object.entries(classCounts).forEach(([classId, count]) => {
        const item = document.createElement('div');
        item.className = 'data-item';
        item.innerHTML = `
            <strong>${classId}</strong>
            <p>${count} estudiantes verificados</p>
        `;
        container.appendChild(item);
    });
}

function updateEmotionDistribution() {
    const canvas = document.getElementById('emotionPieChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Verificar si Chart.js está disponible
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js no está cargado');
        return;
    }
    
    const labels = allData.emotions.map(e => e.emotion);
    const data = allData.emotions.map(e => e.count);
    const colors = [
        '#FCD34D', // happy
        '#9CA3AF', // neutral
        '#F472B6', // surprise
        '#60A5FA', // sad
        '#EF4444'  // angry
    ];
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: false
                }
            }
        }
    });
}

function updateAttendanceTrend() {
    const canvas = document.getElementById('attendanceLineChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Verificar si Chart.js está disponible
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js no está cargado');
        return;
    }
    
    // Generar datos de tendencia por fecha
    const attendanceByDate = {};
    allData.attendance.forEach(a => {
        const date = a.date.split(' ')[0];
        attendanceByDate[date] = (attendanceByDate[date] || 0) + 1;
    });
    
    const dates = Object.keys(attendanceByDate).sort();
    const counts = dates.map(date => attendanceByDate[date]);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Asistencias',
                data: counts,
                borderColor: '#4F46E5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function updateRecentStudents() {
    const container = document.getElementById('recentStudents');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (allData.students.length === 0) {
        container.innerHTML = '<p class="empty-state">No hay estudiantes registrados</p>';
        return;
    }
    
    // Mostrar últimos 5 estudiantes
    const recentStudents = allData.students.slice(-5).reverse();
    
    recentStudents.forEach(student => {
        const item = document.createElement('div');
        item.className = 'data-item';
        item.innerHTML = `
            <strong>${student.name}</strong>
            <p>ID: ${student.id}</p>
            <small>Registrado: ${DataUtils.formatDate(student.enrolled_date)}</small>
        `;
        container.appendChild(item);
    });
}

function updateEngagementAlerts() {
    const container = document.getElementById('engagementAlerts');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Generar alertas basadas en emociones negativas
    const negativeEmotions = allData.emotions.filter(e => 
        ['sad', 'angry', 'fear'].includes(e.emotion)
    );
    
    const totalNegative = negativeEmotions.reduce((sum, e) => sum + e.count, 0);
    const totalEmotions = allData.emotions.reduce((sum, e) => sum + e.count, 0);
    
    if (totalEmotions > 0 && (totalNegative / totalEmotions) > 0.3) {
        const alert = document.createElement('div');
        alert.className = 'alert-item';
        alert.innerHTML = `
            <strong>⚠️ Alto nivel de emociones negativas</strong>
            <p>${((totalNegative / totalEmotions) * 100).toFixed(1)}% de emociones negativas detectadas</p>
        `;
        container.appendChild(alert);
    } else {
        container.innerHTML = '<p class="info-text">✅ Sin alertas. El engagement es bueno.</p>';
    }
}

function exportAttendanceData() {
    if (allData.attendance.length === 0) {
        UIUtils.showMessage('No hay datos de asistencia para exportar', 'error');
        return;
    }
    
    DataUtils.downloadCSV(allData.attendance, `attendance_${Date.now()}.csv`);
    UIUtils.showMessage('Datos de asistencia exportados', 'success');
}

function exportEmotionsData() {
    if (allData.emotions.length === 0) {
        UIUtils.showMessage('No hay datos de emociones para exportar', 'error');
        return;
    }
    
    DataUtils.downloadCSV(allData.emotions, `emotions_${Date.now()}.csv`);
    UIUtils.showMessage('Datos de emociones exportados', 'success');
}

function exportFullReport() {
    UIUtils.showMessage('La exportación de PDF estará disponible próximamente', 'info');
    
    // En una implementación real, aquí generarías un PDF con jsPDF
    console.log('Generando reporte completo...', allData);
}
