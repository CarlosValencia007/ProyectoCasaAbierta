/**
 * Smart Classroom AI - Enrollment Service
 */

import apiClient from './api'
import type { EnrollmentRequest, EnrollmentResponse, Student } from '@/types'

export const enrollmentService = {
  /**
   * Enroll a new student with facial recognition
   */
  async enrollStudent(data: EnrollmentRequest & { course_id?: string }): Promise<EnrollmentResponse> {
    const formData = new FormData()
    formData.append('student_id', data.student_id)
    formData.append('name', data.name)
    formData.append('email', data.email)
    formData.append('image', data.image)
    
    // Add course_id if provided
    if (data.course_id) {
      formData.append('course_id', data.course_id)
    }

    const response = await apiClient.post<EnrollmentResponse>(
      '/enrollment/enroll',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    )
    
    return response.data
  },

  /**
   * Get all enrolled students
   */
  async getStudents(): Promise<Student[]> {
    const response = await apiClient.get<any>('/enrollment/students')
    // Backend returns { success, message, data: { students: [...] } }
    return response.data?.data?.students || []
  },

  /**
   * Get a specific student by ID
   */
  async getStudent(studentId: number): Promise<Student> {
    const response = await apiClient.get<Student>(`/enrollment/students/${studentId}`)
    return response.data
  },

  /**
   * Delete a student
   */
  async deleteStudent(studentId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete<any>(`/enrollment/students/${studentId}`)
    return response.data
  },

  /**
   * Update student information
   */
  async updateStudent(
    studentId: number,
    data: Partial<{ name: string; email: string; student_id: string }>
  ): Promise<Student> {
    const response = await apiClient.put<Student>(
      `/enrollment/students/${studentId}`,
      data
    )
    return response.data
  }
}
