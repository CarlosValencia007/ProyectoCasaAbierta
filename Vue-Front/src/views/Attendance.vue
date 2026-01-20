/**
 * Smart Classroom AI - Attendance View
 * Toma de asistencia con reconocimiento facial automático
 */
<template>
  <div class="min-h-screen bg-gray-50">

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <PageHeader
        title="Toma de Asistencia"
        icon="clipboard-check"
        icon-color="green"
      />

      <!-- Selector de Clase -->
      <div class="bg-white rounded-lg shadow-md p-4 mb-6">
        <div class="flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div class="flex items-center gap-3">
            <label class="font-medium text-gray-700">Clase:</label>
            <select
              v-model="selectedClassId"
              @change="onClassChange"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#b81a16] min-w-[250px]"
            >
              <option value="">{{ activeClasses.length === 0 ? 'No hay clases disponibles' : 'Seleccionar clase...' }}</option>
              <option 
                v-for="classItem in activeClasses" 
                :key="classItem.id" 
                :value="classItem.id"
                :class="getClassOptionClass(classItem)"
              >
                {{ classItem.class_name }} {{ getClassStatusLabel(classItem) }}
              </option>
            </select>
          </div>
          
          <!-- Tabs de Modo -->
          <div class="flex bg-gray-100 rounded-lg p-1">
            <button
              @click="attendanceMode = 'facial'"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2',
                attendanceMode === 'facial' 
                  ? 'bg-[#b81a16] text-white shadow-md' 
                  : 'text-gray-600 hover:text-gray-800'
              ]"
            >
              <FontAwesomeIcon :icon="['fas', 'camera']" />
              <span class="hidden sm:inline">Reconocimiento</span> Facial
            </button>
            <button
              @click="attendanceMode = 'qr'"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2',
                attendanceMode === 'qr' 
                  ? 'bg-[#b81a16] text-white shadow-md' 
                  : 'text-gray-600 hover:text-gray-800'
              ]"
            >
              <FontAwesomeIcon :icon="['fas', 'qrcode']" />
              <span class="hidden sm:inline">Código</span> QR
            </button>
            <button
              @click="attendanceMode = 'manual'"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2',
                attendanceMode === 'manual' 
                  ? 'bg-[#b81a16] text-white shadow-md' 
                  : 'text-gray-600 hover:text-gray-800'
              ]"
            >
              <FontAwesomeIcon :icon="['fas', 'list-check']" />
              Manual
            </button>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Camera Section (Modo Facial) -->
        <div v-if="attendanceMode === 'facial'" class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                <FontAwesomeIcon :icon="['fas', 'camera']" class="text-[#b81a16]" />
                Verificación Facial Automática
              </h2>
              <span v-if="selectedClassId" class="text-sm text-gray-500">
                El estudiante se para frente a la cámara
              </span>
            </div>

            <div class="relative bg-gray-900 rounded-lg overflow-hidden mb-4" style="aspect-ratio: 16/9;">
              <video
                ref="videoRef"
                autoplay
                playsinline
                class="w-full h-full object-cover"
                style="transform: scaleX(1);"
              ></video>
              
              <div v-if="verifying" class="absolute inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center">
                <div class="text-center text-white">
                  <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
                  <p class="font-semibold">Verificando estudiante...</p>
                </div>
              </div>

              <div v-if="autoVerificationEnabled && isCameraActive" class="absolute top-4 right-4">
                <span class="inline-flex items-center gap-2 px-3 py-2 bg-green-500 text-white rounded-lg shadow-lg">
                  <span class="relative flex h-3 w-3">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
                  </span>
                  Verificación automática activa
                </span>
              </div>
            </div>

            <div class="flex gap-3">
              <button
                v-if="!isCameraActive"
                @click="startCamera"
                :disabled="!selectedClassId"
                class="flex-1 px-4 py-3 bg-[#b81a16] text-white rounded-lg hover:bg-[#9a1512] transition-colors disabled:opacity-50 inline-flex items-center justify-center gap-2"
              >
                <FontAwesomeIcon :icon="['fas', 'camera']" />
                Iniciar Verificación Automática
              </button>
              
              <button
                v-if="isCameraActive"
                @click="stopCamera"
                class="flex-1 px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors inline-flex items-center justify-center gap-2"
              >
                <FontAwesomeIcon :icon="['fas', 'stop']" />
                Detener Verificación
              </button>
            </div>

            <div v-if="lastVerification" class="mt-4 p-4 rounded-lg" :class="getResultClass()">
              <p class="font-semibold" :class="getTextClass()">
                {{ getResultMessage() }}
              </p>
              <p v-if="lastVerification.success && lastVerification.student_name" class="text-sm mt-1" :class="getTextClass()">
                Estudiante: {{ lastVerification.student_name }} (Confianza: {{ Math.round(lastVerification.confidence * 100) }}%)
              </p>
              <p v-if="lastVerification.already_registered" class="text-sm mt-2 text-yellow-700 font-medium inline-flex items-center gap-1">
                <FontAwesomeIcon :icon="['fas', 'circle-info']" />
                La asistencia fue registrada previamente a las {{ formatTime(lastVerification.timestamp) }}
              </p>
              <div v-if="detectedEmotion" class="mt-2 p-2 bg-purple-50 rounded border-l-2 border-purple-400">
                <p class="text-sm font-medium text-purple-700">
                  {{ getEmotionEmoji(detectedEmotion.emotion) }} Emoción: <span class="font-bold">{{ getEmotionName(detectedEmotion.emotion) }}</span>
                  <span class="text-xs">({{ Math.round(detectedEmotion.confidence * 100) }}%)</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Manual Section (Modo Manual) -->
        <div v-if="attendanceMode === 'manual'" class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                <FontAwesomeIcon :icon="['fas', 'list-check']" class="text-[#b81a16]" />
                Registro Manual de Asistencia
              </h2>
            </div>

            <!-- Sin clase seleccionada -->
            <div v-if="!selectedClassId" class="text-center py-16 text-gray-500">
              <FontAwesomeIcon :icon="['fas', 'hand-pointer']" class="text-6xl mb-4 text-gray-300" />
              <p class="text-lg">Selecciona una clase para registrar asistencia</p>
            </div>

            <div v-else>
              <!-- Eliminado: Selector de Período/Hora (uso simplificado por estudiante) -->

              <!-- Acciones rápidas -->
              <div class="flex flex-wrap gap-2 mb-4 p-3 bg-gray-50 rounded-lg">
                <span class="text-sm text-gray-600 font-medium mr-2">Marcar todos como:</span>
                <button
                  @click="markAllAs('present')"
                  class="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                >
                  <FontAwesomeIcon :icon="['fas', 'check']" class="mr-1" />
                  Presentes
                </button>
                <button
                  @click="markAllAs('late')"
                  class="px-3 py-1 text-sm bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors"
                >
                  <FontAwesomeIcon :icon="['fas', 'clock']" class="mr-1" />
                  Retrasados
                </button>
                <button
                  @click="markAllAs('absent')"
                  class="px-3 py-1 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                >
                  <FontAwesomeIcon :icon="['fas', 'xmark']" class="mr-1" />
                  Ausentes
                </button>
                <button
                  @click="clearAllManual"
                  class="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors ml-auto"
                >
                  <FontAwesomeIcon :icon="['fas', 'eraser']" class="mr-1" />
                  Limpiar
                </button>
              </div>

              <!-- Lista de estudiantes con estados -->
              <div v-if="loadingStudents" class="text-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#b81a16] mx-auto mb-2"></div>
                <p class="text-sm text-gray-500">Cargando estudiantes...</p>
              </div>

              <div v-else-if="enrolledStudents.length === 0" class="text-center py-8 text-gray-500">
                <FontAwesomeIcon :icon="['fas', 'user-slash']" class="text-4xl mb-2" />
                <p>No hay estudiantes inscritos en esta clase</p>
              </div>

              <div v-else class="space-y-2 max-h-[400px] overflow-y-auto">
                <div
                  v-for="student in enrolledStudents"
                  :key="student.student_id"
                  class="p-4 rounded-lg border-2 transition-all"
                  :class="getManualStudentCardClass(student.student_id)"
                >
                  <div class="flex flex-col sm:flex-row sm:items-center gap-3">
                    <!-- Info del estudiante -->
                    <div class="flex-1 min-w-0">
                      <p class="font-semibold text-gray-900">{{ student.name }}</p>
                      <p class="text-xs text-gray-600">{{ student.student_id }}</p>
                    </div>
                    
                    <!-- Opciones de estado -->
                    <div class="flex gap-2">
                      <label
                        :class="[
                          'flex items-center gap-1 px-3 py-2 rounded-lg cursor-pointer transition-all border-2',
                          getManualStatus(student.student_id) === 'present'
                            ? 'bg-green-500 text-white border-green-500'
                            : 'bg-green-50 text-green-700 border-green-200 hover:border-green-400'
                        ]"
                      >
                        <input
                          type="radio"
                          :name="`attendance-${student.student_id}`"
                          value="present"
                          :checked="getManualStatus(student.student_id) === 'present'"
                          @change="setManualStatus(student.student_id, 'present')"
                          class="sr-only"
                        />
                        <FontAwesomeIcon :icon="['fas', 'check']" />
                        <span class="text-sm font-medium">Presente</span>
                      </label>
                      
                      <label
                        :class="[
                          'flex items-center gap-1 px-3 py-2 rounded-lg cursor-pointer transition-all border-2',
                          getManualStatus(student.student_id) === 'late'
                            ? 'bg-orange-500 text-white border-orange-500'
                            : 'bg-orange-50 text-orange-700 border-orange-200 hover:border-orange-400'
                        ]"
                      >
                        <input
                          type="radio"
                          :name="`attendance-${student.student_id}`"
                          value="late"
                          :checked="getManualStatus(student.student_id) === 'late'"
                          @change="setManualStatus(student.student_id, 'late')"
                          class="sr-only"
                        />
                        <FontAwesomeIcon :icon="['fas', 'clock']" />
                        <span class="text-sm font-medium">Retraso</span>
                      </label>
                      
                      <label
                        :class="[
                          'flex items-center gap-1 px-3 py-2 rounded-lg cursor-pointer transition-all border-2',
                          getManualStatus(student.student_id) === 'absent'
                            ? 'bg-red-500 text-white border-red-500'
                            : 'bg-red-50 text-red-700 border-red-200 hover:border-red-400'
                        ]"
                      >
                        <input
                          type="radio"
                          :name="`attendance-${student.student_id}`"
                          value="absent"
                          :checked="getManualStatus(student.student_id) === 'absent'"
                          @change="setManualStatus(student.student_id, 'absent')"
                          class="sr-only"
                        />
                        <FontAwesomeIcon :icon="['fas', 'xmark']" />
                        <span class="text-sm font-medium">Falta</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Botón guardar -->
              <div class="mt-6 pt-4 border-t border-gray-200">
                <div class="flex flex-col sm:flex-row gap-3 items-center justify-between">
                  <div class="text-sm text-gray-600">
                    <span class="font-medium">Resumen:</span>
                    <span class="ml-2 text-green-600">{{ manualPresentCount }} presentes</span>
                    <span class="mx-1">•</span>
                    <span class="text-orange-600">{{ manualLateCount }} retrasados</span>
                    <span class="mx-1">•</span>
                    <span class="text-red-600">{{ manualAbsentCount }} ausentes</span>
                  </div>
                  <button
                    @click="saveManualAttendance"
                    :disabled="savingManual || !hasManualChanges"
                    class="px-6 py-3 bg-[#b81a16] text-white rounded-lg hover:bg-[#9a1512] transition-colors disabled:opacity-50 inline-flex items-center gap-2 font-medium"
                  >
                    <FontAwesomeIcon :icon="['fas', savingManual ? 'spinner' : 'save']" :class="{ 'animate-spin': savingManual }" />
                    {{ savingManual ? 'Guardando...' : 'Guardar Asistencia' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- QR Code Section (Modo QR) -->
        <div v-if="attendanceMode === 'qr'" class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-bold text-gray-900 flex items-center gap-2">
                <FontAwesomeIcon :icon="['fas', 'qrcode']" class="text-[#b81a16]" />
                Código QR de Asistencia
              </h2>
              <button
                v-if="!qrGenerated"
                @click="generateQRCode"
                :disabled="!selectedClassId || generatingQR"
                class="px-4 py-2 bg-[#b81a16] text-white rounded-lg hover:bg-[#9a1512] transition-colors disabled:opacity-50 inline-flex items-center gap-2"
              >
                <FontAwesomeIcon :icon="['fas', 'wand-magic-sparkles']" />
                {{ generatingQR ? 'Generando...' : 'Generar Código' }}
              </button>
              <button
                v-else
                @click="regenerateQRCode"
                class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors inline-flex items-center gap-2"
              >
                <FontAwesomeIcon :icon="['fas', 'arrows-rotate']" />
                Regenerar
              </button>
            </div>

            <!-- Sin clase seleccionada -->
            <div v-if="!selectedClassId" class="text-center py-16 text-gray-500">
              <FontAwesomeIcon :icon="['fas', 'hand-pointer']" class="text-6xl mb-4 text-gray-300" />
              <p class="text-lg">Selecciona una clase para generar el código QR</p>
            </div>

            <!-- QR Generado -->
            <div v-else-if="qrGenerated" class="text-center">
              <!-- Código Grande -->
              <div class="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 mb-6 shadow-2xl">
                <p class="text-gray-400 text-sm font-medium mb-2 uppercase tracking-widest">Código de Asistencia</p>
                <p class="text-7xl md:text-9xl font-black text-white tracking-[0.2em] font-mono">
                  {{ currentQRCode }}
                </p>
                <div class="mt-4 flex items-center justify-center gap-2 text-gray-400">
                  <FontAwesomeIcon :icon="['fas', 'clock']" />
                  <span>Cambia en: <span class="text-yellow-400 font-bold">{{ codeCountdown }}s</span></span>
                </div>
              </div>

              <!-- QR Code Image -->
              <div class="flex flex-col md:flex-row gap-6 items-center justify-center">
                <div class="bg-white p-4 rounded-xl shadow-lg border-2 border-gray-200">
                  <img v-if="qrImageUrl" :src="qrImageUrl" alt="QR Code" class="w-48 h-48" />
                </div>
                <div class="text-left space-y-2">
                  <p class="text-gray-700 font-medium">Instrucciones para estudiantes:</p>
                  <ol class="text-sm text-gray-600 space-y-1 list-decimal list-inside">
                    <li>Escanea el código QR con tu teléfono</li>
                    <li>Ingresa tu número de cédula</li>
                    <li>Ingresa el código de 6 dígitos que ves en pantalla</li>
                    <li>¡Listo! Tu asistencia quedará registrada</li>
                  </ol>
                  <div class="mt-4 pt-4 border-t border-gray-200">
                    <button
                      @click="copyQRLink"
                      class="text-sm text-blue-600 hover:text-blue-800 inline-flex items-center gap-1"
                    >
                      <FontAwesomeIcon :icon="['fas', 'copy']" />
                      Copiar enlace
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Esperando generar -->
            <div v-else class="text-center py-16 text-gray-500">
              <FontAwesomeIcon :icon="['fas', 'qrcode']" class="text-6xl mb-4 text-gray-300" />
              <p class="text-lg">Haz clic en "Generar Código" para comenzar</p>
              <p class="text-sm mt-2">Los estudiantes podrán registrar su asistencia escaneando el QR</p>
            </div>
          </div>
        </div>

        <!-- Students List -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <FontAwesomeIcon :icon="['fas', 'users']" class="text-[#b81a16]" />
            Lista de Estudiantes
          </h2>
          
          <div v-if="!selectedClassId" class="text-center text-gray-500 py-8">
            <FontAwesomeIcon :icon="['fas', 'arrow-up']" class="text-4xl mb-2" />
            <p>Selecciona una clase</p>
          </div>

          <div v-else-if="loadingStudents" class="text-center text-gray-500 py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#b81a16] mx-auto mb-2"></div>
            <p class="text-sm">Cargando estudiantes...</p>
          </div>

          <div v-else-if="enrolledStudents.length === 0" class="text-center text-gray-500 py-8">
            <FontAwesomeIcon :icon="['fas', 'user-slash']" class="text-4xl mb-2" />
            <p>No hay estudiantes inscritos</p>
          </div>

          <div v-else class="space-y-2 max-h-[600px] overflow-y-auto">
            <div
              v-for="student in enrolledStudents"
              :key="student.student_id"
              class="p-3 rounded-lg border-2 transition-all duration-300"
              :class="getStudentCardClass(student.student_id)"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <p class="font-semibold text-gray-900 truncate">{{ student.name }}</p>
                  <p class="text-xs text-gray-600 mt-0.5">{{ student.student_id }}</p>
                </div>
                <div class="ml-2">
                  <FontAwesomeIcon 
                    v-if="isStudentPresent(student.student_id)"
                    :icon="['fas', 'circle-check']" 
                    class="text-2xl"
                    :class="getStudentStatus(student.student_id) === 'late' ? 'text-orange-500' : 'text-green-500'"
                  />
                  <FontAwesomeIcon 
                    v-else
                    :icon="['fas', 'circle']" 
                    class="text-2xl text-gray-300"
                  />
                </div>
              </div>
              <div v-if="isStudentPresent(student.student_id)" class="mt-2 pt-2 border-t border-gray-200">
                <p class="text-xs" :class="getStudentStatus(student.student_id) === 'late' ? 'text-orange-600' : 'text-green-600'">
                  <FontAwesomeIcon :icon="['fas', 'clock']" class="mr-1" />
                  {{ getStudentAttendanceTime(student.student_id) }}
                  <span v-if="getStudentStatus(student.student_id) === 'late'" class="ml-1 font-semibold">- ATRASADO</span>
                </p>
              </div>
            </div>
          </div>

          <div class="mt-4 pt-4 border-t border-gray-200">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Presente:</span>
              <span class="font-bold text-green-600">{{ presentCount }} / {{ enrolledStudents.length }}</span>
            </div>
            <div class="mt-1 flex items-center justify-between text-sm">
              <span class="text-gray-600">Ausente:</span>
              <span class="font-bold text-gray-500">{{ enrolledStudents.length - presentCount }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { classesService } from '@/services/classes.service'
import { attendanceService } from '@/services/attendance.service'
import { emotionsService } from '@/services/emotions.service'
import { enrollmentService } from '@/services/enrollment.service'
import { qrService } from '@/services/qr.service'
import type { ClassSession, AttendanceRecord, Student } from '@/types'
import PageHeader from '@/components/PageHeader.vue'

const route = useRoute()

// Modo de asistencia: 'facial', 'qr' o 'manual'
const attendanceMode = ref<'facial' | 'qr' | 'manual'>('facial')

// Variables de cámara/facial
const videoRef = ref<HTMLVideoElement | null>(null)
const isCameraActive = ref(false)
const mediaStream = ref<MediaStream | null>(null)
const verifying = ref(false)
const lastVerification = ref<any>(null)
const autoVerificationEnabled = ref(false)
const verificationIntervalId = ref<number | null>(null)

// Variables de QR
const qrGenerated = ref(false)
const generatingQR = ref(false)
const qrImageUrl = ref('')
const qrLink = ref('')
const currentQRCode = ref('')
const codeCountdown = ref(120)
const qrToken = ref('')
const countdownIntervalId = ref<number | null>(null)

const activeClasses = ref<ClassSession[]>([])
const selectedClassId = ref<number | string>('')
const attendanceRecords = ref<AttendanceRecord[]>([])
const enrolledStudents = ref<Student[]>([])
const loadingStudents = ref(false)
const detectedEmotion = ref<{emotion: string, confidence: number} | null>(null)

// Variables para modo manual (uso simplificado por estudiante)
const manualAttendance = ref<Record<string, 'present' | 'late' | 'absent' | null>>({})
const savingManual = ref(false)

// Obtener estado manual de un estudiante (sin períodos)
const getManualStatus = (studentId: string): 'present' | 'late' | 'absent' | null => {
  return manualAttendance.value[studentId] ?? null
}

// Establecer estado manual de un estudiante (sin períodos)
const setManualStatus = (studentId: string, status: 'present' | 'late' | 'absent') => {
  manualAttendance.value[studentId] = status
}

// Marcar todos los estudiantes con un estado
const markAllAs = (status: 'present' | 'late' | 'absent') => {
  enrolledStudents.value.forEach(student => {
    setManualStatus(student.student_id, status)
  })
}

// Limpiar todos los estados manuales
const clearAllManual = () => {
  enrolledStudents.value.forEach(student => {
    if (manualAttendance.value[student.student_id] !== undefined) {
      delete manualAttendance.value[student.student_id]
    }
  })
}

// Contadores (uso simplificado por estudiante)
const manualPresentCount = computed(() => {
  return enrolledStudents.value.filter(s => getManualStatus(s.student_id) === 'present').length
})

const manualLateCount = computed(() => {
  return enrolledStudents.value.filter(s => getManualStatus(s.student_id) === 'late').length
})

const manualAbsentCount = computed(() => {
  return enrolledStudents.value.filter(s => getManualStatus(s.student_id) === 'absent').length
})

// Verificar si hay cambios pendientes
const hasManualChanges = computed(() => {
  return enrolledStudents.value.some(s => getManualStatus(s.student_id) !== null)
})

// Clase CSS para tarjeta de estudiante en modo manual
const getManualStudentCardClass = (studentId: string): string => {
  const status = getManualStatus(studentId)
  switch (status) {
    case 'present':
      return 'bg-green-50 border-green-300'
    case 'late':
      return 'bg-orange-50 border-orange-300'
    case 'absent':
      return 'bg-red-50 border-red-300'
    default:
      return 'bg-white border-gray-200'
  }
}

// Guardar asistencia manual
const saveManualAttendance = async () => {
  if (!selectedClassId.value) return
  
  savingManual.value = true
  try {
    const selectedClass = activeClasses.value.find(c => c.id === Number(selectedClassId.value))
    if (!selectedClass) throw new Error('Clase no encontrada')
    
    const classId = selectedClass.class_id || `CLASS-${selectedClass.id}`
    
    // Preparar registros a guardar
    const records = enrolledStudents.value
      .filter(student => getManualStatus(student.student_id) !== null)
      .map(student => ({
        student_id: student.student_id,
        status: getManualStatus(student.student_id)
      }))
    
    if (records.length === 0) {
      alert('No hay registros para guardar')
      return
    }
    
    // Guardar cada registro
    let successCount = 0
    let errorCount = 0
    
    for (const record of records) {
      try {
        await attendanceService.registerManualAttendance({
          class_id: classId,
          student_id: record.student_id,
          status: record.status as string
        })
        successCount++
      } catch (error) {
        console.error(`Error registrando asistencia para ${record.student_id}:`, error)
        errorCount++
      }
    }
    
    if (successCount > 0) {
      alert(`✅ Asistencia guardada: ${successCount} registros exitosos${errorCount > 0 ? `, ${errorCount} errores` : ''}`)
      await loadAttendanceRecords()
    } else {
      alert('❌ No se pudo guardar ningún registro')
    }
    
  } catch (error: any) {
    console.error('Error guardando asistencia manual:', error)
    alert('Error al guardar: ' + (error.response?.data?.detail || error.message))
  } finally {
    savingManual.value = false
  }
}

const presentCount = computed(() => {
  if (attendanceMode.value === 'manual') {
    return manualPresentCount.value
  }
  return attendanceRecords.value.length
})

const isStudentPresent = (studentId: string): boolean => {
  if (attendanceMode.value === 'manual') {
    const status = getManualStatus(studentId)
    return status === 'present' || status === 'late'
  }
  return attendanceRecords.value.some(record => record.student_id.toString() === studentId)
}

const getStudentStatus = (studentId: string): string => {
  // If manual mode, use manual selection
  if (attendanceMode.value === 'manual') {
    return getManualStatus(studentId) || 'absent'
  }
  const record = attendanceRecords.value.find(r => r.student_id.toString() === studentId)
  if (!record) return 'absent'
  return (record as any).status || 'present'
}

const getStudentAttendanceTime = (studentId: string): string => {
  const record = attendanceRecords.value.find(r => r.student_id.toString() === studentId)
  return record ? formatTime(record.timestamp) : ''
}

const getStudentCardClass = (studentId: string): string => {
  if (isStudentPresent(studentId)) {
    const status = getStudentStatus(studentId)
    if (status === 'late') {
      return 'bg-gradient-to-r from-orange-50 to-amber-50 border-orange-300'
    }
    return 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300'
  }
  return 'bg-white border-gray-200'
}

const startCamera = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { 
        facingMode: 'user', 
        width: { ideal: 640 },  // Reducir resolución para mejor rendimiento
        height: { ideal: 480 }
      }
    })
    
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      mediaStream.value = stream
      isCameraActive.value = true
      
      // Iniciar verificación automática
      startAutoVerification()
    }
  } catch (error) {
    console.error('Error accessing camera:', error)
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
  stopAutoVerification()
}

const startAutoVerification = () => {
  autoVerificationEnabled.value = true
  // Verificar cada 5 segundos automáticamente (aumentado para mejor rendimiento)
  verificationIntervalId.value = window.setInterval(() => {
    if (!verifying.value && isCameraActive.value && selectedClassId.value) {
      captureAndVerify()
    }
  }, 5000)
}

const stopAutoVerification = () => {
  autoVerificationEnabled.value = false
  if (verificationIntervalId.value) {
    clearInterval(verificationIntervalId.value)
    verificationIntervalId.value = null
  }
}

const captureAndVerify = async () => {
  if (!videoRef.value || !selectedClassId.value || verifying.value) return

  verifying.value = true
  detectedEmotion.value = null

  try {
    const canvas = document.createElement('canvas')
    canvas.width = videoRef.value.videoWidth
    canvas.height = videoRef.value.videoHeight
    const ctx = canvas.getContext('2d')
    
    if (!ctx) {
      throw new Error('No se pudo obtener el contexto del canvas')
    }

    ctx.drawImage(videoRef.value, 0, 0)
    
    const blob = await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob((b) => {
        if (b) resolve(b)
        else reject(new Error('Error al capturar imagen'))
      }, 'image/jpeg', 0.7)  // Reducir calidad a 0.7 para mejor rendimiento
    })

    const formData = new FormData()
    formData.append('image', blob, 'capture.jpg')
    formData.append('class_id', selectedClassId.value.toString())

    console.log('📸 Verificando asistencia para clase:', selectedClassId.value)
    
    const result = await attendanceService.verifyAttendance(formData)
    
    console.log('✅ Resultado verificación:', result)

    if (result.success) {
      lastVerification.value = result
      await loadAttendanceRecords()
      
      // Capturar emoción si la asistencia fue exitosa y tenemos student_id
      if (result.student_id) {
        try {
          console.log('🎭 Capturando emoción para estudiante:', result.student_id)
          
          const emotionFormData = new FormData()
          emotionFormData.append('image', blob, 'emotion.jpg')
          emotionFormData.append('student_id', result.student_id.toString())
          emotionFormData.append('class_id', selectedClassId.value.toString())
          
          const emotionResult = await emotionsService.analyzeEmotion(emotionFormData)
          console.log('✅ Emoción detectada:', emotionResult)
          
          // La respuesta tiene estructura: { success, message, data: { emotions: [...], raw_data: {...} } }
          const emotions = emotionResult?.data?.emotions || emotionResult?.emotions
          if (emotions && emotions.length > 0) {
            const firstEmotion = emotions[0]
            if (firstEmotion) {
              detectedEmotion.value = {
                emotion: firstEmotion.emotion,
                confidence: firstEmotion.confidence
              }
              console.log('🎭 Emoción guardada en UI:', detectedEmotion.value)
            }
          }
        } catch (emotionError) {
          console.error('❌ Error capturando emoción:', emotionError)
        }
      }
    } else {
      lastVerification.value = {
        success: false,
        message: result.message || 'No se pudo verificar la asistencia'
      }
    }
  } catch (error: any) {
    console.error('❌ Error en verificación:', error)
    lastVerification.value = {
      success: false,
      message: error.response?.data?.detail || 'Error en la verificación'
    }
  } finally {
    verifying.value = false
  }
}

const onClassChange = async () => {
  lastVerification.value = null
  detectedEmotion.value = null
  await loadEnrolledStudents()
  await loadAttendanceRecords()
}

const loadActiveClasses = async () => {
  try {
    // Cargar todas las clases
    const allClasses = await classesService.getClasses()
    console.log('📚 Clases cargadas:', allClasses)
    
    // Ordenar clases por prioridad: En curso > Próximas > Finalizadas
    const sortedClasses = allClasses.sort((a: any, b: any) => {
      const statusA = getClassStatus(a)
      const statusB = getClassStatus(b)
      
      const priority: Record<string, number> = {
        'active': 1,
        'upcoming': 2,
        'finished': 3,
        'unknown': 4
      }
      
      const priorityA = priority[statusA] || 4
      const priorityB = priority[statusB] || 4
      
      if (priorityA !== priorityB) {
        return priorityA - priorityB
      }
      
      // Si tienen la misma prioridad, ordenar por fecha de inicio
      const startA = new Date(a.start_time || 0).getTime()
      const startB = new Date(b.start_time || 0).getTime()
      return startB - startA
    })
    
    activeClasses.value = sortedClasses
    
    console.log('📊 Clases disponibles para asistencia:', activeClasses.value.length)
    
    // Auto-seleccionar: primero una clase en curso, luego próxima, luego cualquiera
    if (route.query.class_id) {
      selectedClassId.value = Number(route.query.class_id)
      await onClassChange()
    } else if (activeClasses.value.length > 0) {
      const activeClass = activeClasses.value.find(c => getClassStatus(c) === 'active')
      const upcomingClass = activeClasses.value.find(c => getClassStatus(c) === 'upcoming')
      const firstClass = activeClasses.value[0]
      
      const classToSelect = activeClass || upcomingClass || firstClass
      if (classToSelect) {
        selectedClassId.value = classToSelect.id
        await onClassChange()
      }
    }
  } catch (error) {
    console.error('❌ Error loading classes:', error)
  }
}

const loadEnrolledStudents = async () => {
  if (!selectedClassId.value) {
    enrolledStudents.value = []
    return
  }

  loadingStudents.value = true
  try {
    // Buscar la clase seleccionada para obtener su course_id
    const selectedClass = activeClasses.value.find(c => c.id === Number(selectedClassId.value))
    
    console.log('🔍 Clase seleccionada:', selectedClass)
    console.log('🔍 Course ID:', selectedClass?.course_id)
    console.log('🔍 Metadata:', selectedClass?.metadata)
    
    if (selectedClass?.course_id) {
      // Cargar solo estudiantes inscritos en el curso de esta clase
      console.log('📚 Cargando estudiantes del curso:', selectedClass.course_id)
      enrolledStudents.value = await enrollmentService.getCourseStudents(selectedClass.course_id)
      console.log('📚 Estudiantes del curso cargados:', enrolledStudents.value.length)
    } else {
      // Si no hay course_id, cargar todos los estudiantes (fallback)
      console.log('⚠️ Clase sin course_id, cargando todos los estudiantes')
      enrolledStudents.value = await enrollmentService.getStudents()
      console.log('📚 Estudiantes cargados:', enrolledStudents.value.length)
    }
  } catch (error) {
    console.error('Error loading students:', error)
    enrolledStudents.value = []
  } finally {
    loadingStudents.value = false
  }
}

const loadAttendanceRecords = async () => {
  if (!selectedClassId.value) return

  try {
    attendanceRecords.value = await attendanceService.getClassAttendance(Number(selectedClassId.value))
    console.log('📋 Registros de asistencia:', attendanceRecords.value.length)
  } catch (error) {
    console.error('Error loading records:', error)
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

const getResultClass = () => {
  if (!lastVerification.value) return ''
  if (!lastVerification.value.success) return 'bg-red-50 border-l-4 border-red-500'
  if (lastVerification.value.already_registered) return 'bg-yellow-50 border-l-4 border-yellow-500'
  if (lastVerification.value.status === 'late') return 'bg-orange-50 border-l-4 border-orange-500'
  return 'bg-green-50 border-l-4 border-green-500'
}

const getTextClass = () => {
  if (!lastVerification.value) return ''
  if (!lastVerification.value.success) return 'text-red-700'
  if (lastVerification.value.already_registered) return 'text-yellow-700'
  if (lastVerification.value.status === 'late') return 'text-orange-700'
  return 'text-green-700'
}

const getResultMessage = () => {
  if (!lastVerification.value) return ''
  if (!lastVerification.value.success) return lastVerification.value.message || 'Estudiante no reconocido'
  if (lastVerification.value.already_registered) return '⚠️ Asistencia ya registrada anteriormente'
  if (lastVerification.value.status === 'late') return '⏰ Asistencia registrada - ATRASADO'
  return '✅ Asistencia registrada - Presente'
}

const getClassStatusLabel = (classItem: any): string => {
  // Verificar si el backend envió el estado
  if (!classItem.end_time || !classItem.start_time) return '(Estado desconocido)'
  
  const now = new Date()
  const startTime = new Date(classItem.start_time)
  const endTime = new Date(classItem.end_time)
  
  // Clase ya terminó
  if (now >= endTime) {
    return '(Finalizada)'
  }
  
  // Clase está en curso
  if (now >= startTime && now < endTime) {
    return '(En curso)'
  }
  
  // Clase aún no comienza
  if (now < startTime) {
    return '(Próxima)'
  }
  
  return '(Estado desconocido)'
}

const getClassStatus = (classItem: any): 'finished' | 'active' | 'upcoming' | 'unknown' => {
  if (!classItem.end_time || !classItem.start_time) return 'unknown'
  
  const now = new Date()
  const startTime = new Date(classItem.start_time)
  const endTime = new Date(classItem.end_time)
  
  if (now >= endTime) return 'finished'
  if (now >= startTime && now < endTime) return 'active'
  if (now < startTime) return 'upcoming'
  
  return 'unknown'
}

const getClassOptionClass = (classItem: any): string => {
  const status = getClassStatus(classItem)
  
  switch (status) {
    case 'active':
      return 'text-green-600 font-semibold'
    case 'upcoming':
      return 'text-blue-600'
    case 'finished':
      return 'text-gray-500'
    default:
      return 'text-gray-700'
  }
}

// ==================== QR Functions ====================

const generateQRCode = async () => {
  if (!selectedClassId.value) return
  
  generatingQR.value = true
  try {
    // Obtener el class_id de la clase seleccionada
    const selectedClass = activeClasses.value.find(c => c.id === Number(selectedClassId.value))
    if (!selectedClass) {
      throw new Error('Clase no encontrada')
    }
    
    const classId = selectedClass.class_id || `CLASS-${selectedClass.id}`
    
    const result = await qrService.generateQR({
      class_id: classId,
      period_number: 1,
      base_url: window.location.origin
    })
    
    qrImageUrl.value = result.qr_image
    qrLink.value = result.attendance_url
    qrToken.value = result.token
    currentQRCode.value = result.current_code
    codeCountdown.value = result.code_remaining_seconds
    qrGenerated.value = true
    
    // Iniciar actualización del código
    startCodeRefresh()
    
  } catch (error: any) {
    console.error('Error generando QR:', error)
    alert('Error al generar el código QR: ' + (error.response?.data?.detail || error.message))
  } finally {
    generatingQR.value = false
  }
}

const regenerateQRCode = () => {
  stopCodeRefresh()
  qrGenerated.value = false
  generateQRCode()
}

// Variable para el polling de asistencia
const attendancePollingId = ref<number | null>(null)

// Función para obtener nuevo código del servidor
const refreshCode = async () => {
  try {
    const selectedClass = activeClasses.value.find(c => c.id === Number(selectedClassId.value))
    if (!selectedClass) return
    
    const classId = selectedClass.class_id || `CLASS-${selectedClass.id}`
    
    const result = await qrService.generateQR({
      class_id: classId,
      period_number: 1,
      base_url: window.location.origin
    })
    
    currentQRCode.value = result.current_code
    codeCountdown.value = result.code_remaining_seconds
  } catch (error) {
    console.error('Error actualizando código:', error)
  }
}

const startCodeRefresh = () => {
  // Actualizar countdown cada segundo y refrescar código cuando llegue a 0
  countdownIntervalId.value = window.setInterval(async () => {
    if (codeCountdown.value > 1) {
      codeCountdown.value--
    } else {
      // Cuando llega a 0, obtener nuevo código automáticamente
      await refreshCode()
    }
  }, 1000)
  
  // Actualizar lista de asistencia cada 5 segundos (para ver nuevos registros por QR)
  attendancePollingId.value = window.setInterval(async () => {
    if (selectedClassId.value) {
      await loadAttendanceRecords()
    }
  }, 5000)
}

const stopCodeRefresh = () => {
  if (countdownIntervalId.value) {
    clearInterval(countdownIntervalId.value)
    countdownIntervalId.value = null
  }
  if (attendancePollingId.value) {
    clearInterval(attendancePollingId.value)
    attendancePollingId.value = null
  }
}

const copyQRLink = () => {
  if (qrLink.value) {
    navigator.clipboard.writeText(qrLink.value)
    alert('Enlace copiado al portapapeles')
  }
}

// Limpiar QR cuando cambie la clase
watch(selectedClassId, () => {
  if (qrGenerated.value) {
    stopCodeRefresh()
    qrGenerated.value = false
    qrImageUrl.value = ''
    currentQRCode.value = ''
  }
})

// Detener cámara/QR cuando cambie de modo
watch(attendanceMode, (newMode) => {
  if (newMode !== 'facial' && isCameraActive.value) {
    stopCamera()
  }
  if (newMode !== 'qr' && qrGenerated.value) {
    stopCodeRefresh()
  }
  // Cargar registros existentes al cambiar a modo manual
  if (newMode === 'manual' && selectedClassId.value) {
    loadExistingManualRecords()
  }
})

// Cargar registros existentes para modo manual (sin períodos)
const loadExistingManualRecords = async () => {
  // Prellenar con registros existentes
  manualAttendance.value = {}
  attendanceRecords.value.forEach(record => {
    const studentId = record.student_id.toString()
    const status = (record as any).status || 'present'
    manualAttendance.value[studentId] = status
  })
}

onMounted(async () => {
  await loadActiveClasses()
})

onUnmounted(() => {
  stopCamera()
  stopCodeRefresh()
})
</script>
