/**
 * Smart Classroom AI - 404 Not Found View
 */
<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center items-center px-4">
    <div class="text-center">
      <h1 class="text-9xl font-bold text-indigo-600">404</h1>
      <p class="text-2xl font-semibold text-gray-900 mt-4">Página no encontrada</p>
      <p class="text-gray-600 mt-2">La página que buscas no existe</p>
      
      <router-link
        to="/dashboard"
        class="mt-8 inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200"
      >
        ← Volver al Dashboard
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
// No setup needed
</script>
