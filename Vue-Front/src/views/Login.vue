/**
 * Smart Classroom AI - Login/Register View
 */
<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white rounded-2xl shadow-2xl p-8">
      <!-- Logo and Title -->
      <div class="text-center">
        <div class="text-6xl mb-4">🎓</div>
        <h1 class="text-3xl font-extrabold text-gray-900">
          Smart Classroom AI
        </h1>
        <h2 class="mt-2 text-xl font-semibold text-gray-700">
          {{ isLoginMode ? 'Iniciar Sesión' : 'Crear Cuenta' }}
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          {{ isLoginMode ? 'Accede a tu cuenta de profesor' : 'Regístrate como profesor' }}
        </p>
      </div>

      <!-- Error Message -->
      <div
        v-if="errorMessage"
        class="bg-red-50 border-l-4 border-red-500 p-4 rounded"
      >
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{{ errorMessage }}</p>
          </div>
        </div>
      </div>

      <!-- Success Message -->
      <div
        v-if="successMessage"
        class="bg-green-50 border-l-4 border-green-500 p-4 rounded"
      >
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-green-700">{{ successMessage }}</p>
          </div>
        </div>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="mt-8 space-y-6">
        <!-- Full Name (Only for Register) -->
        <div v-if="!isLoginMode">
          <label for="fullName" class="block text-sm font-medium text-gray-700">
            Nombre Completo
          </label>
          <input
            id="fullName"
            v-model="formData.fullName"
            type="text"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="Ej: Juan Pérez García"
          />
        </div>

        <!-- Email -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">
            Correo Electrónico
          </label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            required
            autocomplete="email"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="profesor@universidad.edu"
          />
        </div>

        <!-- Password -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">
            Contraseña
          </label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            required
            autocomplete="current-password"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            :placeholder="isLoginMode ? 'Tu contraseña' : 'Mínimo 6 caracteres'"
          />
        </div>

        <!-- Submit Button -->
        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            <svg
              v-if="isLoading"
              class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isLoading ? 'Procesando...' : (isLoginMode ? 'Iniciar Sesión' : 'Crear Cuenta') }}
          </button>
        </div>
      </form>

      <!-- Toggle Login/Register -->
      <div class="text-center">
        <p class="text-sm text-gray-600">
          {{ isLoginMode ? '¿No tienes cuenta?' : '¿Ya tienes cuenta?' }}
          <button
            @click="toggleMode"
            type="button"
            class="font-medium text-indigo-600 hover:text-indigo-500 ml-1"
          >
            {{ isLoginMode ? 'Regístrate aquí' : 'Inicia sesión' }}
          </button>
        </p>
      </div>

      <!-- Additional Info -->
      <div class="text-center pt-4 border-t border-gray-200">
        <p class="text-xs text-gray-500">
          Plataforma de asistencia inteligente con análisis de emociones
        </p>
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

      successMessage.value = '¡Bienvenido! Redirigiendo...'
      
      setTimeout(() => {
        const redirect = route.query.redirect as string
        router.push(redirect || '/dashboard')
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
