/**
 * StatsCard - Tarjeta de estadísticas estilo Moodle
 */
<template>
  <div class="bg-white rounded-lg border border-gray-200 p-5">
    <div class="flex items-center gap-4">
      <div class="text-3xl text-[#4A5565]">
        <FontAwesomeIcon :icon="['fas', icon]" />
      </div>
      <div>
        <p class="text-sm text-gray-500">{{ label }}</p>
        <p class="text-2xl font-bold text-gray-800">
          {{ value }}<span v-if="suffix" class="text-lg font-normal text-gray-500">{{ suffix }}</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  label: string
  value: string | number
  suffix?: string
  icon: string
  color?: string
}

withDefaults(defineProps<Props>(), {
  color: 'gray'
})
</script>
