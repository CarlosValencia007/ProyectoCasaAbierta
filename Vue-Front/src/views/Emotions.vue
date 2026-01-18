/**
 * Smart Classroom AI - Emotions Analysis View
 */
<template>
  <div class="min-h-screen bg-gray-50">

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <PageHeader
        title="Analisis Emocional"
        icon="face-smile"
        icon-color="purple"
      />

      <!-- Combined Emotion Analytics -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FontAwesomeIcon :icon="['fas', 'chart-bar']" class="text-[#b81a16]" />
            Analisis de Clase
          </h2>
          <select
            v-model="selectedClassId"
            @change="loadEmotionLogs"
            class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#b81a16]"
          >
            <option value="">Seleccionar clase...</option>
            <option v-for="classItem in activeClasses" :key="classItem.id" :value="classItem.id">
              {{ classItem.class_name }} ({{ formatClassDate(classItem.start_time) }})
            </option>
          </select>
        </div>

        <!-- Empty State -->
        <div v-if="emotionLogs.length === 0" class="text-center py-16 text-gray-500">
          <div class="text-6xl mb-4 text-gray-300">
            <FontAwesomeIcon :icon="['fas', 'masks-theater']" />
          </div>
          <p class="text-xl font-semibold text-gray-900 mb-2">No hay registros aun</p>
          <p class="text-sm">Las emociones se capturan automaticamente al tomar asistencia</p>
        </div>

        <!-- Content with data -->
        <div v-else>
          <!-- Statistics Section -->
          <div class="mb-8">
            <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <FontAwesomeIcon :icon="['fas', 'chart-line']" class="text-green-600" />
              Resumen Estadistico
            </h3>
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
            <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <FontAwesomeIcon :icon="['fas', 'clipboard-list']" class="text-[#b81a16]" />
              Historial Detallado
            </h3>
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
import { classesService } from '@/services/classes.service'
import { emotionsService } from '@/services/emotions.service'
import { supabase } from '@/services/supabase'
import type { ClassSession, EmotionLog } from '@/types'
import PageHeader from '@/components/PageHeader.vue'

const route = useRoute()

const activeClasses = ref<ClassSession[]>([])
const selectedClassId = ref<number | string>('')
const emotionLogs = ref<EmotionLog[]>([])

// Obtener courseId de los parámetros de la ruta (si viene desde CourseDetail)
const courseId = computed(() => route.params.courseId as string | undefined)

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
    // Si hay courseId en la ruta, filtrar por materia
    if (courseId.value) {
      // Cargar todas las sesiones de esta materia
      const { data: allSessionsData } = await supabase
        .from('class_sessions')
        .select('*')
        .order('created_at', { ascending: false })
      
      // Filtrar por course_id en metadata
      const filteredSessions = (allSessionsData || []).filter(session => {
        const metadata = session.metadata as { course_id?: string } | null
        return metadata?.course_id === courseId.value
      })
      
      activeClasses.value = filteredSessions
    } else {
      // Sin courseId: cargar todas las clases activas (comportamiento original)
      activeClasses.value = await classesService.getActiveClasses()
    }
    
    // Seleccionar clase inicial
    if (route.query.class_id) {
      selectedClassId.value = route.query.class_id as string
    } else if (activeClasses.value.length > 0 && activeClasses.value[0]) {
      selectedClassId.value = activeClasses.value[0].id
    }
  } catch {
    // Error loading classes
  }
}

const loadEmotionLogs = async () => {
  if (!selectedClassId.value) return

  try {
    emotionLogs.value = await emotionsService.getClassEmotions(selectedClassId.value as any)
  } catch {
    // Error loading logs
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

const formatClassDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-EC', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'America/Guayaquil'
  }).format(date)
}

onMounted(async () => {
  await loadActiveClasses()
  if (selectedClassId.value) {
    await loadEmotionLogs()
  }
})
</script>
