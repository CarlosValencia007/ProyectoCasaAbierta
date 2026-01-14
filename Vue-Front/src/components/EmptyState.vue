/**
 * EmptyState - Componente para estados vacíos estilo Moodle
 */
<template>
  <div class="text-center py-12">
    <div class="mb-4" :class="iconColorClass">
      <FontAwesomeIcon :icon="['fas', icon]" :class="iconSizeClass" />
    </div>
    <h2 class="text-xl font-semibold text-gray-700 mb-2">{{ title }}</h2>
    <p class="text-gray-500 mb-6 max-w-md mx-auto">{{ description }}</p>
    <slot name="action">
      <button
        v-if="actionText"
        @click="$emit('action')"
        class="px-6 py-3 bg-gray-700 text-white rounded hover:bg-gray-800 transition-colors inline-flex items-center gap-2"
      >
        <FontAwesomeIcon v-if="actionIcon" :icon="['fas', actionIcon]" />
        {{ actionText }}
      </button>
    </slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  icon?: string
  iconSize?: 'md' | 'lg' | 'xl'
  iconColor?: 'gray' | 'primary' | 'purple' | 'blue'
  title: string
  description: string
  actionText?: string
  actionIcon?: string
}

const props = withDefaults(defineProps<Props>(), {
  icon: 'inbox',
  iconSize: 'xl',
  iconColor: 'gray'
})

defineEmits<{
  action: []
}>()

const iconSizeClass = computed(() => {
  const sizes = {
    md: 'text-4xl',
    lg: 'text-5xl',
    xl: 'text-6xl'
  }
  return sizes[props.iconSize]
})

const iconColorClass = computed(() => {
  const colors = {
    gray: 'text-gray-300',
    primary: 'text-[#d63031]',
    purple: 'text-purple-300',
    blue: 'text-blue-300'
  }
  return colors[props.iconColor]
})
</script>
