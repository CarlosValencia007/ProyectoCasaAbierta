/**
 * Smart Classroom AI - Authentication Composable
 * Manejo de autenticación con Supabase
 */

import { ref, computed } from 'vue'
import { supabase } from '@/services/supabase'
import type { User, Session } from '@supabase/supabase-js'
import type { UserProfile } from '@/types'

// Estado global compartido entre todas las instancias
const user = ref<User | null>(null)
const session = ref<Session | null>(null)
const loading = ref(true)
const profile = ref<UserProfile | null>(null)

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)

  /**
   * Registrar nuevo usuario
   */
  const signUp = async (email: string, password: string, fullName: string) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
            role: 'teacher'
          }
        }
      })

      if (error) throw error

      // Auto login después del registro
      if (data.user && data.session) {
        user.value = data.user
        session.value = data.session
        profile.value = {
          id: data.user.id,
          email: data.user.email!,
          full_name: fullName,
          role: 'teacher'
        }
      }

      return { data, error: null }
    } catch (error: any) {
      console.error('Error en signUp:', error)
      return { data: null, error: error.message }
    }
  }

  /**
   * Iniciar sesión
   */
  const signIn = async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) throw error

      user.value = data.user
      session.value = data.session

      // Cargar perfil del usuario
      if (data.user) {
        profile.value = {
          id: data.user.id,
          email: data.user.email!,
          full_name: data.user.user_metadata?.full_name || email,
          role: data.user.user_metadata?.role || 'teacher'
        }
      }

      return { data, error: null }
    } catch (error: any) {
      console.error('Error en signIn:', error)
      return { data: null, error: error.message }
    }
  }

  /**
   * Cerrar sesión
   */
  const signOut = async () => {
    try {
      const { error } = await supabase.auth.signOut()
      if (error) throw error

      user.value = null
      session.value = null
      profile.value = null
    } catch (error) {
      console.error('Error al cerrar sesión:', error)
      throw error
    }
  }

  /**
   * Obtener usuario actual
   */
  const getCurrentUser = async () => {
    try {
      const { data: { user: currentUser }, error } = await supabase.auth.getUser()
      
      if (error) throw error
      
      if (currentUser) {
        user.value = currentUser
        profile.value = {
          id: currentUser.id,
          email: currentUser.email!,
          full_name: currentUser.user_metadata?.full_name || currentUser.email!,
          role: currentUser.user_metadata?.role || 'teacher'
        }
      }
      
      return currentUser
    } catch (error) {
      console.error('Error obteniendo usuario actual:', error)
      return null
    }
  }

  /**
   * Actualizar perfil de usuario
   */
  const updateProfile = async (updates: { full_name?: string }) => {
    try {
      const { data, error } = await supabase.auth.updateUser({
        data: updates
      })

      if (error) throw error

      if (data.user && profile.value) {
        profile.value.full_name = updates.full_name || profile.value.full_name
      }

      return { data, error: null }
    } catch (error: any) {
      return { data: null, error: error.message }
    }
  }

  /**
   * Cambiar contraseña
   */
  const updatePassword = async (newPassword: string) => {
    try {
      const { data, error } = await supabase.auth.updateUser({
        password: newPassword
      })

      if (error) throw error
      return { data, error: null }
    } catch (error: any) {
      return { data: null, error: error.message }
    }
  }

  /**
   * Recuperar contraseña
   */
  const resetPassword = async (email: string) => {
    try {
      const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`
      })

      if (error) throw error
      return { data, error: null }
    } catch (error: any) {
      return { data: null, error: error.message }
    }
  }

  /**
   * Inicializar autenticación
   * Debe ser llamado al inicio de la aplicación
   */
  const initAuth = async () => {
    loading.value = true

    try {
      // Obtener sesión actual
      const { data: { session: currentSession } } = await supabase.auth.getSession()
      
      session.value = currentSession
      user.value = currentSession?.user ?? null

      if (currentSession?.user) {
        profile.value = {
          id: currentSession.user.id,
          email: currentSession.user.email!,
          full_name: currentSession.user.user_metadata?.full_name || currentSession.user.email!,
          role: currentSession.user.user_metadata?.role || 'teacher'
        }
      }

      // Escuchar cambios de autenticación
      supabase.auth.onAuthStateChange((_event, newSession) => {
        session.value = newSession
        user.value = newSession?.user ?? null

        if (newSession?.user) {
          profile.value = {
            id: newSession.user.id,
            email: newSession.user.email!,
            full_name: newSession.user.user_metadata?.full_name || newSession.user.email!,
            role: newSession.user.user_metadata?.role || 'teacher'
          }
        } else {
          profile.value = null
        }
      })
    } catch (error) {
      console.error('Error inicializando autenticación:', error)
    } finally {
      loading.value = false
    }
  }

  return {
    // Estado
    user,
    session,
    loading,
    profile,
    isAuthenticated,

    // Métodos
    signUp,
    signIn,
    signOut,
    getCurrentUser,
    updateProfile,
    updatePassword,
    resetPassword,
    initAuth
  }
}
