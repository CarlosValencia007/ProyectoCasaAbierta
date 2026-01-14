/**
 * Smart Classroom AI - Course Detail View
 * Dashboard específico de una materia/curso
 */
<template>
  <div class="min-h-screen bg-gray-50">

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading -->
      <LoadingSpinner v-if="loading" color="primary" />

      <!-- Course Header -->
      <div v-else-if="course" class="mb-8">
        <div class="bg-gradient-to-r from-[#b81a16] to-[#9a1512] rounded-lg shadow-lg p-8 text-white">
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
        <StatsCard
          label="Estudiantes"
          :value="stats.totalStudents"
          icon="users"
          color="blue"
        />
        <StatsCard
          label="Sesiones"
          :value="stats.totalSessions"
          icon="calendar-days"
          color="green"
        />
        <StatsCard
          label="Asistencia"
          :value="stats.avgAttendance"
          suffix="%"
          icon="circle-check"
          color="yellow"
        />
        <StatsCard
          label="Engagement"
          :value="stats.avgEngagement"
          suffix="%"
          icon="face-smile"
          color="purple"
        />
      </div>

      <!-- Quick Actions -->
      <div class="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <h2 class="text-xl font-semibold text-[#d63031] mb-4">
          Acciones Rapidas
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            @click="openAddStudentModal"
            class="flex items-center p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 hover:border-gray-300 transition-all duration-200"
          >
            <span class="text-2xl mr-3 text-gray-600">
              <FontAwesomeIcon :icon="['fas', 'user-plus']" />
            </span>
            <div class="text-left">
              <p class="font-medium text-gray-800">Anadir Estudiante</p>
              <p class="text-xs text-gray-500">De los registrados</p>
            </div>
          </button>

          <button
            @click="openCreateSessionModal"
            class="flex items-center p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 hover:border-gray-300 transition-all duration-200"
          >
            <span class="text-2xl mr-3 text-gray-600">
              <FontAwesomeIcon :icon="['fas', 'file-pen']" />
            </span>
            <div class="text-left">
              <p class="font-medium text-gray-800">Iniciar Sesion</p>
              <p class="text-xs text-gray-500">Nueva clase</p>
            </div>
          </button>

          <button
            @click="$router.push(`/courses/${courseId}/attendance`)"
            class="flex items-center p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 hover:border-gray-300 transition-all duration-200"
          >
            <span class="text-2xl mr-3 text-gray-600">
              <FontAwesomeIcon :icon="['fas', 'camera']" />
            </span>
            <div class="text-left">
              <p class="font-medium text-gray-800">Tomar Asistencia</p>
              <p class="text-xs text-gray-500">Verificacion facial</p>
            </div>
          </button>

          <button
            @click="$router.push(`/courses/${courseId}/emotions`)"
            class="flex items-center p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 hover:border-gray-300 transition-all duration-200"
          >
            <span class="text-2xl mr-3 text-gray-600">
              <FontAwesomeIcon :icon="['fas', 'masks-theater']" />
            </span>
            <div class="text-left">
              <p class="font-medium text-gray-800">Analizar Emociones</p>
              <p class="text-xs text-gray-500">Estado emocional</p>
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
                'px-6 py-4 font-medium text-sm transition-colors inline-flex items-center gap-2',
                activeTab === tab.id
                  ? 'border-b-2 border-[#b81a16] text-[#b81a16]'
                  : 'text-gray-500 hover:text-gray-700'
              ]"
            >
              <FontAwesomeIcon :icon="['fas', tab.icon]" />
              {{ tab.label }}
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- Students Tab -->
          <div v-if="activeTab === 'students'">
            <!-- Header con boton de anadir -->
            <div class="flex justify-between items-center mb-4">
              <p class="text-sm text-gray-600">{{ students.length }} estudiantes inscritos</p>
              <button
                @click="openAddStudentModal"
                class="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 text-sm font-medium inline-flex items-center gap-2"
              >
                <FontAwesomeIcon :icon="['fas', 'plus']" />
                Anadir Estudiante
              </button>
            </div>

            <div v-if="students.length === 0" class="text-center py-12 text-gray-500">
              <div class="text-6xl mb-4 text-gray-300">
                <FontAwesomeIcon :icon="['fas', 'users']" />
              </div>
              <p class="text-lg mb-2">No hay estudiantes en esta materia</p>
              <p class="text-sm mb-4 text-gray-400">
                Los estudiantes deben ser registrados por la secretaria antes de anadirlos aqui
              </p>
              <button
                @click="openAddStudentModal"
                class="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-800 inline-flex items-center gap-2"
              >
                <FontAwesomeIcon :icon="['fas', 'plus']" />
                Anadir Estudiantes Registrados
              </button>
            </div>
            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="student in students"
                :key="student.student_id"
                class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 group"
              >
                <div class="h-12 w-12 rounded-full bg-[#b81a16] flex items-center justify-center text-white font-bold mr-3 overflow-hidden">
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
              <div class="text-6xl mb-4 text-gray-300">
                <FontAwesomeIcon :icon="['fas', 'calendar-days']" />
              </div>
              <p class="text-lg mb-4">No hay sesiones de clase</p>
              <button
                @click="openCreateSessionModal"
                class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 inline-flex items-center gap-2"
              >
                <FontAwesomeIcon :icon="['fas', 'file-pen']" />
                Crear Primera Sesion
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

    <!-- Modal: Anadir Estudiante -->
    <div
      v-if="showAddStudentModal"
      class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center z-50"
      @click.self="showAddStudentModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4 max-h-[80vh] overflow-hidden flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
            <FontAwesomeIcon :icon="['fas', 'plus']" class="text-[#b81a16]" />
            Anadir Estudiante a la Materia
          </h3>
          <button @click="showAddStudentModal = false" class="text-gray-400 hover:text-gray-600">
            <FontAwesomeIcon :icon="['fas', 'xmark']" />
          </button>
        </div>
        
        <!-- Campo de busqueda -->
        <div class="mb-4">
          <div class="relative">
            <FontAwesomeIcon :icon="['fas', 'magnifying-glass']" class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              v-model="studentSearchQuery"
              type="text"
              placeholder="Buscar por nombre, cedula o email..."
              class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#b81a16] focus:border-transparent"
            />
            <button
              v-if="studentSearchQuery"
              @click="studentSearchQuery = ''"
              class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <FontAwesomeIcon :icon="['fas', 'xmark']" />
            </button>
          </div>
        </div>
        
        <div v-if="availableStudents.length === 0" class="text-center py-8 text-gray-500">
          <div class="text-5xl mb-4 text-gray-300">
            <FontAwesomeIcon :icon="['fas', 'inbox']" />
          </div>
          <p class="text-lg mb-2">No hay estudiantes disponibles</p>
          <p class="text-sm">Todos los estudiantes ya estan inscritos en esta materia</p>
          <p class="text-xs text-gray-400 mt-2 flex items-center justify-center gap-1">
            <FontAwesomeIcon :icon="['fas', 'lightbulb']" class="text-yellow-500" />
            Contacta a la secretaria para registrar nuevos estudiantes
          </p>
        </div>
        
        <div v-else-if="filteredAvailableStudents.length === 0" class="text-center py-8 text-gray-500">
          <div class="text-5xl mb-4 text-gray-300">
            <FontAwesomeIcon :icon="['fas', 'magnifying-glass']" />
          </div>
          <p class="text-lg mb-2">No se encontraron resultados</p>
          <p class="text-sm">Prueba con otro termino de busqueda</p>
        </div>
        
        <div v-else class="flex-1 overflow-y-auto space-y-2">
          <p class="text-sm text-gray-600 mb-3">
            {{ filteredAvailableStudents.length }} de {{ availableStudents.length }} estudiantes
          </p>
          <div
            v-for="student in filteredAvailableStudents"
            :key="student.student_id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
          >
            <div class="flex items-center">
              <div class="h-10 w-10 rounded-full bg-[#b81a16] flex items-center justify-center text-white font-bold mr-3 overflow-hidden">
                <img v-if="student.photo_url" :src="student.photo_url" :alt="student.name" class="w-full h-full object-cover" />
                <span v-else>{{ getInitials(student.name) }}</span>
              </div>
              <div>
                <p class="font-semibold text-gray-900">{{ student.name }}</p>
                <p class="text-xs text-gray-600">Cédula: {{ student.student_id }}</p>
                <p v-if="student.email" class="text-xs text-gray-400">{{ student.email }}</p>
              </div>
            </div>
            <button
              @click="enrollStudent(student.student_id)"
              :disabled="addingStudent"
              class="px-3 py-1 bg-gray-700 text-white rounded-lg hover:bg-gray-800 text-sm font-medium disabled:opacity-50"
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
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#b81a16] focus:border-transparent"
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
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#b81a16] focus:border-transparent"
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
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#b81a16] focus:border-transparent"
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
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#b81a16] focus:border-transparent"
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
              class="flex-1 px-6 py-3 bg-[#b81a16] text-white rounded-lg hover:bg-[#9a1512] font-medium"
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElNotification } from 'element-plus'
import { coursesService } from '@/services/courses.service'
import { classesService } from '@/services/classes.service'
import { enrollmentsService, type EnrolledStudent, type AvailableStudent } from '@/services/enrollments.service'
import statisticsService from '@/services/statistics.service'
import { supabase } from '@/services/supabase'
import type { Course, Student, ClassSession } from '@/types'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import StatsCard from '@/components/StatsCard.vue'

const route = useRoute()
const router = useRouter()

const courseId = route.params.id as string

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
const studentSearchQuery = ref('')

// Filtrar estudiantes disponibles por búsqueda
const filteredAvailableStudents = computed(() => {
  if (!studentSearchQuery.value.trim()) {
    return availableStudents.value
  }
  
  const query = studentSearchQuery.value.toLowerCase().trim()
  return availableStudents.value.filter(student => {
    const name = (student.name || '').toLowerCase()
    const studentId = (student.student_id || '').toLowerCase()
    const email = (student.email || '').toLowerCase()
    
    return name.includes(query) || studentId.includes(query) || email.includes(query)
  })
})

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
  { id: 'students', label: 'Estudiantes', icon: 'users' },
  { id: 'sessions', label: 'Sesiones', icon: 'calendar-days' },
  { id: 'activity', label: 'Actividad', icon: 'chart-bar' }
]

const loadCourseData = async () => {
  loading.value = true
  try {
    // Load course
    course.value = await coursesService.getCourse(courseId)

    // Load students enrolled in this course using enrollments service
    students.value = await enrollmentsService.getCourseStudents(courseId)
    stats.value.totalStudents = students.value.length

    // Load sessions of this course only
    // Note: course_id is stored in metadata field
    const { data: allSessionsData, error: sessionsError } = await supabase
      .from('class_sessions')
      .select('*')
      .order('created_at', { ascending: false })
    
    // Filter sessions by course_id in metadata
    sessions.value = (allSessionsData || []).filter(session => {
      const metadata = session.metadata as { course_id?: string } | null
      return metadata?.course_id === courseId
    })
    
    stats.value.totalSessions = sessions.value.length

    // Cargar estadísticas reales del curso (usando UUID, no int)
    try {
      const courseStats = await statisticsService.getCourseStats(courseId as any)
      stats.value.avgAttendance = courseStats.avgAttendance || 0
      stats.value.avgEngagement = courseStats.avgEngagement || 0
    } catch {
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
  } catch {
    // Error loading course data
  } finally {
    loading.value = false
  }
}

// Cargar estudiantes disponibles para inscribir
const loadAvailableStudents = async () => {
  try {
    availableStudents.value = await enrollmentsService.getAvailableStudents(courseId)
  } catch {
    // Error loading available students
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
  studentSearchQuery.value = '' // Resetear búsqueda
  await loadAvailableStudents()
  showAddStudentModal.value = true
}

const createSession = async () => {
  if (!course.value) {
    ElNotification({
      title: 'Error',
      message: 'No se pudo cargar la información del curso',
      type: 'error'
    })
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

  try {
    loading.value = true
    
    // Generar un ID único para la clase basado en la fecha/hora seleccionada
    const sessionDateTime = new Date(`${sessionForm.date}T${sessionForm.startTime}`)
    const timestamp = sessionDateTime.getTime()
    const classId = `${course.value.course_code}-${timestamp}`
    
    // Crear la sesión usando el servicio de clases
    const response = await classesService.createClass({
      class_id: classId,
      class_name: sessionForm.name.trim(),
      course_id: courseId.toString(),
      start_time: sessionDateTime.toISOString(),
      instructor: undefined,
      room: undefined
    })

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
