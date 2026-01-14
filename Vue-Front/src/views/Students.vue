/**
 * Smart Classroom AI - Students Management View
 * Estilo inspirado en Moodle
 */
<template>
  <div class="min-h-screen bg-gray-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header Section -->
      <div class="bg-white rounded-lg border border-gray-200 mb-6">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h1 class="text-xl font-semibold text-[#d63031] flex items-center gap-2">
            <FontAwesomeIcon :icon="['fas', 'users']" />
            Gestión de Estudiantes
          </h1>
          <router-link
            to="/enrollment"
            class="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-800 transition-colors text-sm inline-flex items-center gap-2"
          >
            <FontAwesomeIcon :icon="['fas', 'plus']" />
            Registrar Estudiante
          </router-link>
        </div>
        
        <!-- Search -->
        <div class="p-4">
          <div class="flex flex-col sm:flex-row gap-3">
            <div class="flex-1 relative">
              <FontAwesomeIcon :icon="['fas', 'magnifying-glass']" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar por nombre, cédula o email..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#d63031] focus:border-transparent"
              />
            </div>
            <button
              @click="loadStudents"
              class="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors inline-flex items-center gap-2"
            >
              <FontAwesomeIcon :icon="['fas', 'arrows-rotate']" />
              Actualizar
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <LoadingSpinner v-if="loading" :full-height="false" />

      <!-- Empty State -->
      <div v-else-if="filteredStudents.length === 0 && !searchQuery" class="bg-white rounded-lg border border-gray-200 p-12 text-center">
        <div class="text-6xl mb-4 text-gray-300">
          <FontAwesomeIcon :icon="['fas', 'users']" />
        </div>
        <h3 class="text-xl font-semibold text-gray-700 mb-2">No hay estudiantes registrados</h3>
        <p class="text-gray-500 mb-6">Comienza registrando tu primer estudiante</p>
        <router-link
          to="/enrollment"
          class="px-6 py-3 bg-gray-700 text-white rounded hover:bg-gray-800 transition-colors inline-flex items-center gap-2"
        >
          <FontAwesomeIcon :icon="['fas', 'plus']" />
          Registrar Estudiante
        </router-link>
      </div>

      <!-- No Results -->
      <div v-else-if="filteredStudents.length === 0 && searchQuery" class="bg-white rounded-lg border border-gray-200 p-12 text-center">
        <div class="text-5xl mb-4 text-gray-300">
          <FontAwesomeIcon :icon="['fas', 'magnifying-glass']" />
        </div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">No se encontraron resultados</h3>
        <p class="text-gray-500">Intenta con otra búsqueda</p>
      </div>

      <!-- Students Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="student in filteredStudents"
          :key="student.id"
          class="bg-white rounded-lg border border-gray-200 overflow-hidden hover:border-[#d63031] transition-colors"
        >
          <!-- Student Photo -->
          <div class="h-40 bg-[#d63031] flex items-center justify-center">
            <img
              v-if="student.photo_url"
              :src="student.photo_url"
              :alt="student.name"
              class="h-full w-full object-cover"
            />
            <div v-else class="text-white text-5xl font-bold">
              {{ getInitials(student.name) }}
            </div>
          </div>

          <!-- Student Info -->
          <div class="p-4">
            <h3 class="font-semibold text-gray-800 mb-1">{{ student.name || 'Sin nombre' }}</h3>
            <p class="text-sm text-gray-500 mb-1">Cédula: {{ student.student_id }}</p>
            <p class="text-sm text-gray-500 mb-3">{{ student.email || 'Sin email' }}</p>
            
            <div class="text-xs text-gray-400 mb-4">
              Registrado: {{ formatDate(student.created_at || student.enrolled_at) }}
            </div>

            <!-- Actions -->
            <div class="flex gap-2">
              <button
                @click="viewStudentDetails(student)"
                class="flex-1 px-3 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors text-sm"
              >
                Ver Detalles
              </button>
              <button
                @click="confirmDelete(student)"
                class="px-3 py-2 border border-red-200 text-red-600 rounded hover:bg-red-50 transition-colors text-sm"
              >
                <FontAwesomeIcon :icon="['fas', 'trash']" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Student Details Modal -->
      <div
        v-if="selectedStudent"
        class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50"
        @click.self="selectedStudent = null"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h2 class="text-lg font-semibold text-gray-800">Detalles del Estudiante</h2>
            <button
              @click="selectedStudent = null"
              class="text-gray-400 hover:text-gray-600"
            >
              <FontAwesomeIcon :icon="['fas', 'xmark']" class="text-xl" />
            </button>
          </div>

          <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div class="h-56 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
                <img
                  v-if="selectedStudent.photo_url"
                  :src="selectedStudent.photo_url"
                  :alt="selectedStudent.name"
                  class="h-full w-full object-cover"
                />
                <div v-else class="text-gray-300 text-7xl">
                  {{ getInitials(selectedStudent.name) }}
                </div>
              </div>
            </div>

            <div class="space-y-4">
              <div>
                <label class="block text-sm text-gray-500">Nombre Completo</label>
                <p class="font-semibold text-gray-800">{{ selectedStudent.name }}</p>
              </div>

              <div>
                <label class="block text-sm text-gray-500">Cédula</label>
                <p class="font-semibold text-gray-800">{{ selectedStudent.student_id }}</p>
              </div>

              <div>
                <label class="block text-sm text-gray-500">Email</label>
                <p class="font-semibold text-gray-800">{{ selectedStudent.email }}</p>
              </div>

              <div>
                <label class="block text-sm text-gray-500">Fecha de Registro</label>
                <p class="font-semibold text-gray-800">
                  {{ formatDate(selectedStudent.created_at || selectedStudent.enrolled_at) }}
                </p>
              </div>

              <div>
                <label class="block text-sm text-gray-500">Estado del Embedding</label>
                <p class="font-semibold flex items-center gap-2" :class="selectedStudent.has_embedding ? 'text-green-600' : 'text-orange-500'">
                  <span class="w-2 h-2 rounded-full" :class="selectedStudent.has_embedding ? 'bg-green-500' : 'bg-orange-500'"></span>
                  {{ selectedStudent.has_embedding ? 'Registrado' : 'No disponible' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <ConfirmModal
        :show="!!studentToDelete"
        title="Confirmar Eliminación"
        icon="triangle-exclamation"
        icon-color="warning"
        confirm-text="Eliminar"
        confirm-icon="trash"
        :loading="deleting"
        loading-text="Eliminando..."
        @confirm="deleteStudent"
        @cancel="studentToDelete = null"
      >
        <p>
          ¿Estás seguro de que deseas eliminar a <strong>{{ studentToDelete?.name }}</strong>?
          Esta acción no se puede deshacer.
        </p>
      </ConfirmModal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { enrollmentService } from '@/services/enrollment.service'
import type { Student } from '@/types'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'

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
  } catch {
    // Error loading students
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
  } catch {
    alert('Error al eliminar el estudiante')
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadStudents()
})
</script>
