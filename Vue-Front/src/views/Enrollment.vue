/**
 * Smart Classroom AI - Student Enrollment View
 * Registro de estudiantes con reconocimiento facial
 */
<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">➕ Registrar Nuevo Estudiante</h1>
        <p class="mt-2 text-sm text-gray-600">
          Captura la foto del estudiante para el reconocimiento facial
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Camera Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">📸 Captura de Rostro</h2>

          <!-- Camera/Photo Display -->
          <div class="relative bg-gray-900 rounded-lg overflow-hidden mb-4" style="aspect-ratio: 4/3;">
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
            
            <!-- Camera Overlay -->
            <div v-if="!capturedPhoto" class="absolute inset-0 pointer-events-none">
              <div class="absolute inset-0 border-4 border-indigo-500 rounded-full m-auto" style="width: 60%; height: 80%;"></div>
              <p class="absolute bottom-4 left-0 right-0 text-center text-white text-sm backdrop-blur-sm bg-black/40 py-2">
                Centra tu rostro en el círculo
              </p>
            </div>
          </div>

          <!-- Camera Controls -->
          <div class="flex gap-3">
            <button
              v-if="!isCameraActive && !capturedPhoto"
              @click="startCamera"
              class="flex-1 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200 font-medium"
            >
              📷 Activar Cámara
            </button>
            
            <button
              v-if="isCameraActive && !capturedPhoto"
              @click="capturePhoto"
              class="flex-1 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 font-medium"
            >
              📸 Capturar Foto
            </button>

            <button
              v-if="capturedPhoto"
              @click="retakePhoto"
              class="flex-1 px-4 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors duration-200 font-medium"
            >
              🔄 Tomar Otra
            </button>

            <button
              v-if="isCameraActive"
              @click="stopCamera"
              class="px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 font-medium"
            >
              ⏹️
            </button>
          </div>

          <!-- Instructions -->
          <div class="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 class="font-semibold text-gray-900 mb-2">💡 Consejos para una mejor captura:</h3>
            <ul class="text-sm text-gray-600 space-y-1">
              <li>• Asegúrate de tener buena iluminación</li>
              <li>• Mira directamente a la cámara</li>
              <li>• Mantén una expresión neutral</li>
              <li>• Evita usar gafas oscuras</li>
            </ul>
          </div>
        </div>

        <!-- Form Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">📝 Información del Estudiante</h2>

          <form @submit.prevent="handleEnrollment" class="space-y-4">
            <!-- Cédula -->
            <div>
              <label for="studentId" class="block text-sm font-medium text-gray-700 mb-1">
                Cédula *
              </label>
              <input
                id="studentId"
                v-model="formData.studentId"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Ej: 0102345678"
                maxlength="10"
              />
            </div>

            <!-- Full Name -->
            <div>
              <label for="fullName" class="block text-sm font-medium text-gray-700 mb-1">
                Nombre Completo *
              </label>
              <input
                id="fullName"
                v-model="formData.fullName"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Ej: Juan Pérez García"
              />
            </div>

            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
                Correo Electrónico *
              </label>
              <input
                id="email"
                v-model="formData.email"
                type="email"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="estudiante@universidad.edu"
              />
            </div>

            <!-- Error Message -->
            <div v-if="errorMessage" class="p-4 bg-red-50 border-l-4 border-red-500 rounded">
              <p class="text-sm text-red-700">{{ errorMessage }}</p>
            </div>

            <!-- Success Message -->
            <div v-if="successMessage" class="p-4 bg-green-50 border-l-4 border-green-500 rounded">
              <p class="text-sm text-green-700">{{ successMessage }}</p>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="!capturedPhoto || isSubmitting"
              class="w-full px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <svg
                v-if="isSubmitting"
                class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isSubmitting ? 'Registrando...' : '✅ Registrar Estudiante' }}
            </button>
          </form>

          <!-- Status Info -->
          <div class="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 class="font-semibold text-gray-900 mb-2">Estado del Registro:</h3>
            <div class="space-y-2 text-sm">
              <div class="flex items-center">
                <span :class="capturedPhoto ? 'text-green-600' : 'text-gray-400'">
                  {{ capturedPhoto ? '✅' : '⏸️' }}
                </span>
                <span class="ml-2 text-gray-600">Foto capturada</span>
              </div>
              <div class="flex items-center">
                <span :class="formData.studentId && formData.fullName && formData.email ? 'text-green-600' : 'text-gray-400'">
                  {{ formData.studentId && formData.fullName && formData.email ? '✅' : '⏸️' }}
                </span>
                <span class="ml-2 text-gray-600">Información completa</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="mt-8 flex justify-between">
        <router-link
          to="/students"
          class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors duration-200 font-medium"
        >
          ← Ver Estudiantes
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import { enrollmentService } from '@/services/enrollment.service'

const router = useRouter()

const videoRef = ref<HTMLVideoElement | null>(null)
const isCameraActive = ref(false)
const capturedPhoto = ref<string | null>(null)
const mediaStream = ref<MediaStream | null>(null)
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const formData = reactive({
  studentId: '',
  fullName: '',
  email: ''
})

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
    errorMessage.value = 'No se pudo acceder a la cámara. Verifica los permisos.'
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

const capturePhoto = () => {
  if (!videoRef.value) return

  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  
  const context = canvas.getContext('2d')
  if (context) {
    context.drawImage(videoRef.value, 0, 0)
    capturedPhoto.value = canvas.toDataURL('image/jpeg', 0.9)
    stopCamera()
  }
}

const retakePhoto = () => {
  capturedPhoto.value = null
  errorMessage.value = ''
  successMessage.value = ''
  startCamera()
}

const handleEnrollment = async () => {
  if (!capturedPhoto.value) {
    errorMessage.value = 'Debes capturar una foto primero'
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    // Convert base64 to File
    const response = await fetch(capturedPhoto.value)
    const blob = await response.blob()
    const file = new File([blob], 'student-photo.jpg', { type: 'image/jpeg' })

    // Enroll student
    const result = await enrollmentService.enrollStudent({
      student_id: formData.studentId,
      name: formData.fullName,
      email: formData.email,
      image: file
    })

    if (result.success) {
      successMessage.value = '¡Estudiante registrado exitosamente!'
      
      setTimeout(() => {
        router.push('/students')
      }, 2000)
    } else {
      throw new Error(result.message || 'Error en el registro')
    }
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || error.message || 'Error al registrar el estudiante'
  } finally {
    isSubmitting.value = false
  }
}

onUnmounted(() => {
  stopCamera()
})
</script>
