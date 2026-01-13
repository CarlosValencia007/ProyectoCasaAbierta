/**
 * Smart Classroom AI - Classes Management View
 */
<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">📅 Gestión de Clases</h1>
          <p class="mt-2 text-sm text-gray-600">
            Crea y administra sesiones de clase
          </p>
        </div>
        <button
          @click="showCreateModal = true"
          class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200 font-medium flex items-center"
        >
          <span class="mr-2">➕</span>
          Nueva Clase
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="classes.length === 0" class="bg-white rounded-lg shadow-md p-12 text-center">
        <div class="text-6xl mb-4">📚</div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">No hay clases creadas</h2>
        <p class="text-gray-600 mb-6">Crea tu primera sesión de clase</p>
        <button
          @click="showCreateModal = true"
          class="inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200 font-medium"
        >
          ➕ Nueva Clase
        </button>
      </div>

      <!-- Classes List -->
      <div v-else class="space-y-6">
        <!-- Active Classes -->
        <div v-if="activeClasses.length > 0">
          <h2 class="text-xl font-bold text-gray-900 mb-4">🟢 Clases Activas</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div
              v-for="classItem in activeClasses"
              :key="classItem.id"
              class="bg-white rounded-lg shadow-md overflow-hidden border-l-4 border-green-500 hover:shadow-lg transition-shadow duration-200"
            >
              <div class="p-6">
                <div class="flex justify-between items-start mb-4">
                  <h3 class="text-lg font-bold text-gray-900">{{ classItem.class_name }}</h3>
                  <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded">
                    En curso
                  </span>
                </div>

                <div class="space-y-2 text-sm text-gray-600 mb-4">
                  <p>📅 Inicio: {{ formatDateTime(classItem.start_time) }}</p>
                  <p>⏱️ Duración: {{ getDuration(classItem.start_time) }}</p>
                  <p>🆔 ID: {{ classItem.id }}</p>
                </div>

                <div class="flex gap-2">
                  <router-link
                    :to="`/attendance?class_id=${classItem.id}`"
                    class="flex-1 px-3 py-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors duration-200 text-sm font-medium text-center"
                  >
                    ✅ Asistencia
                  </router-link>
                  <router-link
                    :to="`/emotions?class_id=${classItem.id}`"
                    class="flex-1 px-3 py-2 bg-purple-50 text-purple-600 rounded-lg hover:bg-purple-100 transition-colors duration-200 text-sm font-medium text-center"
                  >
                    😊 Emociones
                  </router-link>
                </div>

                <button
                  @click="confirmEndClass(classItem)"
                  class="w-full mt-2 px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors duration-200 text-sm font-medium"
                >
                  ⏹️ Finalizar Clase
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Past Classes -->
        <div v-if="pastClasses.length > 0">
          <h2 class="text-xl font-bold text-gray-900 mb-4 mt-8">📚 Clases Finalizadas</h2>
          <div class="bg-white rounded-lg shadow-md overflow-hidden">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Clase
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Inicio
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fin
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Duración
                    </th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="classItem in pastClasses" :key="classItem.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ classItem.class_name }}</div>
                      <div class="text-xs text-gray-500">ID: {{ classItem.id }}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {{ formatDateTime(classItem.start_time) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {{ formatDateTime(classItem.end_time!) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {{ getClassDuration(classItem.start_time, classItem.end_time!) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        @click="confirmDeleteClass(classItem)"
                        class="text-red-600 hover:text-red-900"
                      >
                        🗑️ Eliminar
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Create Class Modal -->
      <div
        v-if="showCreateModal"
        class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center p-4 z-50"
        @click.self="showCreateModal = false"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">📝 Nueva Clase</h2>

          <form @submit.prevent="createClass">
            <div class="mb-4">
              <label for="className" class="block text-sm font-medium text-gray-700 mb-2">
                Nombre de la Clase
              </label>
              <input
                id="className"
                v-model="newClassName"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Ej: Matemáticas - Sección A"
              />
            </div>

            <div v-if="createError" class="mb-4 p-3 bg-red-50 border-l-4 border-red-500 rounded">
              <p class="text-sm text-red-700">{{ createError }}</p>
            </div>

            <div class="flex gap-3">
              <button
                type="button"
                @click="showCreateModal = false"
                class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors duration-200 font-medium"
              >
                Cancelar
              </button>
              <button
                type="submit"
                :disabled="creating"
                class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200 font-medium disabled:opacity-50"
              >
                {{ creating ? 'Creando...' : 'Crear Clase' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- End Class Confirmation Modal -->
      <div
        v-if="classToEnd"
        class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center p-4 z-50"
        @click.self="classToEnd = null"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Finalizar Clase</h2>
          <p class="text-gray-600 mb-6">
            ¿Estás seguro de que deseas finalizar la clase <strong>{{ classToEnd.class_name }}</strong>?
          </p>
          <div class="flex gap-3">
            <button
              @click="classToEnd = null"
              class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors duration-200 font-medium"
            >
              Cancelar
            </button>
            <button
              @click="endClass"
              :disabled="ending"
              class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 font-medium disabled:opacity-50"
            >
              {{ ending ? 'Finalizando...' : 'Finalizar' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Delete Class Confirmation Modal -->
      <div
        v-if="classToDelete"
        class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center p-4 z-50"
        @click.self="classToDelete = null"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Eliminar Clase</h2>
          <p class="text-gray-600 mb-6">
            ¿Estás seguro de que deseas eliminar la clase <strong>{{ classToDelete.class_name }}</strong>?
            Esta acción no se puede deshacer.
          </p>
          <div class="flex gap-3">
            <button
              @click="classToDelete = null"
              class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors duration-200 font-medium"
            >
              Cancelar
            </button>
            <button
              @click="deleteClass"
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
import { classesService } from '@/services/classes.service'
import type { ClassSession } from '@/types'

const loading = ref(true)
const classes = ref<ClassSession[]>([])
const showCreateModal = ref(false)
const newClassName = ref('')
const creating = ref(false)
const createError = ref('')
const classToEnd = ref<ClassSession | null>(null)
const ending = ref(false)
const classToDelete = ref<ClassSession | null>(null)
const deleting = ref(false)

const activeClasses = computed(() => 
  classes.value.filter(c => !c.end_time)
)

const pastClasses = computed(() => 
  classes.value.filter(c => c.end_time).reverse()
)

const loadClasses = async () => {
  loading.value = true
  try {
    classes.value = await classesService.getClasses()
  } catch (error) {
    console.error('Error cargando clases:', error)
  } finally {
    loading.value = false
  }
}

const createClass = async () => {
  if (!newClassName.value.trim()) return

  creating.value = true
  createError.value = ''

  try {
    await classesService.createClass({ class_name: newClassName.value })
    await loadClasses()
    showCreateModal.value = false
    newClassName.value = ''
  } catch (error: any) {
    createError.value = error.response?.data?.detail || 'Error al crear la clase'
  } finally {
    creating.value = false
  }
}

const confirmEndClass = (classItem: ClassSession) => {
  classToEnd.value = classItem
}

const endClass = async () => {
  if (!classToEnd.value) return

  ending.value = true
  try {
    await classesService.endClass(classToEnd.value.class_id)
    await loadClasses()
    classToEnd.value = null
  } catch (error) {
    console.error('Error finalizando clase:', error)
    alert('Error al finalizar la clase')
  } finally {
    ending.value = false
  }
}

const confirmDeleteClass = (classItem: ClassSession) => {
  classToDelete.value = classItem
}

const deleteClass = async () => {
  if (!classToDelete.value) return

  deleting.value = true
  try {
    await classesService.deleteClass(classToDelete.value.class_id)
    classes.value = classes.value.filter(c => c.class_id !== classToDelete.value!.class_id)
    classToDelete.value = null
  } catch (error) {
    console.error('Error eliminando clase:', error)
    alert('Error al eliminar la clase')
  } finally {
    deleting.value = false
  }
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

const getDuration = (startTime: string) => {
  const start = new Date(startTime)
  const now = new Date()
  const diff = now.getTime() - start.getTime()
  const minutes = Math.floor(diff / 60000)
  return `${minutes} min`
}

const getClassDuration = (startTime: string, endTime: string) => {
  const start = new Date(startTime)
  const end = new Date(endTime)
  const diff = end.getTime() - start.getTime()
  const minutes = Math.floor(diff / 60000)
  return `${minutes} min`
}

onMounted(() => {
  loadClasses()
})
</script>
