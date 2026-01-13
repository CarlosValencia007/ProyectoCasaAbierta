/**
 * Smart Classroom AI - Dashboard View
 */
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Simplified Navbar -->
    <nav class="bg-white shadow-md">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo y Brand -->
          <div class="flex items-center space-x-2">
            <span class="text-3xl">🎓</span>
            <span class="text-xl font-bold text-indigo-600 hidden sm:block">
              Smart Classroom AI
            </span>
          </div>

          <!-- User Menu -->
          <div class="flex items-center space-x-4">
            <div class="hidden sm:flex items-center space-x-2">
              <div class="text-right">
                <p class="text-sm font-medium text-gray-700">
                  {{ userProfile?.full_name || 'Carlos Valencia' }}
                </p>
                <p class="text-xs text-gray-500">{{ userProfile?.email || 'valenciamendozacarlos5@gmail.com' }}</p>
              </div>
              <div class="h-10 w-10 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold">
                CV
              </div>
            </div>
            
            <button
              @click="handleLogout"
              class="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-md hover:bg-red-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              Salir
            </button>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">
          📊 Dashboard General
        </h1>
        <p class="mt-2 text-sm text-gray-600">
          Resumen de actividad y estadísticas del sistema
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Stats Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Total Students -->
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Total Estudiantes</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.totalStudents }}</p>
            </div>
            <div class="text-4xl">👥</div>
          </div>
          <p class="text-xs text-gray-500 mt-2">Estudiantes registrados</p>
        </div>

        <!-- Active Classes -->
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Clases Activas</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.activeClasses }}</p>
            </div>
            <div class="text-4xl">📅</div>
          </div>
          <p class="text-xs text-gray-500 mt-2">Sesiones en curso</p>
        </div>

        <!-- Average Attendance -->
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Asistencia Promedio</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.avgAttendance }}%</p>
            </div>
            <div class="text-4xl">✅</div>
          </div>
          <p class="text-xs text-gray-500 mt-2">Últimas 7 clases</p>
        </div>

        <!-- Engagement Score -->
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Engagement</p>
              <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.avgEngagement }}%</p>
            </div>
            <div class="text-4xl">😊</div>
          </div>
          <p class="text-xs text-gray-500 mt-2">Nivel de participación</p>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-8">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-900">📚 Mis Materias/Cursos</h2>
          <button
            @click="showCreateCourseModal = true"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            ➕ Nueva Materia
          </button>
        </div>

        <div v-if="courses.length === 0" class="text-center py-12 text-gray-500">
          <div class="text-6xl mb-4">📚</div>
          <p class="text-lg mb-4">No tienes materias registradas</p>
          <button
            @click="showCreateCourseModal = true"
            class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            ➕ Crear Primera Materia
          </button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <router-link
            v-for="course in courses"
            :key="course.id"
            :to="`/courses/${course.id}`"
            class="block p-6 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg border-2 border-indigo-200 hover:border-indigo-400 transition-all hover:shadow-lg"
          >
            <div class="flex items-start justify-between mb-3">
              <div>
                <h3 class="text-lg font-bold text-gray-900">{{ course.course_name }}</h3>
                <p class="text-sm text-indigo-600 font-medium">{{ course.course_code }}</p>
              </div>
              <span class="text-3xl">📖</span>
            </div>
            <p v-if="course.description" class="text-sm text-gray-600 mb-3 line-clamp-2">
              {{ course.description }}
            </p>
            <div class="flex items-center justify-between text-xs text-gray-500">
              <span>Click para ver detalles →</span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Recent Classes -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">📅 Clases Recientes</h2>
          <div v-if="recentClasses.length === 0" class="text-center py-8 text-gray-500">
            <p>No hay clases recientes</p>
            <router-link
              to="/classes"
              class="text-indigo-600 hover:text-indigo-700 text-sm font-medium mt-2 inline-block"
            >
              Crear primera clase →
            </router-link>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="classItem in recentClasses"
              :key="classItem.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div>
                <p class="font-semibold text-gray-900">{{ classItem.class_name }}</p>
                <p class="text-xs text-gray-600">
                  {{ formatDate(classItem.start_time) }}
                </p>
              </div>
              <span
                :class="[
                  'px-2 py-1 text-xs font-medium rounded',
                  classItem.end_time
                    ? 'bg-gray-200 text-gray-700'
                    : 'bg-green-100 text-green-700'
                ]"
              >
                {{ classItem.end_time ? 'Finalizada' : 'Activa' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Recent Students -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">👥 Estudiantes Recientes</h2>
          <div v-if="recentStudents.length === 0" class="text-center py-8 text-gray-500">
            <p>No hay estudiantes registrados</p>
            <router-link
              to="/enrollment"
              class="text-indigo-600 hover:text-indigo-700 text-sm font-medium mt-2 inline-block"
            >
              Registrar estudiante →
            </router-link>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="student in recentStudents"
              :key="student.id"
              class="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div class="h-10 w-10 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold mr-3">
                {{ getInitials(student.name) }}
              </div>
              <div class="flex-1">
                <p class="font-semibold text-gray-900">{{ student.name }}</p>
                <p class="text-xs text-gray-600">{{ student.student_id }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Course Modal -->
    <div
      v-if="showCreateCourseModal"
      class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center p-4 z-50"
      @click.self="showCreateCourseModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">📚 Nueva Materia/Curso</h2>

        <form @submit.prevent="createCourse">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Nombre de la Materia *
              </label>
              <input
                v-model="newCourse.course_name"
                @input="onCourseNameChange"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Ej: Matemáticas Avanzadas"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Código de la Materia * <span class="text-xs text-gray-500">(se genera automáticamente)</span>
              </label>
              <input
                v-model="newCourse.course_code"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-gray-50"
                placeholder="Ej: MAT-301"
                readonly
              />
              <p class="text-xs text-gray-500 mt-1">
                El código se genera automáticamente a partir del nombre de la materia
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Descripción (opcional)
              </label>
              <textarea
                v-model="newCourse.description"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Breve descripción de la materia..."
              ></textarea>
            </div>
          </div>

          <div v-if="createError" class="mt-4 p-3 bg-red-50 border-l-4 border-red-500 rounded">
            <p class="text-sm text-red-700">{{ createError }}</p>
          </div>

          <div class="flex gap-3 mt-6">
            <button
              type="button"
              @click="showCreateCourseModal = false"
              class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="creatingCourse"
              class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              {{ creatingCourse ? 'Creando...' : 'Crear Materia' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { enrollmentService } from '@/services/enrollment.service'
import { classesService } from '@/services/classes.service'
import { coursesService } from '@/services/courses.service'
import statisticsService from '@/services/statistics.service'
import type { Student, ClassSession, Course } from '@/types'

const router = useRouter()
const loading = ref(true)
const showCreateCourseModal = ref(false)
const creatingCourse = ref(false)
const createError = ref('')
const userProfile = ref<any>(null)

const stats = ref({
  totalStudents: 0,
  activeClasses: 0,
  avgAttendance: 0,
  avgEngagement: 0
})

const courses = ref<Course[]>([])
const recentClasses = ref<ClassSession[]>([])
const recentStudents = ref<Student[]>([])

const newCourse = reactive({
  course_name: '',
  course_code: '',
  description: ''
})

// Auto-generar código de curso basado en el nombre
const generateCourseCode = (courseName: string): string => {
  if (!courseName) return ''
  
  // Dividir el nombre en palabras
  const words = courseName.trim().toUpperCase().split(/\s+/).filter(w => w.length > 0)
  
  if (words.length === 0) return ''
  
  // Tomar primeras 2-3 letras de cada palabra
  let abbreviation = ''
  if (words.length === 1) {
    // Una palabra: tomar las primeras 3 letras
    abbreviation = words[0]?.substring(0, 3) || 'CUR'
  } else if (words.length === 2) {
    // Dos palabras: tomar 2 letras de cada una
    abbreviation = (words[0]?.substring(0, 2) || '') + (words[1]?.substring(0, 2) || '')
  } else {
    // Tres o más palabras: tomar la primera letra de cada una de las 3 primeras
    abbreviation = words.slice(0, 3).map(w => w?.[0] || '').join('')
  }
  
  // Generar número aleatorio de 3 dígitos
  const randomNum = Math.floor(100 + Math.random() * 900)
  
  return `${abbreviation}-${randomNum}`
}

// Actualizar código cuando cambia el nombre
const onCourseNameChange = () => {
  if (newCourse.course_name && !newCourse.course_code) {
    newCourse.course_code = generateCourseCode(newCourse.course_name)
  }
}

const loadDashboardData = async () => {
  loading.value = true
  
  try {
    // Load courses
    courses.value = await coursesService.getMyCourses()
    console.log('📚 Cursos cargados:', courses.value)

    // Cargar estudiantes
    const students = await enrollmentService.getStudents()
    stats.value.totalStudents = students.length
    recentStudents.value = students.slice(-5).reverse()

    // Cargar clases
    const classes = await classesService.getClasses()
    const activeClasses = classes.filter(c => !c.end_time)
    stats.value.activeClasses = activeClasses.length
    recentClasses.value = classes.slice(-5).reverse()

    // Cargar estadísticas reales desde el backend
    const dashboardStats = await statisticsService.getDashboardStats()
    stats.value.avgAttendance = dashboardStats.avgAttendance
    stats.value.avgEngagement = dashboardStats.avgEngagement
  } catch (error) {
    console.error('Error cargando datos del dashboard:', error)
  } finally {
    loading.value = false
  }
}

const createCourse = async () => {
  if (!newCourse.course_name || !newCourse.course_code) return

  creatingCourse.value = true
  createError.value = ''

  try {
    await coursesService.createCourse({
      course_name: newCourse.course_name,
      course_code: newCourse.course_code,
      description: newCourse.description || undefined
    })

    await loadDashboardData()
    
    showCreateCourseModal.value = false
    newCourse.course_name = ''
    newCourse.course_code = ''
    newCourse.description = ''
  } catch (error: any) {
    createError.value = error.message || 'Error al crear la materia'
  } finally {
    creatingCourse.value = false
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-ES', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const getInitials = (name: string) => {
  const names = name.split(' ').filter(n => n.length > 0)
  if (names.length === 0) return 'U'
  return names.length > 1
    ? (names[0]?.[0] || '') + (names[1]?.[0] || '')
    : (names[0]?.[0] || 'U')
}

const handleLogout = async () => {
  if (confirm('¿Estás seguro de que deseas cerrar sesión?')) {
    try {
      const { supabase } = await import('@/services/supabase')
      await supabase.auth.signOut()
      router.push('/login')
    } catch (error) {
      console.error('Error al cerrar sesión:', error)
    }
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>
