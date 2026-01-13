/**
 * Smart Classroom AI - Emotions Analysis View
 */
<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">😊 Análisis Emocional</h1>

      <!-- Combined Emotion Analytics -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">📊 Análisis de Clase</h2>
          <select
            v-model="selectedClassId"
            @change="loadEmotionLogs"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Seleccionar clase...</option>
            <option v-for="classItem in activeClasses" :key="classItem.id" :value="classItem.id">
              {{ classItem.class_name }}
            </option>
          </select>
        </div>

        <!-- Empty State -->
        <div v-if="emotionLogs.length === 0" class="text-center py-16 text-gray-500">
          <div class="text-6xl mb-4">🎭</div>
          <p class="text-xl font-semibold text-gray-900 mb-2">No hay registros aún</p>
          <p class="text-sm">Las emociones se capturan automáticamente al tomar asistencia</p>
        </div>

        <!-- Content with data -->
        <div v-else>
          <!-- Statistics Section -->
          <div class="mb-8">
            <h3 class="text-lg font-bold text-gray-900 mb-4">📈 Resumen Estadístico</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              <div 
                v-for="(count, emotion) in emotionStats" 
                :key="emotion" 
                class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200"
              >
                <div class="text-center">
                  <div class="text-4xl mb-2">{{ getEmotionEmoji(emotion as string) }}</div>
                  <p class="font-semibold text-gray-900 text-sm">{{ getEmotionName(emotion as string) }}</p>
                  <p class="text-2xl font-bold text-purple-600 mt-1">{{ count }}</p>
                  <p class="text-xs text-gray-600">
                    {{ Math.round((count / emotionLogs.length) * 100) }}%
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- History Section -->
          <div class="border-t border-gray-200 pt-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">📋 Historial Detallado</h3>
            <div class="space-y-3 max-h-[500px] overflow-y-auto pr-2">
              <div
                v-for="log in emotionLogs"
                :key="log.id"
                class="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="text-2xl">{{ getEmotionEmoji((log as any).dominant_emotion || (log as any).emotion) }}</span>
                  <span class="text-xs text-gray-600">{{ formatTime((log as any).detected_at || (log as any).timestamp) }}</span>
                </div>
                <p class="font-semibold text-gray-900">{{ getEmotionName((log as any).dominant_emotion || (log as any).emotion) }}</p>
                <p class="text-xs text-gray-600">
                  {{ (log as any).student?.name || (log as any).student_id || 'Desconocido' }}
                </p>
                <p class="text-xs text-purple-600">
                  {{ Math.round((log as any).confidence * 100) }}% confianza
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import { classesService } from '@/services/classes.service'
import { emotionsService } from '@/services/emotions.service'
import type { ClassSession, EmotionLog } from '@/types'

const route = useRoute()

const activeClasses = ref<ClassSession[]>([])
const selectedClassId = ref<number | string>('')
const emotionLogs = ref<EmotionLog[]>([])

const emotionStats = computed(() => {
  if (emotionLogs.value.length === 0) return null
  
  const stats: Record<string, number> = {}
  emotionLogs.value.forEach(log => {
    const emotion = (log as any).dominant_emotion || (log as any).emotion
    stats[emotion] = (stats[emotion] || 0) + 1
  })
  
  return stats
})

const loadActiveClasses = async () => {
  try {
    activeClasses.value = await classesService.getActiveClasses()
    
    if (route.query.class_id) {
      selectedClassId.value = route.query.class_id as string
    } else if (activeClasses.value.length > 0 && activeClasses.value[0]) {
      selectedClassId.value = activeClasses.value[0].id
    }
  } catch (error) {
    console.error('Error cargando clases:', error)
  }
}

const loadEmotionLogs = async () => {
  if (!selectedClassId.value) return

  try {
    emotionLogs.value = await emotionsService.getClassEmotions(selectedClassId.value as any)
  } catch (error) {
    console.error('Error cargando logs:', error)
  }
}

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
  return emojis[emotion.toLowerCase()] || '😶'
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
  return names[emotion.toLowerCase()] || emotion
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-ES', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}

onMounted(async () => {
  await loadActiveClasses()
  if (selectedClassId.value) {
    await loadEmotionLogs()
  }
})
</script>
