/**
 * Smart Classroom AI - Attendance View
 * Toma de asistencia con reconocimiento facial
 */
<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">✅ Toma de Asistencia</h1>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Camera Section -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-bold text-gray-900">📸 Verificación Facial</h2>
              <select
                v-model="selectedClassId"
                class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Seleccionar clase...</option>
                <option v-for="classItem in activeClasses" :key="classItem.id" :value="classItem.id">
                  {{ classItem.class_name }}
                </option>
              </select>
            </div>

            <div class="relative bg-gray-900 rounded-lg overflow-hidden mb-4" style="aspect-ratio: 16/9;">
              <video
                v-if="!capturedPhoto"
                ref="videoRef"
                autoplay
                playsinline
                class="w-full h-full object-cover"
                style="transform: scaleX(1);"
              ></video>
              <img
                v-else
                :src="capturedPhoto"
                alt="Captured photo"
                class="w-full h-full object-cover"
              />
              
              <div v-if="verifying" class="absolute inset-0 backdrop-blur-md bg-black/50 flex items-center justify-center">
                <div class="text-center text-white">
                  <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                  <p>Verificando estudiante...</p>
                </div>
              </div>
            </div>

            <div class="flex gap-3">
              <button
                v-if="!isCameraActive"
                @click="startCamera"
                class="flex-1 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                📷 Activar Cámara
              </button>
              
              <button
                v-if="isCameraActive && !capturedPhoto"
                @click="captureAndVerify"
                :disabled="!selectedClassId || verifying"
                class="flex-1 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                ✅ Verificar Asistencia
              </button>

              <button
                v-if="capturedPhoto"
                @click="resetCapture"
                class="flex-1 px-4 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
              >
                🔄 Otra Verificación
              </button>

              <button
                v-if="isCameraActive"
                @click="stopCamera"
                class="px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                ⏹️
              </button>
            </div>

            <div v-if="verificationResult" class="mt-4 p-4 rounded-lg" :class="getResultClass()">
              <p class="font-semibold" :class="getTextClass()">
                {{ getResultMessage() }}
              </p>
              <p v-if="verificationResult.success && verificationResult.student_name" class="text-sm mt-1" :class="getTextClass()">
                Estudiante: {{ verificationResult.student_name }} (Confianza: {{ Math.round(verificationResult.confidence * 100) }}%)
              </p>
              <!-- Warning for already registered attendance -->
              <p v-if="verificationResult.already_registered" class="text-sm mt-2 text-yellow-700 font-medium">
                ℹ️ La asistencia fue registrada previamente a las {{ formatTime(verificationResult.timestamp) }}
              </p>
              <div v-if="detectedEmotion" class="mt-2 p-2 bg-purple-50 rounded border-l-2 border-purple-400">
                <p class="text-sm font-medium text-purple-700">
                  {{ getEmotionEmoji(detectedEmotion.emotion) }} Emoción detectada: <span class="font-bold">{{ getEmotionName(detectedEmotion.emotion) }}</span>
                  <span class="text-xs">({{ Math.round(detectedEmotion.confidence * 100) }}%)</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Attendance Log -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">📋 Registro de Asistencia</h2>
          
          <div v-if="attendanceRecords.length === 0" class="text-center text-gray-500 py-8">
            <p>No hay registros aún</p>
            <p class="text-xs mt-2">Selecciona una clase y verifica asistencia</p>
          </div>

          <div v-else class="space-y-3 max-h-[600px] overflow-y-auto">
            <div
              v-for="record in attendanceRecords"
              :key="record.id"
              class="p-3 rounded-lg border-l-4"
              :class="record.status === 'late' 
                ? 'bg-gradient-to-r from-orange-50 to-amber-50 border-orange-500' 
                : 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-500'"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <p class="font-bold text-gray-900">{{ record.student_name || record.student_id }}</p>
                  <p class="text-xs text-gray-600 mt-1">
                    <span class="font-medium">Cédula:</span> {{ record.student_id }}
                  </p>
                  <p class="text-xs text-gray-600">
                    <span class="font-medium">Hora:</span> {{ formatTime(record.timestamp) }}
                  </p>
                  <div class="mt-2 flex items-center gap-2">
                    <span 
                      class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                      :class="record.status === 'late' 
                        ? 'bg-orange-100 text-orange-800' 
                        : 'bg-green-100 text-green-800'"
                    >
                      {{ record.status === 'late' ? '⏰ Atrasado' : '✓ Presente' }}
                    </span>
                    <span 
                      class="text-xs font-medium"
                      :class="record.status === 'late' ? 'text-orange-600' : 'text-green-600'"
                    >
                      Confianza: {{ record.confidence ? Math.round(record.confidence * 100) : 'N/A' }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import { classesService } from '@/services/classes.service'
import { attendanceService } from '@/services/attendance.service'
import { emotionsService } from '@/services/emotions.service'
import type { ClassSession, AttendanceRecord } from '@/types'

const route = useRoute()

const videoRef = ref<HTMLVideoElement | null>(null)
const isCameraActive = ref(false)
const capturedPhoto = ref<string | null>(null)
const mediaStream = ref<MediaStream | null>(null)
const verifying = ref(false)
const verificationResult = ref<any>(null)

const activeClasses = ref<ClassSession[]>([])
const selectedClassId = ref<number | string>('')
const attendanceRecords = ref<AttendanceRecord[]>([])
const detectedEmotion = ref<{emotion: string, confidence: number} | null>(null)

const startCamera = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: 1280, height: 720 },
      audio: false
    })

    if (videoRef.value) {
      videoRef.value.srcObject = stream
      mediaStream.value = stream
      isCameraActive.value = true
    }
  } catch (error) {
    console.error('Error activando cámara:', error)
    alert('No se pudo acceder a la cámara')
  }
}

const stopCamera = () => {
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach(track => track.stop())
    mediaStream.value = null
  }
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
  isCameraActive.value = false
}

const captureAndVerify = async () => {
  if (!videoRef.value || !selectedClassId.value) return

  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  
  const context = canvas.getContext('2d')
  if (!context) return

  context.drawImage(videoRef.value, 0, 0)
  capturedPhoto.value = canvas.toDataURL('image/jpeg', 0.9)

  verifying.value = true
  verificationResult.value = null
  detectedEmotion.value = null

  try {
    const response = await fetch(capturedPhoto.value)
    const blob = await response.blob()
    const file = new File([blob], 'attendance.jpg', { type: 'image/jpeg' })

    // Verify attendance
    const result = await attendanceService.verifyAttendance({
      class_id: Number(selectedClassId.value),
      image: file
    })

    console.log('✅ Attendance result:', result)
    verificationResult.value = result
    
    // If student recognized, analyze emotion and save to DB
    if (result.success && result.student_id) {
      try {
        console.log('🎭 Analyzing emotion for student:', result.student_id, 'in class:', selectedClassId.value)
        const emotionFile = new File([blob], 'emotion.jpg', { type: 'image/jpeg' })
        const emotionResult = await emotionsService.analyzeEmotion({
          class_id: selectedClassId.value.toString(),
          image: emotionFile,
          student_id: result.student_id.toString()
        })
        
        console.log('🎭 Emotion result:', emotionResult)
        
        if (emotionResult.data?.emotions?.[0]) {
          detectedEmotion.value = {
            emotion: emotionResult.data.emotions[0].emotion,
            confidence: emotionResult.data.emotions[0].confidence
          }
          console.log('✅ Emotion detected:', detectedEmotion.value)
        } else {
          console.warn('⚠️ No emotions in response:', emotionResult)
        }
      } catch (emotionError) {
        console.error('❌ Emotion analysis failed:', emotionError)
      }
    } else {
      console.warn('⚠️ No student_id in attendance result or not successful:', result)
    }
    
    if (result.success) {
      await loadAttendanceRecords()
    }
  } catch (error: any) {
    verificationResult.value = {
      success: false,
      message: error.response?.data?.detail || 'Error en la verificación'
    }
  } finally {
    verifying.value = false
  }
}

const resetCapture = () => {
  capturedPhoto.value = null
  verificationResult.value = null
  startCamera()
}

const loadActiveClasses = async () => {
  try {
    activeClasses.value = await classesService.getActiveClasses()
    
    if (route.query.class_id) {
      selectedClassId.value = Number(route.query.class_id)
    } else if (activeClasses.value.length > 0 && activeClasses.value[0]) {
      selectedClassId.value = activeClasses.value[0].id
    }
  } catch (error) {
    console.error('Error cargando clases:', error)
  }
}

const loadAttendanceRecords = async () => {
  if (!selectedClassId.value) return

  try {
    attendanceRecords.value = await attendanceService.getClassAttendance(Number(selectedClassId.value))
  } catch (error) {
    console.error('Error cargando registros:', error)
  }
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-ES', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}

// Emotion helper functions
const getEmotionEmoji = (emotion: string): string => {
  const emojis: Record<string, string> = {
    'happy': '😊',
    'sad': '😢',
    'angry': '😠',
    'surprise': '😮',
    'fear': '😨',
    'disgust': '🤢',
    'neutral': '😐'
  }
  return emojis[emotion?.toLowerCase()] || '😶'
}

const getEmotionName = (emotion: string): string => {
  const names: Record<string, string> = {
    'happy': 'Feliz',
    'sad': 'Triste',
    'angry': 'Enojado',
    'surprise': 'Sorprendido',
    'fear': 'Miedo',
    'disgust': 'Disgusto',
    'neutral': 'Neutral'
  }
  return names[emotion?.toLowerCase()] || emotion
}

// Helper functions for displaying verification result
const getResultClass = () => {
  if (!verificationResult.value) return ''
  if (!verificationResult.value.success) return 'bg-red-50 border-l-4 border-red-500'
  if (verificationResult.value.already_registered) return 'bg-yellow-50 border-l-4 border-yellow-500'
  // Orange/amber for late students
  if (verificationResult.value.status === 'late') return 'bg-orange-50 border-l-4 border-orange-500'
  return 'bg-green-50 border-l-4 border-green-500'
}

const getTextClass = () => {
  if (!verificationResult.value) return ''
  if (!verificationResult.value.success) return 'text-red-700'
  if (verificationResult.value.already_registered) return 'text-yellow-700'
  // Orange for late students
  if (verificationResult.value.status === 'late') return 'text-orange-700'
  return 'text-green-700'
}

const getResultMessage = () => {
  if (!verificationResult.value) return ''
  if (!verificationResult.value.success) return verificationResult.value.message || 'Estudiante no reconocido'
  if (verificationResult.value.already_registered) return '⚠️ Asistencia ya registrada anteriormente'
  
  // Check if student is late
  if (verificationResult.value.status === 'late') {
    return '⏰ Asistencia registrada - ATRASADO'
  }
  return '✅ Asistencia registrada - Presente'
}

onMounted(async () => {
  await loadActiveClasses()
  if (selectedClassId.value) {
    await loadAttendanceRecords()
  }
})

onUnmounted(() => {
  stopCamera()
})
</script>
