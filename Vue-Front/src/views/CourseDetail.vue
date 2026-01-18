/**
 * Smart Classroom AI - Course Detail View
 * Dashboard específico de una materia/curso
 */
<template>
  <div class="min-h-screen bg-gray-50">

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading -->
      <LoadingSpinner v-if="loading" color="primary" />

      <!-- Course Header -->
      <div v-else-if="course" class="mb-8">
        <div class="bg-gradient-to-r from-[#b81a16] to-[#9a1512] rounded-lg shadow-lg p-8 text-white">
          <div class="flex justify-between items-start">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <router-link to="/dashboard" class="text-white/80 hover:text-white">
                  ← Dashboard
                </router-link>
                <span class="text-white/50">/</span>
                <span>{{ course.course_code }}</span>
              </div>
              <h1 class="text-4xl font-bold mb-2">{{ course.course_name }}</h1>
              <p v-if="course.description" class="text-white/90">{{ course.description }}</p>
              <p class="text-sm text-white/70 mt-2">Código: {{ course.course_code }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Grid -->
      <div v-if="!loading" class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatsCard
          label="Estudiantes"
          :value="stats.totalStudents"
          icon="users"
          color="blue"
        />
        <StatsCard
          label="Sesiones"
          :value="stats.totalSessions"
          icon="calendar-days"
          color="green"
        />
        <StatsCard
          label="Asistencia"
          :value="stats.avgAttendance"
          suffix="%"
          icon="circle-check"
          color="yellow"
        />
        <StatsCard
          label="Engagement"
          :value="stats.avgEngagement"
          suffix="%"
          icon="face-smile"
          color="purple"
        />
      </div>

      <!-- Quick Actions -->
      <div class="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <h2 class="text-xl font-semibold text-[#d63031] mb-4">
          Acciones Rápidas
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <button
            @click="openAddStudentModal"
            class="flex items-center gap-3 p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 hover:border-gray-300 transition-all duration-200"
          >
            <div class="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-blue-100 text-blue-600 rounded-lg">
              <FontAwesomeIcon :icon="['fas', 'user-plus']" class="text-lg" />
            </div>
            <div class="text-left flex-1">
              <p class="font-medium text-gray-800">Añadir Estudiante</p>
              <p class="text-xs text-gray-500">De los registrados</p>
            </div>
          </button>

          <button
            @click="openCreateSessionModal"
            class="flex items-center gap-3 p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 hover:border-gray-300 transition-all duration-200"
          >
            <div class="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-green-100 text-green-600 rounded-lg">
              <FontAwesomeIcon :icon="['fas', 'file-pen']" class="text-lg" />
            </div>
            <div class="text-left flex-1">
              <p class="font-medium text-gray-800">Iniciar Sesión</p>
              <p class="text-xs text-gray-500">Nueva clase</p>
            </div>
          </button>

          <button
            @click="$router.push(`/courses/${courseId}/attendance`)"
            class="flex items-center gap-3 p-4 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 hover:border-purple-300 transition-all duration-200"
          >
            <div class="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-purple-100 text-purple-600 rounded-lg">
              <FontAwesomeIcon :icon="['fas', 'camera']" class="text-lg" />
            </div>
            <div class="text-left flex-1">
              <p class="font-medium text-gray-800">Tomar Asistencia</p>
              <p class="text-xs text-gray-500">Verificación facial</p>
            </div>
          </button>

          <button
            @click="$router.push(`/courses/${courseId}/attendance`)"
            class="flex items-center gap-3 p-4 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 hover:border-indigo-300 transition-all duration-200"
          >
            <div class="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-indigo-100 text-indigo-600 rounded-lg">
              <FontAwesomeIcon :icon="['fas', 'clipboard-check']" class="text-lg" />
            </div>
            <div class="text-left flex-1">
              <p class="font-medium text-gray-800">Ver Asistencia</p>
              <p class="text-xs text-gray-500">Registros y reportes</p>
            </div>
          </button>

          <button
            @click="$router.push(`/courses/${courseId}/emotions`)"
            class="flex items-center gap-3 p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 hover:border-gray-300 transition-all duration-200"
          >
            <div class="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-amber-100 text-amber-600 rounded-lg">
              <FontAwesomeIcon :icon="['fas', 'masks-theater']" class="text-lg" />
            </div>
            <div class="text-left flex-1">
              <p class="font-medium text-gray-800">Analizar Emociones</p>
              <p class="text-xs text-gray-500">Estado emocional</p>
            </div>
          </button>

          <button
            @click="openQRModal"
            class="flex items-center gap-3 p-4 bg-sky-50 border border-sky-200 rounded-lg hover:bg-sky-100 hover:border-sky-300 transition-all duration-200"
          >
            <div class="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-sky-100 text-sky-600 rounded-lg">
              <FontAwesomeIcon :icon="['fas', 'qrcode']" class="text-lg" />
            </div>
            <div class="text-left flex-1">
              <p class="font-medium text-gray-800">Generar QR</p>
              <p class="text-xs text-gray-500">Asistencia por código</p>
            </div>
          </button>
        </div>
      </div>

      <!-- Content Tabs -->
      <div class="bg-white rounded-lg shadow-md">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'px-6 py-4 font-medium text-sm transition-colors inline-flex items-center gap-2',
                activeTab === tab.id
                  ? 'border-b-2 border-[#b81a16] text-[#b81a16]'
                  : 'text-gray-500 hover:text-gray-700'
              ]"
            >
              <FontAwesomeIcon :icon="['fas', tab.icon]" />
              {{ tab.label }}
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- Students Tab -->
          <div v-if="activeTab === 'students'">
            <!-- Header con boton de anadir -->
            <div class="flex justify-between items-center mb-4">
              <p class="text-sm text-gray-600">{{ students.length }} estudiantes inscritos</p>
              <button
                @click="openAddStudentModal"
                class="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 text-sm font-medium inline-flex items-center gap-2"
              >
                <FontAwesomeIcon :icon="['fas', 'plus']" class="text-sm" />
                Añadir Estudiante
              </button>
            </div>

            <div v-if="students.length === 0" class="text-center py-12 text-gray-500">
              <div class="w-24 h-24 mx-auto mb-4 flex items-center justify-center bg-gray-100 rounded-full">
                <FontAwesomeIcon :icon="['fas', 'users']" class="text-5xl text-gray-300" />
              </div>
              <p class="text-lg mb-2">No hay estudiantes en esta materia</p>
              <p class="text-sm mb-4 text-gray-400">
                Los estudiantes deben ser registrados por la secretaría antes de añadirlos aquí
              </p>
              <button
                @click="openAddStudentModal"
                class="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-800 inline-flex items-center gap-2"
              >
                <FontAwesomeIcon :icon="['fas', 'plus']" class="text-sm" />
                Añadir Estudiantes Registrados
              </button>
            </div>
            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="student in students"
                :key="student.student_id"
                class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 group"
              >
                <div class="flex-1">
                  <p class="font-semibold text-gray-900">{{ student.name }}</p>
                  <p class="text-xs text-gray-600">Cédula: {{ student.student_id }}</p>
                </div>
                <button
                  @click="unenrollStudent(student.student_id, student.name)"
                  class="opacity-0 group-hover:opacity-100 p-2 text-red-500 hover:bg-red-50 rounded-lg transition-all"
                  title="Quitar de la materia"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>

          <!-- Sessions Tab -->
          <div v-if="activeTab === 'sessions'">
            <div v-if="sessions.length === 0" class="text-center py-12 text-gray-500">
              <div class="w-24 h-24 mx-auto mb-4 flex items-center justify-center bg-gray-100 rounded-full">
                <FontAwesomeIcon :icon="['fas', 'calendar-days']" class="text-5xl text-gray-300" />
              </div>
              <p class="text-lg mb-4">No hay sesiones de clase</p>
              <button
                @click="openCreateSessionModal"
                class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 inline-flex items-center gap-2"
              >
                <FontAwesomeIcon :icon="['fas', 'file-pen']" class="text-sm" />
                Crear Primera Sesión
              </button>
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="session in sessions"
                :key="session.id"
                class="p-4 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div class="flex items-center justify-between mb-3">
                  <div>
                    <p class="font-semibold text-gray-900">{{ session.class_name }}</p>
                    <p class="text-sm text-gray-600">{{ formatDateTime(session.start_time) }}</p>
                  </div>
                  <span
                    :class="[
                      'px-3 py-1 text-sm font-medium rounded',
                      isSessionActive(session) ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-700'
                    ]"
                  >
                    {{ isSessionActive(session) ? 'Activa' : 'Finalizada' }}
                  </span>
                </div>
                
                <!-- Botones de acción -->
                <div class="flex flex-wrap gap-2">
                  <!-- Botones para sesiones activas -->
                  <template v-if="isSessionActive(session)">
                    <router-link
                      :to="`/attendance?class_id=${session.id}`"
                      class="px-3 py-1.5 bg-[#b81a16] text-white text-sm rounded-lg hover:bg-[#9a1512] inline-flex items-center gap-1"
                    >
                      <FontAwesomeIcon :icon="['fas', 'clipboard-check']" />
                      Tomar Asistencia
                    </router-link>
                    <router-link
                      :to="`/emotions?class_id=${session.id}`"
                      class="px-3 py-1.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 inline-flex items-center gap-1"
                    >
                      <FontAwesomeIcon :icon="['fas', 'face-smile']" />
                      Emociones
                    </router-link>
                    <button
                      @click="confirmEndSession(session)"
                      class="px-3 py-1.5 bg-orange-500 text-white text-sm rounded-lg hover:bg-orange-600 inline-flex items-center gap-1"
                    >
                      <FontAwesomeIcon :icon="['fas', 'stop']" />
                      Finalizar
                    </button>
                  </template>
                  
                  <!-- Botones para sesiones finalizadas -->
                  <template v-else>
                    <router-link
                      :to="`/attendance?class_id=${session.id}`"
                      class="px-3 py-1.5 bg-gray-500 text-white text-sm rounded-lg hover:bg-gray-600 inline-flex items-center gap-1"
                    >
                      <FontAwesomeIcon :icon="['fas', 'eye']" />
                      Ver Asistencia
                    </router-link>
                    <router-link
                      :to="`/emotions?class_id=${session.id}`"
                      class="px-3 py-1.5 bg-purple-400 text-white text-sm rounded-lg hover:bg-purple-500 inline-flex items-center gap-1"
                    >
                      <FontAwesomeIcon :icon="['fas', 'chart-bar']" />
                      Ver Emociones
                    </router-link>
                  </template>
                  
                  <!-- Botón eliminar siempre visible -->
                  <button
                    @click="confirmDeleteSession(session)"
                    class="px-3 py-1.5 bg-red-100 text-red-600 text-sm rounded-lg hover:bg-red-200 inline-flex items-center gap-1"
                  >
                    <FontAwesomeIcon :icon="['fas', 'trash']" />
                    Eliminar
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Activity Tab -->
          <div v-if="activeTab === 'activity'">
            <p class="text-gray-600">Historial de actividad próximamente...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Anadir Estudiante -->
    <div
      v-if="showAddStudentModal"
      class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center z-50"
      @click.self="showAddStudentModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4 max-h-[80vh] overflow-hidden flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
            <div class="w-8 h-8 flex items-center justify-center bg-[#b81a16] text-white rounded-lg">
              <FontAwesomeIcon :icon="['fas', 'plus']" class="text-sm" />
            </div>
            Añadir Estudiante a la Materia
          </h3>
          <button @click="showAddStudentModal = false" class="text-gray-400 hover:text-gray-600 text-xl">
            <FontAwesomeIcon :icon="['fas', 'xmark']" />
          </button>
        </div>
        
        <!-- Campo de busqueda -->
        <div class="mb-4">
          <div class="relative">
            <div class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              <FontAwesomeIcon :icon="['fas', 'magnifying-glass']" class="text-sm" />
            </div>
            <input
              v-model="studentSearchQuery"
              type="text"
              placeholder="Buscar por nombre, cédula o email..."
              class="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#b81a16] focus:border-transparent"
            />
            <button
              v-if="studentSearchQuery"
              @click="studentSearchQuery = ''"
              class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <FontAwesomeIcon :icon="['fas', 'xmark']" class="text-sm" />
            </button>
          </div>
        </div>
        
        <div v-if="availableStudents.length === 0" class="text-center py-8 text-gray-500">
          <div class="w-20 h-20 mx-auto mb-4 flex items-center justify-center bg-gray-100 rounded-full">
            <FontAwesomeIcon :icon="['fas', 'inbox']" class="text-4xl text-gray-300" />
          </div>
          <p class="text-lg mb-2">No hay estudiantes disponibles</p>
          <p class="text-sm">Todos los estudiantes ya están inscritos en esta materia</p>
          <p class="text-xs text-gray-400 mt-2 flex items-center justify-center gap-1">
            <FontAwesomeIcon :icon="['fas', 'lightbulb']" class="text-sm text-yellow-500" />
            Contacta a la secretaría para registrar nuevos estudiantes
          </p>
        </div>
        
        <div v-else-if="filteredAvailableStudents.length === 0" class="text-center py-8 text-gray-500">
          <div class="w-20 h-20 mx-auto mb-4 flex items-center justify-center bg-gray-100 rounded-full">
            <FontAwesomeIcon :icon="['fas', 'magnifying-glass']" class="text-4xl text-gray-300" />
          </div>
          <p class="text-lg mb-2">No se encontraron resultados</p>
          <p class="text-sm">Prueba con otro término de búsqueda</p>
        </div>
        
        <div v-else class="flex-1 overflow-y-auto space-y-2">
          <p class="text-sm text-gray-600 mb-3">
            {{ filteredAvailableStudents.length }} de {{ availableStudents.length }} estudiantes
          </p>
          <div
            v-for="student in filteredAvailableStudents"
            :key="student.student_id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
          >
            <div class="flex items-center">
              <div class="h-10 w-10 rounded-full bg-[#b81a16] flex items-center justify-center text-white font-bold mr-3 overflow-hidden">
                <img v-if="student.photo_url" :src="student.photo_url" :alt="student.name" class="w-full h-full object-cover" />
                <span v-else>{{ getInitials(student.name) }}</span>
              </div>
              <div>
                <p class="font-semibold text-gray-900">{{ student.name }}</p>
                <p class="text-xs text-gray-600">Cédula: {{ student.student_id }}</p>
                <p v-if="student.email" class="text-xs text-gray-400">{{ student.email }}</p>
              </div>
            </div>
            <button
              @click="enrollStudent(student.student_id)"
              :disabled="addingStudent"
              class="px-3 py-1 bg-gray-700 text-white rounded-lg hover:bg-gray-800 text-sm font-medium disabled:opacity-50"
            >
              {{ addingStudent ? '...' : '+ Añadir' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Crear Sesión -->
    <div
      v-if="showCreateSessionModal"
      class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center z-50"
      @click.self="showCreateSessionModal = false"
    >
      <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4">
        <h3 class="text-2xl font-bold text-gray-900 mb-6">Nueva Sesión de Clase</h3>
        
        <form @submit.prevent="createSession" class="space-y-4">
          <!-- Curso (Solo lectura) -->
          <div class="p-3 bg-[#b81a16]/10 border border-[#b81a16]/30 rounded-lg">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Curso/Materia
            </label>
            <p class="font-semibold text-[#b81a16]">
              {{ course?.course_name }} ({{ course?.course_code }})
            </p>
            <p class="text-xs text-gray-500 mt-1">
              ✅ Los estudiantes de este curso se filtrarán automáticamente en la asistencia
            </p>
          </div>

          <!-- Selector de clase programada del día -->
          <div v-if="todayScheduledClasses.length > 0">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Clase Programada de Hoy *
            </label>
            <div class="space-y-2">
              <div
                v-for="(scheduledClass, index) in todayScheduledClasses"
                :key="index"
                @click="selectScheduledClass(scheduledClass)"
                :class="[
                  'p-4 border-2 rounded-lg cursor-pointer transition-all',
                  sessionForm.selectedSchedule === scheduledClass
                    ? 'border-[#b81a16] bg-[#b81a16]/5'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                ]"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <p class="font-semibold text-gray-900">
                      {{ getDayName(scheduledClass.day_of_week) }} - {{ scheduledClass.start_time }} a {{ scheduledClass.end_time }}
                    </p>
                    <p class="text-sm text-gray-600">
                      Duración: {{ calculateClassDuration(scheduledClass.start_time, scheduledClass.end_time) }}
                    </p>
                  </div>
                  <div
                    v-if="sessionForm.selectedSchedule === scheduledClass"
                    class="h-6 w-6 rounded-full bg-[#b81a16] flex items-center justify-center text-white text-xs"
                  >
                    ✓
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Mensaje si no hay clases programadas hoy -->
          <div v-else class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div class="flex items-start gap-2">
              <span class="text-yellow-600">⚠️</span>
              <div>
                <p class="text-sm font-medium text-yellow-800">No hay clases programadas para hoy</p>
                <p class="text-xs text-yellow-700 mt-1">
                  Puedes crear una sesión manual ingresando los datos a continuación
                </p>
              </div>
            </div>
          </div>
          
          <!-- Nombre de la sesión -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Nombre de la Sesión *
            </label>
            <input
              v-model="sessionForm.name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#b81a16] focus:border-transparent"
              placeholder="Ej: Clase de Introducción"
              required
            />
          </div>

          <!-- Fecha (solo lectura si hay clase programada) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Fecha *
            </label>
            <input
              v-model="sessionForm.date"
              type="date"
              :readonly="sessionForm.selectedSchedule !== null"
              :class="[
                'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#b81a16] focus:border-transparent',
                sessionForm.selectedSchedule ? 'bg-gray-100 cursor-not-allowed' : ''
              ]"
              required
            />
          </div>

          <!-- Hora de Inicio (solo lectura si hay clase programada) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Hora de Inicio *
            </label>
            <input
              v-model="sessionForm.startTime"
              type="time"
              :readonly="sessionForm.selectedSchedule !== null"
              :class="[
                'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#b81a16] focus:border-transparent',
                sessionForm.selectedSchedule ? 'bg-gray-100 cursor-not-allowed' : ''
              ]"
              required
            />
          </div>

          <!-- Hora de Fin (opcional - si no se pone, la clase queda activa) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Hora de Fin <span class="text-gray-400 font-normal">(opcional)</span>
            </label>
            <input
              v-model="sessionForm.endTime"
              type="time"
              :readonly="sessionForm.selectedSchedule !== null"
              :class="[
                'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#b81a16] focus:border-transparent',
                sessionForm.selectedSchedule ? 'bg-gray-100 cursor-not-allowed' : ''
              ]"
            />
            <p class="text-xs text-gray-500 mt-1">
              Si no configuras hora de fin, la clase quedará activa hasta que la finalices manualmente
            </p>
          </div>

          <!-- Botones -->
          <div class="flex gap-3 mt-6">
            <button
              type="button"
              @click="showCreateSessionModal = false"
              class="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="flex-1 px-6 py-3 bg-[#b81a16] text-white rounded-lg hover:bg-[#9a1512] font-medium"
            >
              Crear Sesión
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Generar QR -->
    <div
      v-if="showQRModal"
      class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center z-50"
      @click.self="showQRModal = false"
    >
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
            <FontAwesomeIcon :icon="['fas', 'qrcode']" class="text-blue-600" />
            Asistencia por QR
          </h3>
          <button @click="showQRModal = false" class="text-gray-400 hover:text-gray-600">
            <FontAwesomeIcon :icon="['fas', 'xmark']" />
          </button>
        </div>

        <!-- Seleccionar Sesión Activa -->
        <div v-if="!selectedSessionForQR" class="space-y-4">
          <p class="text-gray-600 text-sm">Selecciona una sesión activa para generar el código QR:</p>
          
          <div v-if="allActiveSessions.length === 0" class="text-center py-8 text-gray-500">
            <div class="text-5xl mb-4 text-gray-300">
              <FontAwesomeIcon :icon="['fas', 'calendar-xmark']" />
            </div>
            <p class="text-lg mb-2">No hay sesiones activas</p>
            <p class="text-sm">Crea una sesión de clase primero</p>
            <button
              @click="showQRModal = false; openCreateSessionModal()"
              class="mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Crear Sesión
            </button>
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="session in allActiveSessions"
              :key="session.class_id"
              @click="selectSessionForQR(session)"
              class="p-4 border border-gray-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 cursor-pointer transition-all"
            >
              <p class="font-semibold text-gray-900">{{ session.class_name }}</p>
              <p class="text-sm text-gray-600">{{ formatDateTime(session.start_time) }} - {{ formatTime(session.end_time) }}</p>
              <div class="flex items-center gap-2 mt-2">
                <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded">
                  Activa
                </span>
                <span class="text-xs text-gray-500">
                  {{ calculateDuration(session.start_time, session.end_time) }} horas
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- QR Generado -->
        <div v-else class="space-y-4">
          <!-- Info de la sesión -->
          <div class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p class="font-semibold text-blue-800">{{ selectedSessionForQR.class_name }}</p>
            <p class="text-sm text-blue-600">{{ formatDateTime(selectedSessionForQR.start_time) }}</p>
          </div>

          <!-- Selector de Período -->
          <div v-if="classPeriods.length > 1" class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">
              Selecciona el Período/Hora:
            </label>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="period in classPeriods"
                :key="period.period_number"
                @click="selectedPeriod = period.period_number"
                :class="[
                  'p-3 border rounded-lg text-left transition-all',
                  selectedPeriod === period.period_number
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <p class="font-medium">Período {{ period.period_number }}</p>
                <p class="text-xs text-gray-500">
                  {{ formatTime(period.start_time) }} - {{ formatTime(period.end_time) }}
                </p>
              </button>
            </div>
          </div>

          <!-- Botón Generar -->
          <button
            @click="generateQR"
            :disabled="generatingQR"
            class="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {{ generatingQR ? 'Generando...' : 'Generar Código QR' }}
          </button>

          <!-- QR Code Display -->
          <div v-if="qrData" class="space-y-4">
            <!-- CÓDIGO ROTATIVO PROMINENTE -->
            <div class="p-6 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl text-white text-center">
              <p class="text-sm opacity-80 mb-2">CÓDIGO DE ASISTENCIA</p>
              <p class="text-5xl font-mono font-bold tracking-widest mb-3">
                {{ currentCode || qrData.current_code }}
              </p>
              <div class="flex items-center justify-center gap-2 text-sm">
                <span class="animate-pulse">⏱️</span>
                <span>Cambia en {{ codeRemainingSeconds }}s</span>
              </div>
              <p class="text-xs opacity-70 mt-2">
                Proyecta esta pantalla para que los estudiantes vean el código
              </p>
            </div>

            <!-- QR Code (opcional) -->
            <details class="border border-gray-200 rounded-lg">
              <summary class="p-3 cursor-pointer text-sm text-gray-600 hover:bg-gray-50">
                📱 Mostrar código QR (opcional)
              </summary>
              <div class="p-4 text-center border-t">
                <img :src="qrData.qr_image" alt="QR Code" class="w-48 h-48 mx-auto" />
                <p class="text-xs text-gray-500 mt-2">
                  Los estudiantes también pueden escanear este QR
                </p>
              </div>
            </details>

            <div class="text-center space-y-2">
              <p class="text-xs text-gray-500">
                Válido hasta: {{ formatDateTime(qrData.expires_at) }} • Período {{ qrData.period_number }}
              </p>
            </div>
            
            <div class="flex gap-2">
              <button
                @click="copyQRLink"
                class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm"
              >
                📋 Copiar Enlace
              </button>
              <button
                @click="downloadQR"
                class="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 text-sm"
              >
                ⬇️ Descargar QR
              </button>
            </div>
          </div>

          <button
            @click="selectedSessionForQR = null; qrData = null"
            class="w-full px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            ← Volver a seleccionar sesión
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Confirmar Finalizar Sesión -->
    <div
      v-if="sessionToEnd"
      class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center z-50"
      @click.self="sessionToEnd = null"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <div class="w-10 h-10 flex items-center justify-center bg-orange-100 text-orange-600 rounded-full">
            <FontAwesomeIcon :icon="['fas', 'stop']" />
          </div>
          Finalizar Sesión
        </h3>
        <p class="text-gray-600 mb-6">
          ¿Estás seguro de que deseas finalizar la sesión <strong>{{ sessionToEnd.class_name }}</strong>?
          Esta acción marcará la clase como terminada.
        </p>
        <div class="flex gap-3">
          <button
            @click="sessionToEnd = null"
            class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            Cancelar
          </button>
          <button
            @click="endSession"
            :disabled="endingSession"
            class="flex-1 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50"
          >
            {{ endingSession ? 'Finalizando...' : 'Finalizar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Confirmar Eliminar Sesión -->
    <div
      v-if="sessionToDelete"
      class="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center z-50"
      @click.self="sessionToDelete = null"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <div class="w-10 h-10 flex items-center justify-center bg-red-100 text-red-600 rounded-full">
            <FontAwesomeIcon :icon="['fas', 'trash']" />
          </div>
          Eliminar Sesión
        </h3>
        <p class="text-gray-600 mb-6">
          ¿Estás seguro de que deseas eliminar la sesión <strong>{{ sessionToDelete.class_name }}</strong>?
          Esta acción no se puede deshacer.
        </p>
        <div class="flex gap-3">
          <button
            @click="sessionToDelete = null"
            class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            Cancelar
          </button>
          <button
            @click="deleteSession"
            :disabled="deletingSession"
            class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {{ deletingSession ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElNotification } from 'element-plus'
import { coursesService } from '@/services/courses.service'
import { classesService } from '@/services/classes.service'
import { enrollmentsService, type EnrolledStudent, type AvailableStudent } from '@/services/enrollments.service'
import { qrService, type ClassPeriod, type QRGenerateResponse } from '@/services/qr.service'
import statisticsService from '@/services/statistics.service'
import { supabase } from '@/services/supabase'
import type { Course, ClassSession } from '@/types'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import StatsCard from '@/components/StatsCard.vue'

const route = useRoute()

const courseId = route.params.id as string

const loading = ref(true)
const course = ref<Course | null>(null)
const activeTab = ref('students')
const students = ref<EnrolledStudent[]>([])
const availableStudents = ref<AvailableStudent[]>([])
const sessions = ref<ClassSession[]>([])
const recentActivity = ref<Array<{ id: string; type: string; message: string; timestamp: string }>>([])

// Modal para añadir estudiantes
const showAddStudentModal = ref(false)
const addingStudent = ref(false)
const studentSearchQuery = ref('')

// Filtrar estudiantes disponibles por búsqueda
const filteredAvailableStudents = computed(() => {
  if (!studentSearchQuery.value.trim()) {
    return availableStudents.value
  }
  
  const query = studentSearchQuery.value.toLowerCase().trim()
  return availableStudents.value.filter(student => {
    const name = (student.name || '').toLowerCase()
    const studentId = (student.student_id || '').toLowerCase()
    const email = (student.email || '').toLowerCase()
    
    return name.includes(query) || studentId.includes(query) || email.includes(query)
  })
})

const showCreateSessionModal = ref(false)
const sessionToEnd = ref<ClassSession | null>(null)
const sessionToDelete = ref<ClassSession | null>(null)
const endingSession = ref(false)
const deletingSession = ref(false)

const sessionForm = reactive<{
  name: string
  date: string
  startTime: string
  endTime: string
  selectedSchedule: any | null
}>({
  name: '',
  date: '',
  startTime: '',
  endTime: '',
  selectedSchedule: null
})

// Resetear formulario de sesión
const resetSessionForm = () => {
  const now = new Date()
  sessionForm.name = ''
  sessionForm.date = now.toISOString().split('T')[0]
  sessionForm.startTime = now.toTimeString().slice(0, 5)
  sessionForm.endTime = ''
  sessionForm.selectedSchedule = null
}

// Clases programadas para hoy
const todayScheduledClasses = computed(() => {
  if (!course.value?.schedule || course.value.schedule.length === 0) {
    return []
  }
  
  const today = new Date()
  const dayOfWeek = today.getDay() === 0 ? 7 : today.getDay() // 1=Lunes, 7=Domingo
  
  return course.value.schedule.filter(schedule => schedule.day_of_week === dayOfWeek)
})

// QR Modal
const showQRModal = ref(false)
const selectedSessionForQR = ref<ClassSession | null>(null)
const classPeriods = ref<ClassPeriod[]>([])
const selectedPeriod = ref(1)
const generatingQR = ref(false)
const qrData = ref<QRGenerateResponse | null>(null)
const allActiveSessions = ref<ClassSession[]>([])
const currentCode = ref('')
const codeRemainingSeconds = ref(0)
let codeRefreshInterval: ReturnType<typeof setInterval> | null = null

// Verificar si una sesión está activa
const isSessionActive = (session: ClassSession): boolean => {
  const now = new Date()
  
  // Parsear start_time
  if (!session.start_time) return false
  const startTime = new Date(session.start_time)
  if (isNaN(startTime.getTime())) return false
  
  // Si aún no ha comenzado
  if (now < startTime) return false
  
  // Verificar end_time - puede ser null, undefined, o string vacío
  const endTimeValue = session.end_time
  if (!endTimeValue || endTimeValue === '' || endTimeValue === 'null') {
    // Sin hora de fin = activa indefinidamente (ya comenzó)
    return true
  }
  
  const endTime = new Date(endTimeValue)
  if (isNaN(endTime.getTime())) {
    // end_time inválido = tratar como activa
    return true
  }
  
  // Activa si: ahora < fin
  return now < endTime
}

// Sesiones activas del curso actual
const activeSessions = computed(() => {
  return sessions.value.filter(session => isSessionActive(session))
})

const stats = ref({
  totalStudents: 0,
  totalSessions: 0,
  avgAttendance: 0,
  avgEngagement: 0
})

const tabs = [
  { id: 'students', label: 'Estudiantes', icon: 'users' },
  { id: 'sessions', label: 'Sesiones', icon: 'calendar-days' },
  { id: 'activity', label: 'Actividad', icon: 'chart-bar' }
]

const loadCourseData = async () => {
  loading.value = true
  try {
    // Load course
    course.value = await coursesService.getCourse(courseId)

    // Load students enrolled in this course using enrollments service
    students.value = await enrollmentsService.getCourseStudents(courseId)
    stats.value.totalStudents = students.value.length

    // Load sessions of this course only
    // Note: course_id is stored in metadata field
    const { data: allSessionsData } = await supabase
      .from('class_sessions')
      .select('*')
      .order('created_at', { ascending: false })
    
    // Filter sessions by course_id in metadata
    sessions.value = (allSessionsData || []).filter(session => {
      const metadata = session.metadata as { course_id?: string } | null
      return metadata?.course_id === courseId
    })
    stats.value.totalSessions = sessions.value.length

    // Cargar estadísticas reales del curso (usando UUID, no int)
    try {
      const courseStats = await statisticsService.getCourseStats(courseId as any)
      stats.value.avgAttendance = courseStats.avgAttendance || 0
      stats.value.avgEngagement = courseStats.avgEngagement || 0
    } catch {
      stats.value.avgAttendance = 0
      stats.value.avgEngagement = 0
    }

    // Mock activity
    recentActivity.value = [
      {
        id: '1',
        type: 'session',
        message: 'Sesiones de clase registradas',
        timestamp: new Date().toISOString()
      },
      {
        id: '2',
        type: 'student',
        message: `${students.value.length} estudiantes en esta materia`,
        timestamp: new Date().toISOString()
      }
    ]
  } catch {
    // Error loading course data
  } finally {
    loading.value = false
  }
}

// Cargar estudiantes disponibles para inscribir
const loadAvailableStudents = async () => {
  try {
    availableStudents.value = await enrollmentsService.getAvailableStudents(courseId)
  } catch {
    // Error loading available students
  }
}

// Inscribir estudiante al curso
const enrollStudent = async (studentId: string) => {
  addingStudent.value = true
  try {
    await enrollmentsService.enrollStudent(studentId, courseId)
    ElNotification({
      title: 'Éxito',
      message: 'Estudiante inscrito exitosamente',
      type: 'success'
    })
    // Recargar datos
    await loadCourseData()
    await loadAvailableStudents()
  } catch (error: any) {
    ElNotification({
      title: 'Error',
      message: error.response?.data?.detail || 'Error al inscribir estudiante',
      type: 'error'
    })
  } finally {
    addingStudent.value = false
  }
}

// Desinscribir estudiante del curso
const unenrollStudent = async (studentId: string, studentName: string) => {
  if (!confirm(`¿Seguro que deseas quitar a ${studentName} de esta materia?`)) return
  
  try {
    await enrollmentsService.unenrollStudent(courseId, studentId)
    ElNotification({
      title: 'Éxito',
      message: 'Estudiante removido de la materia',
      type: 'success'
    })
    await loadCourseData()
  } catch (error: any) {
    ElNotification({
      title: 'Error',
      message: error.response?.data?.detail || 'Error al remover estudiante',
      type: 'error'
    })
  }
}

// Abrir modal de añadir estudiantes
const openAddStudentModal = async () => {
  studentSearchQuery.value = '' // Resetear búsqueda
  await loadAvailableStudents()
  showAddStudentModal.value = true
}

const createSession = async () => {
  if (!course.value) {
    ElNotification({
      title: 'Error',
      message: 'No se pudo cargar la información del curso',
      type: 'error'
    })
    return
  }
  
  if (!sessionForm.name || !sessionForm.date || !sessionForm.startTime) {
    ElNotification({
      title: 'Error',
      message: 'Completa todos los campos requeridos',
      type: 'warning'
    })
    return
  }

  try {
    loading.value = true
    
    // Crear la sesión usando el servicio de clases con course_id para filtrado
    // Solo enviar end_time si tiene valor (para que la clase quede activa indefinidamente)
    const classData: any = {
      class_name: sessionForm.name.trim(),
      session_date: sessionForm.date,
      start_time: sessionForm.startTime,
      course_id: courseId
    }
    
    // Solo agregar end_time si el usuario lo configuró
    if (sessionForm.endTime && sessionForm.endTime.trim() !== '') {
      classData.end_time = sessionForm.endTime
    }
    
    const response = await classesService.createClass(classData)

    if (response.success || response.class_id) {
      ElNotification({
        title: 'Éxito',
        message: `Sesión "${sessionForm.name}" creada exitosamente`,
        type: 'success'
      })
      
      // Resetear formulario para poder crear más sesiones
      resetSessionForm()
      showCreateSessionModal.value = false
      
      // Recargar los datos
      await loadCourseData()
    } else {
      ElNotification({
        title: 'Error',
        message: 'Error al crear la sesión. Intenta de nuevo.',
        type: 'error'
      })
    }
  } catch (error: any) {
    ElNotification({
      title: 'Error',
      message: error.response?.data?.detail || error.message || 'No se pudo crear la sesión',
      type: 'error'
    })
  } finally {
    loading.value = false
  }
}

// Confirmar finalizar sesión
const confirmEndSession = (session: ClassSession) => {
  sessionToEnd.value = session
}

// Finalizar sesión
const endSession = async () => {
  if (!sessionToEnd.value) return
  
  endingSession.value = true
  try {
    // Usar class_id (UUID) en lugar de id (número)
    const classId = sessionToEnd.value.class_id || sessionToEnd.value.id.toString()
    await classesService.endClass(classId)
    ElNotification({
      title: 'Éxito',
      message: `Sesión "${sessionToEnd.value.class_name}" finalizada`,
      type: 'success'
    })
    sessionToEnd.value = null
    await loadCourseData()
  } catch (error: any) {
    ElNotification({
      title: 'Error',
      message: error.response?.data?.detail || 'Error al finalizar la sesión',
      type: 'error'
    })
  } finally {
    endingSession.value = false
  }
}

// Confirmar eliminar sesión
const confirmDeleteSession = (session: ClassSession) => {
  sessionToDelete.value = session
}

// Eliminar sesión
const deleteSession = async () => {
  if (!sessionToDelete.value) return
  
  deletingSession.value = true
  try {
    // Usar class_id (UUID) en lugar de id (número)
    const classId = sessionToDelete.value.class_id || sessionToDelete.value.id.toString()
    await classesService.deleteClass(classId)
    ElNotification({
      title: 'Éxito',
      message: `Sesión "${sessionToDelete.value.class_name}" eliminada`,
      type: 'success'
    })
    sessionToDelete.value = null
    await loadCourseData()
  } catch (error: any) {
    ElNotification({
      title: 'Error',
      message: error.response?.data?.detail || 'Error al eliminar la sesión',
      type: 'error'
    })
  } finally {
    deletingSession.value = false
  }
}

const getInitials = (name: string) => {
  const names = name.split(' ').filter(n => n.length > 0)
  if (names.length === 0) return 'U'
  return names.length > 1
    ? (names[0]?.[0] || '') + (names[1]?.[0] || '')
    : (names[0]?.[0] || 'U')
}

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-EC', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'America/Guayaquil'
  }).format(date)
}

const selectScheduledClass = (schedule: any) => {
  sessionForm.selectedSchedule = schedule
  
  const now = new Date()
  const tzOffset = now.getTimezoneOffset() * 60000
  const localDate = new Date(now.getTime() - tzOffset).toISOString().slice(0, 10)
  
  sessionForm.date = localDate
  sessionForm.startTime = schedule.start_time
  sessionForm.endTime = schedule.end_time
  sessionForm.name = `Clase de ${course.value?.course_name || 'Materia'}`
}

const calculateClassDuration = (startTime: string, endTime: string): string => {
  const [startHour, startMin] = startTime.split(':').map(Number)
  const [endHour, endMin] = endTime.split(':').map(Number)
  
  const startMinutes = (startHour || 0) * 60 + (startMin || 0)
  const endMinutes = (endHour || 0) * 60 + (endMin || 0)
  const durationMinutes = endMinutes - startMinutes
  
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60
  
  if (hours > 0 && minutes > 0) {
    return `${hours}h ${minutes}min`
  } else if (hours > 0) {
    return `${hours}h`
  } else {
    return `${minutes}min`
  }
}

const getDayName = (dayOfWeek: number): string => {
  const days = ['', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
  return days[dayOfWeek] || ''
}

const openCreateSessionModal = () => {
  const now = new Date()
  const tzOffset = now.getTimezoneOffset() * 60000
  const localDate = new Date(now.getTime() - tzOffset).toISOString().slice(0, 10)
  const localTime = new Date(now.getTime() - tzOffset).toISOString().slice(11, 16)
  
  sessionForm.name = `Clase de ${course.value?.course_name || 'Materia'}`
  sessionForm.date = localDate
  sessionForm.startTime = localTime
  sessionForm.endTime = ''
  sessionForm.selectedSchedule = null
  
  // Auto-seleccionar la primera clase programada del día si existe
  if (todayScheduledClasses.value.length > 0) {
    selectScheduledClass(todayScheduledClasses.value[0])
  }
  
  showCreateSessionModal.value = true
}

// === QR Functions ===
const openQRModal = async () => {
  selectedSessionForQR.value = null
  classPeriods.value = []
  selectedPeriod.value = 1
  qrData.value = null
  
  // Cargar TODAS las sesiones activas (no solo las del curso)
  try {
    const response = await classesService.getActiveClasses()
    allActiveSessions.value = response || []
  } catch {
    allActiveSessions.value = []
  }
  
  showQRModal.value = true
}

const selectSessionForQR = async (session: ClassSession) => {
  selectedSessionForQR.value = session
  selectedPeriod.value = 1
  qrData.value = null
  
  // Load periods for this session
  try {
    const periodsData = await qrService.getClassPeriods(session.class_id)
    classPeriods.value = periodsData.periods
    
    // Set current period if available
    if (periodsData.current_period) {
      selectedPeriod.value = periodsData.current_period.period_number
    }
  } catch {
    // Default to single period
    classPeriods.value = [{
      period_number: 1,
      start_time: session.start_time,
      end_time: session.end_time,
      late_threshold: session.start_time,
      duration_minutes: 60
    }]
  }
}

const generateQR = async () => {
  if (!selectedSessionForQR.value) return
  
  generatingQR.value = true
  try {
    const result = await qrService.generateQR({
      class_id: selectedSessionForQR.value.class_id,
      period_number: selectedPeriod.value,
      base_url: window.location.origin
    })
    qrData.value = result
    currentCode.value = result.current_code
    codeRemainingSeconds.value = result.code_remaining_seconds
    
    // Start code refresh timer
    startCodeRefreshTimer()
    
    ElNotification({
      title: 'QR Generado',
      message: `Código de asistencia generado: ${result.current_code}`,
      type: 'success'
    })
  } catch (error: any) {
    ElNotification({
      title: 'Error',
      message: error.response?.data?.detail || 'Error al generar QR',
      type: 'error'
    })
  } finally {
    generatingQR.value = false
  }
}

const startCodeRefreshTimer = () => {
  // Clear existing interval
  if (codeRefreshInterval) {
    clearInterval(codeRefreshInterval)
  }
  
  // Update every second
  codeRefreshInterval = setInterval(async () => {
    if (codeRemainingSeconds.value > 0) {
      codeRemainingSeconds.value--
    } else {
      // Code expired, fetch new one
      if (selectedSessionForQR.value) {
        try {
          const result = await qrService.generateQR({
            class_id: selectedSessionForQR.value.class_id,
            period_number: selectedPeriod.value,
            base_url: window.location.origin
          })
          currentCode.value = result.current_code
          codeRemainingSeconds.value = result.code_remaining_seconds
        } catch {
          // Error refreshing code
        }
      }
    }
  }, 1000)
}

const stopCodeRefreshTimer = () => {
  if (codeRefreshInterval) {
    clearInterval(codeRefreshInterval)
    codeRefreshInterval = null
  }
}

const copyQRLink = () => {
  if (!qrData.value?.qr_url) return
  navigator.clipboard.writeText(qrData.value.qr_url)
  ElNotification({
    title: 'Copiado',
    message: 'Enlace copiado al portapapeles',
    type: 'success'
  })
}

const downloadQR = () => {
  if (!qrData.value?.qr_image) return
  
  const link = document.createElement('a')
  link.download = `qr-asistencia-${selectedSessionForQR.value?.class_name || 'clase'}-periodo-${selectedPeriod.value}.png`
  link.href = qrData.value.qr_image
  link.click()
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('es-EC', { 
    hour: '2-digit', 
    minute: '2-digit',
    timeZone: 'America/Guayaquil'
  })
}

const calculateDuration = (startTime: string, endTime: string) => {
  const start = new Date(startTime)
  const end = new Date(endTime)
  return Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60))
}

onMounted(() => {
  loadCourseData()
})

onUnmounted(() => {
  stopCodeRefreshTimer()
})
</script>
