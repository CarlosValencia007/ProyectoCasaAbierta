/**
 * ConfirmModal - Modal de confirmación estilo Moodle
 */
<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50"
      @click.self="$emit('cancel')"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 class="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <FontAwesomeIcon 
              v-if="icon" 
              :icon="['fas', icon]" 
              :class="iconColorClass" 
            />
            {{ title }}
          </h2>
        </div>
        <div class="p-6 text-gray-600">
          <slot>
            <p>{{ message }}</p>
          </slot>
        </div>
        <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex gap-3 justify-end">
          <button
            @click="$emit('cancel')"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-100 transition-colors"
          >
            {{ cancelText }}
          </button>
          <button
            @click="$emit('confirm')"
            :disabled="loading"
            class="px-4 py-2 rounded transition-colors disabled:opacity-50 inline-flex items-center gap-2"
            :class="confirmButtonClass"
          >
            <FontAwesomeIcon v-if="loading" :icon="['fas', 'spinner']" class="animate-spin" />
            <FontAwesomeIcon v-else-if="confirmIcon" :icon="['fas', confirmIcon]" />
            {{ loading ? loadingText : confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  show: boolean
  title: string
  message?: string
  icon?: string
  iconColor?: 'warning' | 'danger' | 'info'
  confirmText?: string
  confirmIcon?: string
  cancelText?: string
  loading?: boolean
  loadingText?: string
  variant?: 'danger' | 'primary' | 'warning'
}

const props = withDefaults(defineProps<Props>(), {
  confirmText: 'Confirmar',
  cancelText: 'Cancelar',
  loadingText: 'Procesando...',
  variant: 'danger',
  iconColor: 'warning'
})

defineEmits<{
  confirm: []
  cancel: []
}>()

const iconColorClass = computed(() => {
  const colors = {
    warning: 'text-amber-500',
    danger: 'text-red-500',
    info: 'text-blue-500'
  }
  return colors[props.iconColor]
})

const confirmButtonClass = computed(() => {
  const variants = {
    danger: 'bg-red-600 text-white hover:bg-red-700',
    primary: 'bg-gray-700 text-white hover:bg-gray-800',
    warning: 'bg-amber-600 text-white hover:bg-amber-700'
  }
  return variants[props.variant]
})
</script>
