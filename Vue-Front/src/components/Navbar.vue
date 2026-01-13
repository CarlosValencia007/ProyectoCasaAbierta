/**
 * Smart Classroom AI - Navbar Component
 */
<template>
  <nav class="bg-white shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo y Brand -->
        <div class="flex items-center">
          <router-link to="/dashboard" class="flex items-center space-x-2">
            <span class="text-3xl">🎓</span>
            <span class="text-xl font-bold text-indigo-600 hidden sm:block">
              Smart Classroom AI
            </span>
          </router-link>
        </div>

        <!-- Navigation Links (Desktop) -->
        <div class="hidden md:flex items-center space-x-1">
          <router-link
            v-for="link in navLinks"
            :key="link.path"
            :to="link.path"
            class="px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
            :class="[
              isActive(link.path)
                ? 'bg-indigo-100 text-indigo-700'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            ]"
          >
            <span class="mr-1">{{ link.icon }}</span>
            {{ link.name }}
          </router-link>
        </div>

        <!-- User Menu -->
        <div class="flex items-center space-x-4">
          <div class="hidden sm:flex items-center space-x-2">
            <div class="text-right">
              <p class="text-sm font-medium text-gray-700">
                {{ profile?.full_name || 'Usuario' }}
              </p>
              <p class="text-xs text-gray-500">{{ profile?.email }}</p>
            </div>
            <div class="h-10 w-10 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold">
              {{ initials }}
            </div>
          </div>
          
          <button
            @click="handleLogout"
            class="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-md hover:bg-red-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            Salir
          </button>

          <!-- Mobile menu button -->
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden p-2 rounded-md text-gray-600 hover:bg-gray-100"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                v-if="!mobileMenuOpen"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-200">
      <div class="px-2 pt-2 pb-3 space-y-1">
        <router-link
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          @click="mobileMenuOpen = false"
          class="block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
          :class="[
            isActive(link.path)
              ? 'bg-indigo-100 text-indigo-700'
              : 'text-gray-600 hover:bg-gray-100'
          ]"
        >
          <span class="mr-2">{{ link.icon }}</span>
          {{ link.name }}
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const route = useRoute()
const { profile, signOut } = useAuth()

const mobileMenuOpen = ref(false)

const navLinks = [
  { name: 'Dashboard', path: '/dashboard', icon: '📊' },
  { name: 'Estudiantes', path: '/students', icon: '👥' },
  { name: 'Clases', path: '/classes', icon: '📅' },
  { name: 'Asistencia', path: '/attendance', icon: '✅' },
  { name: 'Emociones', path: '/emotions', icon: '😊' }
]

const initials = computed(() => {
  if (!profile.value?.full_name) return 'U'
  const names = profile.value.full_name.split(' ').filter(n => n.length > 0)
  if (names.length === 0) return 'U'
  return names.length > 1
    ? (names[0]?.[0] || '') + (names[1]?.[0] || '')
    : (names[0]?.[0] || 'U')
})

const isActive = (path: string) => {
  return route.path === path
}

const handleLogout = async () => {
  try {
    await signOut()
    router.push('/login')
  } catch (error) {
    console.error('Error al cerrar sesión:', error)
  }
}
</script>
