/**
 * Smart Classroom AI - Course Detail View
 * Dashboard específico de una materia/curso
 */
<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading -->
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Course Header -->
      <div v-else-if="course" class="mb-8">
        <div class="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-8 text-white">
          <div class="flex justify-between items-start">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <router-link to="/dashboard" class="text-white/80 hover:text-white">
                  ← Dashboard
                </router-link>
                <span class="text-white/50">/</span>
                <span>{{ course.course_code }}</span>
              </div>
              <h1 class="text-4xl font-bold mb-2">{{ course.course_name }}</h1>
              <p v-if="course.description" class="text-white/90">{{ course.description }}</p>
              <p class="text-sm text-white/70 mt-2">Código: {{ course.course_code }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Grid -->
      <div v-if="!loading" class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Estudiantes</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.totalStudents }}</p>
            </div>
            <div class="text-4xl">👥</div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Sesiones</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.totalSessions }}</p>
            </div>
            <div class="text-4xl">📅</div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Asistencia</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.avgAttendance }}%</p>
            </div>
            <div class="text-4xl">✅</div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Engagement</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.avgEngagement }}%</p>
            </div>
            <div class="text-4xl">😊</div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 class="text-xl font-bold text-gray-900 mb-4">🚀 Acciones Rápidas</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            @click="$router.push(`/courses/${courseId}/enrollment`)"
            class="flex items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors duration-200"
          >
            <span class="text-3xl mr-3">➕</span>
            <div class="text-left">
              <p class="font-semibold text-gray-900">Registrar Estudiante</p>
              <p class="text-xs text-gray-600">Nuevo estudiante</p>
            </div>
          </button>

          <button
            @click="openCreateSessionModal"
            class="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors duration-200"
          >
            <span class="text-3xl mr-3">📝</span>
            <div class="text-left">
              <p class="font-semibold text-gray-900">Iniciar Sesión</p>
              <p class="text-xs text-gray-600">Nueva clase</p>
            </div>
          </button>

          <button
            @click="$router.push(`/courses/${courseId}/attendance`)"
            class="flex items-center p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors duration-200"
          >
            <span class="text-3xl mr-3">📸</span>
            <div class="text-left">
              <p class="font-semibold text-gray-900">Tomar Asistencia</p>
              <p class="text-xs text-gray-600">Verificación facial</p>
            </div>
          </button>

          <button
            @click="$router.push(`/courses/${courseId}/emotions`)"
            class="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors duration-200"
          >
            <span class="text-3xl mr-3">🎭</span>
            <div class="text-left">
              <p class="font-semibold text-gray-900">Analizar Emociones</p>
              <p class="text-xs text-gray-600">Estado emocional</p>
            </div>
          </button>
        </div>
      </div>

      <!-- Content Tabs -->
      <div class="bg-white rounded-lg shadow-md">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'px-6 py-4 font-medium text-sm transition-colors',
                activeTab === tab.id
                  ? 'border-b-2 border-indigo-500 text-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              ]"
            >
              {{ tab.icon }} {{ tab.label }}
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- Students Tab -->
          <div v-if="activeTab === 'students'">
            <!-- Header con botón de añadir -->
            <div class="flex justify-between items-center mb-4">
              <p class="text-sm text-gray-600">{{ students.length }} estudiantes inscritos</p>
              <button
                @click="openAddStudentModal"
                class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium"
              >
                ➕ Añadir Estudiante
              </button>
            </div>

            <div v-if="students.length === 0" class="text-center py-12 text-gray-500">
              <div class="text-6xl mb-4">👥</div>
              <p class="text-lg mb-2">No hay estudiantes en esta materia</p>
              <p class="text-sm mb-4">Los estudiantes deben estar registrados primero en el sistema</p>
              <div class="flex justify-center gap-3">
                <button
                  @click="$router.push('/enrollment')"
                  class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  📝 Registrar Nuevo Estudiante
                </button>
                <button
                  @click="openAddStudentModal"
                  class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  ➕ Añadir Existente
                </button>
              </div>
            </div>
            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="student in students"
                :key="student.student_id"
                class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 group"
              >
                <div class="h-12 w-12 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold mr-3 overflow-hidden">
                  <img v-if="student.photo_url" :src="student.photo_url" :alt="student.name" class="w-full h-full object-cover" />
                  <span v-else>{{ getInitials(student.name) }}</span>
                </div>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900">{{ student.name }}</p>
                  <p class="text-xs text-gray-600">Cédula: {{ student.student_id }}</p>
                </div>
                <button
                  @click="unenrollStudent(student.student_id, student.name)"
                  class="opacity-0 group-hover:opacity-100 p-2 text-red-500 hover:bg-red-50 rounded-lg transition-all"
                  title="Quitar de la materia"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>

          <!-- Sessions Tab -->
          <div v-if="activeTab === 'sessions'">
            <div v-if="sessions.length === 0" class="text-center py-12 text-gray-500">
              <div class="text-6xl mb-4">📅</div>
              <p class="text-lg mb-4">No hay sesiones de clase</p>
              <button
                @click="openCreateSessionModal"
                class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                📝 Crear Primera Sesión
              </button>
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="session in sessions"
                :key="session.id"
                class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div>
                  <p class="font-semibold text-gray-900">{{ session.class_name }}</p>
                  <p class="text-sm text-gray-600">{{ formatDateTime(session.start_time) }}</p>
                </div>
                <span
                  :class="[
                    'px-3 py-1 text-sm font-medium rounded',
                    session.end_time ? 'bg-gray-200 text-gray-700' : 'bg-green-100 text-green-700'
                  ]"
                >
                  {{ session.end_time ? 'Finalizada' : 'Activa' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Activity Tab -->
          <div v-if="activeTab === 'activity'">
            <p class="text-gray-600">Historial de actividad próximamente...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Añadir Estudiante -->
    <div
      v-if="showAddStudentModal"
      class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center z-50"
      @click.self="showAddStudentModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4 max-h-[80vh] overflow-hidden flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-bold text-gray-900">➕ Añadir Estudiante a la Materia</h3>
          <button @click="showAddStudentModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        
        <div v-if="availableStudents.length === 0" class="text-center py-8 text-gray-500">
          <div class="text-5xl mb-4">📭</div>
          <p class="text-lg mb-2">No hay estudiantes disponibles</p>
          <p class="text-sm">Todos los estudiantes ya están inscritos o no hay estudiantes registrados</p>
          <button
            @click="$router.push('/enrollment'); showAddStudentModal = false"
            class="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            📝 Registrar Nuevo Estudiante
          </button>
        </div>
        
        <div v-else class="flex-1 overflow-y-auto space-y-2">
          <p class="text-sm text-gray-600 mb-3">{{ availableStudents.length }} estudiantes disponibles</p>
          <div
            v-for="student in availableStudents"
            :key="student.student_id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
          >
            <div class="flex items-center">
              <div class="h-10 w-10 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold mr-3 overflow-hidden">
                <img v-if="student.photo_url" :src="student.photo_url" :alt="student.name" class="w-full h-full object-cover" />
                <span v-else>{{ getInitials(student.name) }}</span>
              </div>
              <div>
                <p class="font-semibold text-gray-900">{{ student.name }}</p>
                <p class="text-xs text-gray-600">Cédula: {{ student.student_id }}</p>
              </div>
            </div>
            <button
              @click="enrollStudent(student.student_id)"
              :disabled="addingStudent"
              class="px-3 py-1 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium disabled:opacity-50"
            >
              {{ addingStudent ? '...' : '+ Añadir' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Crear Sesión -->
    <div
      v-if="showCreateSessionModal"
      class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center z-50"
      @click.self="showCreateSessionModal = false"
    >
      <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4">
        <h3 class="text-2xl font-bold text-gray-900 mb-6">Nueva Sesión de Clase</h3>
        
        <form @submit.prevent="createSession" class="space-y-4">
          <!-- Nombre de la sesión -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Nombre de la Sesión *
            </label>
            <input
              v-model="sessionForm.name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Ej: Clase de Introducción"
              required
            />
          </div>

          <!-- Fecha -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Fecha *
            </label>
            <input
              v-model="sessionForm.date"
              type="date"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <!-- Hora de Inicio -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Hora de Inicio *
            </label>
            <input
              v-model="sessionForm.startTime"
              type="time"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <!-- Hora de Fin (Opcional) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Hora de Fin (Opcional)
            </label>
            <input
              v-model="sessionForm.endTime"
              type="time"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <!-- Botones -->
          <div class="flex gap-3 mt-6">
            <button
              type="button"
              @click="showCreateSessionModal = false"
              class="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
            >
              Crear Sesión
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElNotification } from 'element-plus'
import Navbar from '@/components/Navbar.vue'
import { coursesService } from '@/services/courses.service'
import { classesService } from '@/services/classes.service'
import { enrollmentsService, type EnrolledStudent, type AvailableStudent } from '@/services/enrollments.service'
import statisticsService from '@/services/statistics.service'
import { supabase } from '@/services/supabase'
import type { Course, Student, ClassSession } from '@/types'

const route = useRoute()
const router = useRouter()

const courseId = route.params.id as string

console.log('🔍 CourseId:', courseId)

const loading = ref(true)
const course = ref<Course | null>(null)
const activeTab = ref('students')
const students = ref<EnrolledStudent[]>([])
const availableStudents = ref<AvailableStudent[]>([])
const sessions = ref<ClassSession[]>([])
const recentActivity = ref<Array<{ id: string; type: string; message: string; timestamp: string }>>([])

// Modal para añadir estudiantes
const showAddStudentModal = ref(false)
const addingStudent = ref(false)

const showCreateSessionModal = ref(false)
const sessionForm = reactive({
  name: '',
  date: '',
  startTime: '',
  endTime: ''
})

const stats = ref({
  totalStudents: 0,
  totalSessions: 0,
  avgAttendance: 0,
  avgEngagement: 0
})

const tabs = [
  { id: 'students', label: 'Estudiantes', icon: '👥' },
  { id: 'sessions', label: 'Sesiones', icon: '📅' },
  { id: 'activity', label: 'Actividad', icon: '📊' }
]

const loadCourseData = async () => {
  loading.value = true
  try {
    // Load course
    course.value = await coursesService.getCourse(courseId)

    // Load students enrolled in this course using enrollments service
    students.value = await enrollmentsService.getCourseStudents(courseId)
    stats.value.totalStudents = students.value.length
    console.log('👥 Estudiantes inscritos:', students.value)

    // Load sessions of this course only
    // Note: course_id is stored in metadata field
    const { data: allSessionsData, error: sessionsError } = await supabase
      .from('class_sessions')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (sessionsError) {
      console.error('Error loading sessions:', sessionsError)
    }
    
    // Filter sessions by course_id in metadata
    sessions.value = (allSessionsData || []).filter(session => {
      const metadata = session.metadata as { course_id?: string } | null
      return metadata?.course_id === courseId
    })
    
    console.log('📅 Sessions loaded:', sessions.value)
    stats.value.totalSessions = sessions.value.length

    // Cargar estadísticas reales del curso (usando UUID, no int)
    try {
      const courseStats = await statisticsService.getCourseStats(courseId as any)
      stats.value.avgAttendance = courseStats.avgAttendance || 0
      stats.value.avgEngagement = courseStats.avgEngagement || 0
    } catch (statsError) {
      console.warn('No se pudieron cargar estadísticas:', statsError)
      stats.value.avgAttendance = 0
      stats.value.avgEngagement = 0
    }

    // Mock activity
    recentActivity.value = [
      {
        id: '1',
        type: 'session',
        message: 'Sesiones de clase registradas',
        timestamp: new Date().toISOString()
      },
      {
        id: '2',
        type: 'student',
        message: `${students.value.length} estudiantes en esta materia`,
        timestamp: new Date().toISOString()
      }
    ]
  } catch (error) {
    console.error('Error loading course data:', error)
  } finally {
    loading.value = false
  }
}

// Cargar estudiantes disponibles para inscribir
const loadAvailableStudents = async () => {
  try {
    availableStudents.value = await enrollmentsService.getAvailableStudents(courseId)
  } catch (error) {
    console.error('Error loading available students:', error)
  }
}

// Inscribir estudiante al curso
const enrollStudent = async (studentId: string) => {
  addingStudent.value = true
  try {
    await enrollmentsService.enrollStudent(studentId, courseId)
    ElNotification({
      title: 'Éxito',
      message: 'Estudiante inscrito exitosamente',
      type: 'success'
    })
    // Recargar datos
    await loadCourseData()
    await loadAvailableStudents()
  } catch (error: any) {
    ElNotification({
      title: 'Error',
      message: error.response?.data?.detail || 'Error al inscribir estudiante',
      type: 'error'
    })
  } finally {
    addingStudent.value = false
  }
}

// Desinscribir estudiante del curso
const unenrollStudent = async (studentId: string, studentName: string) => {
  if (!confirm(`¿Seguro que deseas quitar a ${studentName} de esta materia?`)) return
  
  try {
    await enrollmentsService.unenrollStudent(courseId, studentId)
    ElNotification({
      title: 'Éxito',
      message: 'Estudiante removido de la materia',
      type: 'success'
    })
    await loadCourseData()
  } catch (error: any) {
    ElNotification({
      title: 'Error',
      message: error.response?.data?.detail || 'Error al remover estudiante',
      type: 'error'
    })
  }
}

// Abrir modal de añadir estudiantes
const openAddStudentModal = async () => {
  await loadAvailableStudents()
  showAddStudentModal.value = true
}

const createSession = async () => {
  console.log('🔥 createSession called!')
  console.log('Course:', course.value)
  
  if (!course.value) {
    alert('⚠️ No se pudo cargar la información del curso')
    return
  }
  
  if (!sessionForm.name || !sessionForm.date || !sessionForm.startTime) {
    ElNotification({
      title: 'Error',
      message: 'Completa todos los campos requeridos',
      type: 'warning'
    })
    return
  }
  
  console.log('Session form:', sessionForm)

  try {
    loading.value = true
    
    // Generar un ID único para la clase basado en la fecha/hora seleccionada
    const sessionDateTime = new Date(`${sessionForm.date}T${sessionForm.startTime}`)
    const timestamp = sessionDateTime.getTime()
    const classId = `${course.value.course_code}-${timestamp}`
    
    console.log('📤 Creating session with data:', {
      class_id: classId,
      class_name: sessionForm.name.trim(),
      course_id: courseId.toString(),
      start_time: sessionDateTime.toISOString()
    })
    
    // Crear la sesión usando el servicio de clases
    const response = await classesService.createClass({
      class_id: classId,
      class_name: sessionForm.name.trim(),
      course_id: courseId.toString(),
      start_time: sessionDateTime.toISOString(),
      instructor: undefined,
      room: undefined
    })

    console.log('📥 Response:', response)

    if (response.success) {
      ElNotification({
        title: 'Éxito',
        message: `Sesión "${sessionForm.name}" creada exitosamente`,
        type: 'success'
      })
      
      showCreateSessionModal.value = false
      
      // Recargar los datos
      await loadCourseData()
    } else {
      ElNotification({
        title: 'Error',
        message: 'Error al crear la sesión. Intenta de nuevo.',
        type: 'error'
      })
    }
  } catch (error: any) {
    console.error('❌ Error creando sesión:', error)
    console.error('Error details:', error.response?.data)
    ElNotification({
      title: 'Error',
      message: error.response?.data?.detail || error.message || 'No se pudo crear la sesión',
      type: 'error'
    })
  } finally {
    loading.value = false
  }
}

const getInitials = (name: string) => {
  const names = name.split(' ').filter(n => n.length > 0)
  if (names.length === 0) return 'U'
  return names.length > 1
    ? (names[0]?.[0] || '') + (names[1]?.[0] || '')
    : (names[0]?.[0] || 'U')
}

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-ES', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const openCreateSessionModal = () => {
  const now = new Date()
  const tzOffset = now.getTimezoneOffset() * 60000
  const localDate = new Date(now - tzOffset).toISOString().slice(0, 10)
  const localTime = new Date(now - tzOffset).toISOString().slice(11, 16)
  
  sessionForm.name = ''
  sessionForm.date = localDate
  sessionForm.startTime = localTime
  sessionForm.endTime = ''
  showCreateSessionModal.value = true
}

onMounted(() => {
  loadCourseData()
})
</script>
