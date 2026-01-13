/**
 * Smart Classroom AI - Classes Service
 */

import apiClient from './api'
import type { ClassSession, ClassCreateRequest, ClassCreateResponse } from '@/types'

export const classesService = {
  /**
   * Create a new class session
   */
  async createClass(data: ClassCreateRequest): Promise<ClassCreateResponse> {
    const response = await apiClient.post<ClassCreateResponse>(
      '/classes/create',
      data
    )
    return response.data
  },

  /**
   * Get all class sessions
   */
  async getClasses(): Promise<ClassSession[]> {
    const response = await apiClient.get<any>('/classes')
    // Backend returns { success, message, data: { classes: [...] } }
    return response.data?.data?.classes || []
  },

  /**
   * Get active classes (end_time is null)
   */
  async getActiveClasses(): Promise<ClassSession[]> {
    const response = await apiClient.get<any>('/classes/active')
    // Backend returns { success, message, data: { classes: [...] } }
    return response.data?.data?.classes || []
  },

  /**
   * Get a specific class by ID
   */
  async getClass(classId: number): Promise<ClassSession> {
    const response = await apiClient.get<ClassSession>(`/classes/${classId}`)
    return response.data
  },

  /**
   * End a class session
   */
  async endClass(classId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post<any>(`/classes/${classId}/end`)
    return response.data
  },

  /**
   * Delete a class session
   */
  async deleteClass(classId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete(`/classes/${classId}`)
    return response.data
  }
}
