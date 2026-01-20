/**
 * Smart Classroom AI - Attendance Service
 */

import apiClient from './api'
import type { AttendanceRequest, AttendanceResponse, AttendanceRecord } from '@/types'

export const attendanceService = {
  /**
   * Verify student attendance with facial recognition
   */
  async verifyAttendance(data: AttendanceRequest | FormData): Promise<any> {
    let formData: FormData
    
    // Si ya es FormData, usarlo directamente
    if (data instanceof FormData) {
      formData = data
    } else {
      // Si no, construir el FormData
      formData = new FormData()
      formData.append('class_id', data.class_id.toString())
      formData.append('image', data.image)
    }

    const response = await apiClient.post(
      '/attendance/verify',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    )
    
    // Backend returns { success, message, data: { student_id, student_name, ... } }
    return response.data?.data || response.data
  },

  /**
   * Get attendance records for a specific class
   */
  async getClassAttendance(classId: number): Promise<AttendanceRecord[]> {
    const response = await apiClient.get<any>(
      `/attendance/class/${classId}`
    )
    // Backend returns { success, message, data: { records: [...] } }
    return response.data?.data?.records || []
  },

  /**
   * Get attendance records for a specific student
   */
  async getStudentAttendance(studentId: number): Promise<AttendanceRecord[]> {
    const response = await apiClient.get<AttendanceRecord[]>(
      `/attendance/student/${studentId}`
    )
    return response.data
  },

  /**
   * Get attendance statistics for a class
   */
  async getClassStats(classId: number): Promise<{
    total_students: number
    present: number
    absent: number
    attendance_rate: number
  }> {
    const response = await apiClient.get(`/attendance/class/${classId}/stats`)
    return response.data
  },

  /**
   * Register manual attendance for a student
   */
  async registerManualAttendance(data: {
    class_id: string
    student_id: string
    status: string
    period?: number
  }): Promise<any> {
    const response = await apiClient.post('/attendance/manual', {
      class_id: data.class_id,
      student_id: data.student_id,
      status: data.status,
      period: data.period || 1
    })
    return response.data
  }
}
