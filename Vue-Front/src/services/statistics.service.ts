import apiClient from './api'

export interface DashboardStats {
  totalStudents: number
  activeClasses: number
  avgAttendance: number
  avgEngagement: number
  totalClasses: number
  totalAttendances: number
  totalEmotions: number
}

export interface CourseStats {
  avgAttendance: number
  avgEngagement: number
  totalClasses: number
  totalAttendances: number
  totalEmotions: number
  enrolledStudents: number
}

class StatisticsService {
  /**
   * Get dashboard statistics
   */
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await apiClient.get('/statistics/dashboard')
    return response.data?.data || response.data
  }

  /**
   * Get course statistics
   */
  async getCourseStats(courseId: number): Promise<CourseStats> {
    const response = await apiClient.get(`/statistics/course/${courseId}`)
    return response.data?.data || response.data
  }
}

export default new StatisticsService()
