/**
 * Smart Classroom AI - Login/Register View
 * Estilo inspirado en Moodle
 */
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center mb-4">
          <img 
            src="@/assets/LOGO-ULEAM-INICIO.png" 
            alt="ULEAM Logo" 
            class="h-24 w-auto"
          />
        </div>
        <h1 class="text-2xl font-bold text-gray-800">
          Smart Classroom AI
        </h1>
        <p class="mt-1 text-gray-500">
          Plataforma de asistencia inteligente
        </p>
      </div>

      <!-- Card -->
      <div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 class="text-lg font-semibold text-[#d63031]">
            {{ isLoginMode ? 'Iniciar Sesión' : 'Crear Cuenta' }}
          </h2>
        </div>

        <div class="p-6">
          <!-- Error Message -->
          <div
            v-if="errorMessage"
            class="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700 flex items-start gap-2"
          >
            <FontAwesomeIcon :icon="['fas', 'circle-exclamation']" class="mt-0.5 text-red-500" />
            {{ errorMessage }}
          </div>

          <!-- Success Message -->
          <div
            v-if="successMessage"
            class="mb-4 p-3 bg-green-50 border border-green-200 rounded text-sm text-green-700 flex items-start gap-2"
          >
            <FontAwesomeIcon :icon="['fas', 'circle-check']" class="mt-0.5 text-green-500" />
            {{ successMessage }}
          </div>

          <!-- Form -->
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <!-- Full Name (Only for Register) -->
            <div v-if="!isLoginMode">
              <label for="fullName" class="block text-sm font-medium text-gray-700 mb-1">
                Nombre Completo
              </label>
              <input
                id="fullName"
                v-model="formData.fullName"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#d63031] focus:border-transparent"
                placeholder="Ej: Juan Pérez García"
              />
            </div>

            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
                Correo Electrónico
              </label>
              <input
                id="email"
                v-model="formData.email"
                type="email"
                required
                autocomplete="email"
                class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#d63031] focus:border-transparent"
                placeholder="profesor@universidad.edu"
              />
            </div>

            <!-- Password -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
                Contraseña
              </label>
              <input
                id="password"
                v-model="formData.password"
                type="password"
                required
                autocomplete="current-password"
                class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#d63031] focus:border-transparent"
                :placeholder="isLoginMode ? 'Tu contraseña' : 'Mínimo 6 caracteres'"
              />
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full py-3 bg-[#d63031] text-white rounded hover:bg-[#c0292a] focus:outline-none focus:ring-2 focus:ring-[#d63031] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors inline-flex items-center justify-center gap-2"
            >
              <FontAwesomeIcon v-if="isLoading" :icon="['fas', 'spinner']" class="animate-spin" />
              {{ isLoading ? 'Procesando...' : (isLoginMode ? 'Iniciar Sesión' : 'Crear Cuenta') }}
            </button>
          </form>
        </div>

        <!-- Toggle Login/Register -->
        <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 text-center text-sm">
          <span class="text-gray-600">
            {{ isLoginMode ? '¿No tienes cuenta?' : '¿Ya tienes cuenta?' }}
          </span>
          <button
            @click="toggleMode"
            type="button"
            class="ml-1 font-medium text-[#d63031] hover:underline"
          >
            {{ isLoginMode ? 'Regístrate aquí' : 'Inicia sesión' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const route = useRoute()
const { signIn, signUp } = useAuth()

// Email del admin para mostrar mensaje especial
const ADMIN_EMAIL = 'secretaria@uleam.com'

const isLoginMode = ref(true)
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const formData = reactive({
  email: '',
  password: '',
  fullName: ''
})

const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value
  errorMessage.value = ''
  successMessage.value = ''
  formData.email = ''
  formData.password = ''
  formData.fullName = ''
}

const handleSubmit = async () => {
  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    if (isLoginMode.value) {
      // Login
      const { error } = await signIn(formData.email, formData.password)
      
      if (error) {
        errorMessage.value = error === 'Invalid login credentials' 
          ? 'Credenciales incorrectas' 
          : error
        return
      }

      // Determinar redirección según rol
      const isAdminUser = formData.email.toLowerCase() === ADMIN_EMAIL.toLowerCase()
      
      if (isAdminUser) {
        successMessage.value = '¡Bienvenida Secretaría! Redirigiendo...'
      } else {
        successMessage.value = '¡Bienvenido Profesor! Redirigiendo...'
      }
      
      setTimeout(() => {
        if (isAdminUser) {
          router.push('/admin/students')
        } else {
          const redirect = route.query.redirect as string
          router.push(redirect || '/dashboard')
        }
      }, 1000)
    } else {
      // Register
      if (!formData.fullName.trim()) {
        errorMessage.value = 'El nombre completo es requerido'
        return
      }

      if (formData.password.length < 6) {
        errorMessage.value = 'La contraseña debe tener al menos 6 caracteres'
        return
      }

      const { error } = await signUp(
        formData.email,
        formData.password,
        formData.fullName
      )
      
      if (error) {
        errorMessage.value = error.includes('already registered')
          ? 'Este correo ya está registrado'
          : error
        return
      }

      successMessage.value = '¡Cuenta creada! Redirigiendo...'
      
      setTimeout(() => {
        router.push('/dashboard')
      }, 1000)
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'Ocurrió un error inesperado'
  } finally {
    isLoading.value = false
  }
}
</script>
