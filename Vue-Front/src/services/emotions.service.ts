/**
 * Smart Classroom AI - Emotions Service
 */

import apiClient from './api'
import type { EmotionRequest, EmotionResponse, EmotionLog } from '@/types'

export const emotionsService = {
  /**
   * Analyze emotions from classroom image
   */
  async analyzeEmotion(data: EmotionRequest & { student_id?: string }): Promise<EmotionResponse> {
    const formData = new FormData()
    formData.append('class_id', data.class_id.toString())
    formData.append('image', data.image)
    
    if (data.student_id) {
      formData.append('student_id', data.student_id)
    }

    const response = await apiClient.post(
      '/emotions/analyze',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    )
    
    return response.data
  },

  /**
   * Get emotion logs for a specific class
   */
  async getClassEmotions(classId: number): Promise<EmotionLog[]> {
    const response = await apiClient.get(
      `/emotions/class/${classId}`
    )
    return response.data?.data?.logs || []
  },

  /**
   * Get emotion statistics for a class
   */
  async getClassEmotionStats(classId: number): Promise<{
    total_logs: number
    emotion_distribution: Record<string, number>
    engagement_score: number
  }> {
    const response = await apiClient.get(`/emotions/class/${classId}/stats`)
    return response.data
  },

  /**
   * Get emotion timeline for a class
   */
  async getEmotionTimeline(classId: number): Promise<{
    timestamp: string
    emotion: string
    count: number
  }[]> {
    const response = await apiClient.get(`/emotions/class/${classId}/timeline`)
    return response.data
  }
}
