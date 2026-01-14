/**
 * Smart Classroom AI - Dashboard View
 * Estilo inspirado en Moodle
 */
<template>
  <div class="min-h-screen bg-gray-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Welcome Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-800">
          ¡Hola, {{ userName }}! 👋
        </h1>
      </div>

      <!-- Mis Materias Section -->
      <div class="bg-white rounded-lg border border-gray-200 mb-6">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-xl font-semibold text-[#d63031]">Mis Materias</h2>
        </div>
        
        <div class="p-6">
          <!-- Loading State -->
          <LoadingSpinner v-if="loading" text="Cargando materias..." :full-height="false" />

          <!-- Empty State -->
          <div v-else-if="courses.length === 0" class="text-center py-12">
            <div class="text-6xl mb-4 text-gray-300">
              <FontAwesomeIcon :icon="['fas', 'book']" />
            </div>
            <h3 class="text-xl font-semibold text-gray-700 mb-2">No tienes materias registradas</h3>
            <p class="text-gray-500 mb-6">Crea tu primera materia para comenzar a gestionar tus clases</p>
            <button
              @click="showCreateCourseModal = true"
              class="px-6 py-3 bg-gray-700 text-white rounded hover:bg-gray-800 transition-colors inline-flex items-center gap-2"
            >
              <FontAwesomeIcon :icon="['fas', 'plus']" />
              Crear Primera Materia
            </button>
          </div>

          <!-- Courses List -->
          <div v-else>
            <div class="flex justify-between items-center mb-4">
              <div class="flex items-center gap-4">
                <select class="px-3 py-2 border border-gray-300 rounded text-sm text-gray-600 bg-white">
                  <option>Todas las materias</option>
                </select>
              </div>
              <button
                @click="showCreateCourseModal = true"
                class="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-800 transition-colors inline-flex items-center gap-2 text-sm"
              >
                <FontAwesomeIcon :icon="['fas', 'plus']" />
                Nueva Materia
              </button>
            </div>

            <!-- Courses Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <router-link
                v-for="course in courses"
                :key="course.id"
                :to="`/courses/${course.id}`"
                class="group block bg-gray-50 border border-gray-200 rounded-lg p-5 hover:border-[#d63031] hover:bg-white transition-all"
              >
                <div class="flex items-start gap-4">
                  <div class="h-12 w-12 rounded-lg bg-[#d63031] flex items-center justify-center text-white text-xl flex-shrink-0">
                    <FontAwesomeIcon :icon="['fas', 'book-open']" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="font-semibold text-gray-800 group-hover:text-[#d63031] transition-colors truncate">
                      {{ course.course_name }}
                    </h3>
                    <p class="text-sm text-gray-500 mt-1">{{ course.course_code }}</p>
                    <p v-if="course.description" class="text-sm text-gray-500 mt-2 line-clamp-2">
                      {{ course.description }}
                    </p>
                  </div>
                </div>
                <div class="mt-4 pt-3 border-t border-gray-200 flex items-center justify-between text-sm">
                  <span class="text-gray-500">Ver detalles</span>
                  <FontAwesomeIcon :icon="['fas', 'chevron-right']" class="text-gray-400 group-hover:text-[#d63031] transition-colors" />
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Create Course Modal -->
    <div
      v-if="showCreateCourseModal"
      class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50"
      @click.self="showCreateCourseModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 class="text-xl font-semibold text-gray-800">Nueva Materia</h2>
        </div>

        <form @submit.prevent="createCourse" class="p-6">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Nombre de la Materia *
              </label>
              <input
                v-model="newCourse.course_name"
                @input="onCourseNameChange"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#d63031] focus:border-transparent"
                placeholder="Ej: Matemáticas Avanzadas"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Código <span class="text-xs text-gray-400">(automático)</span>
              </label>
              <input
                v-model="newCourse.course_code"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded bg-gray-50 text-gray-500"
                placeholder="Ej: MAT-301"
                readonly
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Descripción <span class="text-xs text-gray-400">(opcional)</span>
              </label>
              <textarea
                v-model="newCourse.description"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#d63031] focus:border-transparent resize-none"
                placeholder="Breve descripción de la materia..."
              ></textarea>
            </div>
          </div>

          <AlertMessage 
            v-if="createError" 
            type="error" 
            :message="createError" 
            class="mt-4"
          />

          <div class="flex gap-3 mt-6">
            <button
              type="button"
              @click="showCreateCourseModal = false"
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="creatingCourse"
              class="flex-1 px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-800 disabled:opacity-50 transition-colors"
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
import { ref, onMounted, reactive, computed } from 'vue'
import { coursesService } from '@/services/courses.service'
import { useAuth } from '@/composables/useAuth'
import type { Course } from '@/types'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import AlertMessage from '@/components/AlertMessage.vue'

const { profile } = useAuth()

const loading = ref(true)
const showCreateCourseModal = ref(false)
const creatingCourse = ref(false)
const createError = ref('')

const courses = ref<Course[]>([])

const userName = computed(() => {
  if (!profile.value?.full_name) return 'Usuario'
  return profile.value.full_name.split(' ')[0] || 'Usuario'
})

const newCourse = reactive({
  course_name: '',
  course_code: '',
  description: ''
})

const generateCourseCode = (courseName: string): string => {
  if (!courseName) return ''
  
  const words = courseName.trim().toUpperCase().split(/\s+/).filter(w => w.length > 0)
  
  if (words.length === 0) return ''
  
  let abbreviation = ''
  if (words.length === 1) {
    abbreviation = words[0]?.substring(0, 3) || 'CUR'
  } else if (words.length === 2) {
    abbreviation = (words[0]?.substring(0, 2) || '') + (words[1]?.substring(0, 2) || '')
  } else {
    abbreviation = words.slice(0, 3).map(w => w?.[0] || '').join('')
  }
  
  const randomNum = Math.floor(100 + Math.random() * 900)
  
  return `${abbreviation}-${randomNum}`
}

const onCourseNameChange = () => {
  if (newCourse.course_name && !newCourse.course_code) {
    newCourse.course_code = generateCourseCode(newCourse.course_name)
  }
}

const loadDashboardData = async () => {
  loading.value = true
  
  try {
    courses.value = await coursesService.getMyCourses()
  } catch {
    // Error loading data
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

onMounted(() => {
  loadDashboardData()
})
</script>
