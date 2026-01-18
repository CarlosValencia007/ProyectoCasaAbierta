/**
 * Smart Classroom AI - Navbar Component
 */
<template>
  <nav class="navbar-uleam shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo y Brand -->
        <div class="flex items-center">
          <router-link to="/dashboard" class="flex items-center space-x-3 group">
            <FontAwesomeIcon :icon="['fas', 'house']" class="text-white text-2xl" />
            <!--<img :src="logoUleam" alt="Clase Inteligente AI" class="h-8 w-auto bg-white rounded shadow-sm"> -->
            <span class="text-xl font-bold text-white hidden sm:block drop-shadow-sm group-hover:text-red-100 transition-colors">
              Clase Inteligente AI
            </span>
          </router-link>
        </div>

        <!-- Navigation Links (Desktop) - Solo visible cuando está autenticado -->
        <div v-if="isAuthenticated && showNavLinks" class="hidden md:flex items-center space-x-1">
          <router-link
            v-for="link in navLinks"
            :key="link.path"
            :to="link.path"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
            :class="[
              isActive(link.path)
                ? 'bg-white/20 text-white shadow-inner backdrop-blur-sm'
                : 'text-red-100 hover:bg-white/10 hover:text-white'
            ]"
          >
            <FontAwesomeIcon :icon="['fas', link.icon]" class="mr-2" />
            {{ link.name }}
          </router-link>
        </div>

        <!-- User Menu - Solo visible cuando está autenticado -->
        <div v-if="isAuthenticated" class="flex items-center space-x-4">
          <div class="hidden sm:flex items-center space-x-3">
            <div class="text-right">
              <p class="text-sm font-semibold text-white">
                {{ profile?.full_name || 'Usuario' }}
              </p>
              <p class="text-xs text-red-200">{{ profile?.email }}</p>
            </div>
            <div class="h-10 w-10 rounded-full bg-white/20 backdrop-blur-sm border-2 border-white/30 flex items-center justify-center text-white font-bold shadow-sm">
              {{ initials }}
            </div>
          </div>
          
          <button
            @click="handleLogout"
            class="px-4 py-2 text-sm font-medium text-[#D31E19] bg-white rounded-lg hover:bg-red-50 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-[#D31E19] shadow-sm flex items-center gap-2"
          >
            <FontAwesomeIcon :icon="['fas', 'right-from-bracket']" />
            Salir
          </button>

          <!-- Mobile menu button -->
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden p-2 rounded-lg text-white hover:bg-white/10 transition-colors"
          >
            <FontAwesomeIcon 
              :icon="['fas', mobileMenuOpen ? 'xmark' : 'bars']" 
              class="h-6 w-6" 
            />
          </button>
        </div>

        <!-- Login button - Solo visible cuando NO está autenticado -->
        <div v-else>
          <router-link
            to="/login"
            class="px-4 py-2 text-sm font-medium text-[#D31E19] bg-white rounded-lg hover:bg-red-50 transition-all duration-200 shadow-sm flex items-center gap-2"
          >
            <FontAwesomeIcon :icon="['fas', 'right-to-bracket']" />
            Iniciar Sesión
          </router-link>
        </div>
      </div>
    </div>

    <!-- Mobile menu - Solo visible cuando está autenticado -->
    <div v-if="mobileMenuOpen && isAuthenticated && showNavLinks" class="md:hidden border-t border-white/20">
      <div class="px-3 pt-3 pb-4 space-y-1">
        <router-link
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          @click="mobileMenuOpen = false"
          class="block px-4 py-3 rounded-lg text-base font-medium transition-all duration-200"
          :class="[
            isActive(link.path)
              ? 'bg-white/20 text-white'
              : 'text-red-100 hover:bg-white/10 hover:text-white'
          ]"
        >
          <FontAwesomeIcon :icon="['fas', link.icon]" class="mr-3 w-5" />
          {{ link.name }}
        </router-link>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar-uleam {
  background: #d63031;
}
</style>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const route = useRoute()
const { profile, signOut, isAuthenticated } = useAuth()

const mobileMenuOpen = ref(false)

const navLinks = [
  { name: 'Dashboard', path: '/dashboard', icon: 'gauge-high' },
  { name: 'Asistencia', path: '/attendance', icon: 'clipboard-check' },
  { name: 'Emociones', path: '/emotions', icon: 'face-smile' }
]

// Mostrar links de navegación solo cuando NO estemos en el dashboard principal
const showNavLinks = computed(() => {
  return route.path !== '/dashboard'
})

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
  } catch {
    // Error signing out
  }
}
</script>
