/**
 * Smart Classroom AI - Students Management View
 */
<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">👥 Gestión de Estudiantes</h1>
          <p class="mt-2 text-sm text-gray-600">
            Administra los estudiantes registrados en el sistema
          </p>
        </div>
        <router-link
          to="/enrollment"
          class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200 font-medium flex items-center"
        >
          <span class="mr-2">➕</span>
          Registrar Nuevo Estudiante
        </router-link>
      </div>

      <!-- Search and Filters -->
      <div class="bg-white rounded-lg shadow-md p-4 mb-6">
        <div class="flex flex-col sm:flex-row gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar por nombre, cédula o email..."
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <button
            @click="loadStudents"
            class="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors duration-200"
          >
            🔄 Actualizar
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredStudents.length === 0 && !searchQuery" class="bg-white rounded-lg shadow-md p-12 text-center">
        <div class="text-6xl mb-4">📚</div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">No hay estudiantes registrados</h2>
        <p class="text-gray-600 mb-6">Comienza registrando tu primer estudiante</p>
        <router-link
          to="/enrollment"
          class="inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200 font-medium"
        >
          ➕ Registrar Estudiante
        </router-link>
      </div>

      <!-- No Results -->
      <div v-else-if="filteredStudents.length === 0 && searchQuery" class="bg-white rounded-lg shadow-md p-12 text-center">
        <div class="text-6xl mb-4">🔍</div>
        <h2 class="text-xl font-bold text-gray-900 mb-2">No se encontraron resultados</h2>
        <p class="text-gray-600">Intenta con otra búsqueda</p>
      </div>

      <!-- Students Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="student in filteredStudents"
          :key="student.id"
          class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200"
        >
          <!-- Student Photo -->
          <div class="h-48 bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center">
            <img
              v-if="student.photo_url"
              :src="student.photo_url"
              :alt="student.name"
              class="h-full w-full object-cover"
            />
            <div v-else class="text-white text-6xl font-bold">
              {{ getInitials(student.name) }}
            </div>
          </div>

          <!-- Student Info -->
          <div class="p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-1">{{ student.name || 'Sin nombre' }}</h3>
            <p class="text-sm text-gray-600 mb-1">Cédula: {{ student.student_id }}</p>
            <p class="text-sm text-gray-600 mb-4">{{ student.email || 'Sin email' }}</p>
            
            <div class="text-xs text-gray-500 mb-4">
              Registrado: {{ formatDate(student.created_at || student.enrolled_at) }}
            </div>

            <!-- Actions -->
            <div class="flex gap-2">
              <button
                @click="viewStudentDetails(student)"
                class="flex-1 px-3 py-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors duration-200 text-sm font-medium"
              >
                Ver Detalles
              </button>
              <button
                @click="confirmDelete(student)"
                class="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors duration-200 text-sm font-medium"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Student Details Modal -->
      <div
        v-if="selectedStudent"
        class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center p-4 z-50"
        @click.self="selectedStudent = null"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
          <div class="flex justify-between items-start mb-4">
            <h2 class="text-2xl font-bold text-gray-900">Detalles del Estudiante</h2>
            <button
              @click="selectedStudent = null"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div class="h-64 bg-gray-100 rounded-lg flex items-center justify-center mb-4">
                <img
                  v-if="selectedStudent.photo_url"
                  :src="selectedStudent.photo_url"
                  :alt="selectedStudent.name"
                  class="h-full w-full object-cover rounded-lg"
                />
                <div v-else class="text-gray-400 text-8xl">
                  {{ getInitials(selectedStudent.name) }}
                </div>
              </div>
            </div>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-600">Nombre Completo</label>
                <p class="text-lg font-semibold text-gray-900">{{ selectedStudent.name }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-600">Cédula</label>
                <p class="text-lg font-semibold text-gray-900">{{ selectedStudent.student_id }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-600">Email</label>
                <p class="text-lg font-semibold text-gray-900">{{ selectedStudent.email }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-600">Fecha de Registro</label>
                <p class="text-lg font-semibold text-gray-900">
                  {{ formatDate(selectedStudent.created_at || selectedStudent.enrolled_at) }}
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-600">Estado del Embedding</label>
                <p class="text-lg font-semibold" :class="selectedStudent.has_embedding ? 'text-green-600' : 'text-red-600'">
                  {{ selectedStudent.has_embedding ? '✅ Registrado' : '❌ No disponible' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div
        v-if="studentToDelete"
        class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center p-4 z-50"
        @click.self="studentToDelete = null"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Confirmar Eliminación</h2>
          <p class="text-gray-600 mb-6">
            ¿Estás seguro de que deseas eliminar a <strong>{{ studentToDelete.name }}</strong>?
            Esta acción no se puede deshacer.
          </p>
          <div class="flex gap-3">
            <button
              @click="studentToDelete = null"
              class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors duration-200 font-medium"
            >
              Cancelar
            </button>
            <button
              @click="deleteStudent"
              :disabled="deleting"
              class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 font-medium disabled:opacity-50"
            >
              {{ deleting ? 'Eliminando...' : 'Eliminar' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Navbar from '@/components/Navbar.vue'
import { enrollmentService } from '@/services/enrollment.service'
import type { Student } from '@/types'

const loading = ref(true)
const students = ref<Student[]>([])
const searchQuery = ref('')
const selectedStudent = ref<Student | null>(null)
const studentToDelete = ref<Student | null>(null)
const deleting = ref(false)

const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value

  const query = searchQuery.value.toLowerCase()
  return students.value.filter(student =>
    student.name?.toLowerCase().includes(query) ||
    student.student_id?.toLowerCase().includes(query) ||
    student.email?.toLowerCase().includes(query)
  )
})

const loadStudents = async () => {
  loading.value = true
  try {
    students.value = await enrollmentService.getStudents()
  } catch (error) {
    console.error('Error cargando estudiantes:', error)
  } finally {
    loading.value = false
  }
}

const getInitials = (name: string | undefined) => {
  if (!name) return 'U'
  const names = name.split(' ').filter(n => n.length > 0)
  if (names.length === 0) return 'U'
  return names.length > 1
    ? (names[0]?.[0] || '') + (names[1]?.[0] || '')
    : (names[0]?.[0] || 'U')
}

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return 'Fecha desconocida'
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(date)
}

const viewStudentDetails = (student: Student) => {
  selectedStudent.value = student
}

const confirmDelete = (student: Student) => {
  studentToDelete.value = student
}

const deleteStudent = async () => {
  if (!studentToDelete.value) return

  deleting.value = true
  try {
    await enrollmentService.deleteStudent(studentToDelete.value.student_id)
    students.value = students.value.filter(s => s.student_id !== studentToDelete.value!.student_id)
    studentToDelete.value = null
  } catch (error) {
    console.error('Error eliminando estudiante:', error)
    alert('Error al eliminar el estudiante')
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadStudents()
})
</script>
