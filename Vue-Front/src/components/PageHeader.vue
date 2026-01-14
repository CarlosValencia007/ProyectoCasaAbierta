/**
 * PageHeader - Header de página estilo Moodle
 */
<template>
  <div class="bg-white rounded-lg border border-gray-200 mb-6">
    <div class="px-6 py-4" :class="{ 'border-b border-gray-200': hasAction || description }">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-semibold text-[#d63031] flex items-center gap-2">
          <FontAwesomeIcon v-if="icon" :icon="['fas', icon]" />
          {{ title }}
        </h1>
        <slot name="action"></slot>
      </div>
      <p v-if="description" class="mt-2 text-sm text-gray-500">
        {{ description }}
      </p>
    </div>
    <div v-if="$slots.default" class="p-6">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSlots } from 'vue'

interface Props {
  title: string
  icon?: string
  description?: string
}

defineProps<Props>()

const slots = useSlots()
const hasAction = !!slots.action
</script>
