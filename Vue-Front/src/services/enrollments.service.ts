/**
 * Smart Classroom AI - Enrollments Service
 * Gestión de inscripciones de estudiantes en cursos
 */

import apiClient from './api'

export interface EnrolledStudent {
  enrollment_id: number
  student_id: string
  name: string
  email?: string
  photo_url?: string
  is_active: boolean
  enrolled_at: string
}

export interface AvailableStudent {
  student_id: string
  name: string
  email?: string
  photo_url?: string
}

export const enrollmentsService = {
  /**
   * Inscribir un estudiante en un curso
   */
  async enrollStudent(studentId: string, courseId: string): Promise<any> {
    const response = await apiClient.post('/enrollments', {
      student_id: studentId,
      course_id: courseId
    })
    return response.data
  },

  /**
   * Desinscribir un estudiante de un curso
   */
  async unenrollStudent(courseId: string, studentId: string): Promise<any> {
    const response = await apiClient.delete(`/enrollments/${courseId}/${studentId}`)
    return response.data
  },

  /**
   * Obtener estudiantes inscritos en un curso
   */
  async getCourseStudents(courseId: string): Promise<EnrolledStudent[]> {
    const response = await apiClient.get(`/enrollments/course/${courseId}`)
    return response.data?.data?.students || []
  },

  /**
   * Obtener estudiantes disponibles para inscribir (no inscritos en el curso)
   */
  async getAvailableStudents(courseId: string): Promise<AvailableStudent[]> {
    const response = await apiClient.get(`/enrollments/available/${courseId}`)
    return response.data?.data?.students || []
  },

  /**
   * Obtener cursos de un estudiante
   */
  async getStudentCourses(studentId: string): Promise<any[]> {
    const response = await apiClient.get(`/enrollments/student/${studentId}`)
    return response.data?.data?.courses || []
  }
}
