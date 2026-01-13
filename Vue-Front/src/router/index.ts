/**
 * Smart Classroom AI - Vue Router Configuration
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { 
      requiresAuth: false,
      title: 'Iniciar Sesión'
    }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Dashboard'
    }
  },
  {
    path: '/students',
    name: 'Students',
    component: () => import('@/views/Students.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Estudiantes'
    }
  },
  {
    path: '/courses/:id',
    name: 'CourseDetail',
    component: () => import('@/views/CourseDetail.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Detalle de Materia'
    }
  },
  {
    path: '/enrollment',
    name: 'Enrollment',
    component: () => import('@/views/Enrollment.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Registrar Estudiante'
    }
  },
  {
    path: '/courses/:courseId/enrollment',
    name: 'CourseEnrollment',
    component: () => import('@/views/Enrollment.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Registrar Estudiante'
    }
  },
  {
    path: '/courses/:courseId/attendance',
    name: 'CourseAttendance',
    component: () => import('@/views/Attendance.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Asistencia'
    }
  },
  {
    path: '/courses/:courseId/emotions',
    name: 'CourseEmotions',
    component: () => import('@/views/Emotions.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Análisis Emocional'
    }
  },
  {
    path: '/classes',
    name: 'Classes',
    component: () => import('@/views/Classes.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Clases'
    }
  },
  {
    path: '/attendance',
    name: 'Attendance',
    component: () => import('@/views/Attendance.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Asistencia'
    }
  },
  {
    path: '/emotions',
    name: 'Emotions',
    component: () => import('@/views/Emotions.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Análisis Emocional'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { 
      requiresAuth: false,
      title: 'Página no encontrada'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guard
router.beforeEach(async (to, _from, next) => {
  const { isAuthenticated, loading } = useAuth()

  // Actualizar título de la página
  document.title = `${to.meta.title || 'Smart Classroom AI'} - Smart Classroom AI`

  // Esperar a que termine la carga de autenticación
  let attempts = 0
  while (loading.value && attempts < 50) {
    await new Promise(resolve => setTimeout(resolve, 100))
    attempts++
  }

  // Verificar autenticación
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !isAuthenticated.value) {
    // Ruta protegida sin autenticación -> redirigir a login
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (to.path === '/login' && isAuthenticated.value) {
    // Usuario autenticado intentando acceder a login -> redirigir a dashboard
    next('/dashboard')
  } else {
    // Permitir navegación
    next()
  }
})

export default router
