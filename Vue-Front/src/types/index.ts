/**
 * Smart Classroom AI - TypeScript Types & Interfaces
 */

// ============================================================================
// Database Types
// ============================================================================

export interface Course {
  id: string  // UUID from Supabase
  course_name: string
  course_code: string
  description?: string
  teacher_id?: string
  created_at: string
}

export interface Student {
  id: number
  student_id: string
  name: string
  email: string
  photo_url: string | null
  embedding: number[] | null
  course_id?: number
  created_at: string
}

export interface ClassSession {
  id: number
  class_name: string
  course_id?: number
  start_time: string
  end_time: string | null
  created_at: string
}

export interface AttendanceRecord {
  id: number
  student_id: number
  class_id: number
  timestamp: string
  confidence_score: number
  student?: Student
}

export interface EmotionLog {
  id: number
  student_id: number
  class_id: number
  emotion: string
  confidence: number
  timestamp: string
  student?: Student
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface EnrollmentRequest {
  student_id: string
  name: string
  email: string
  image: File
}

export interface EnrollmentResponse {
  success: boolean
  message: string
  student_id: number
  photo_url: string
}

export interface AttendanceRequest {
  class_id: number
  image: File
}

export interface AttendanceResponse {
  success: boolean
  message: string
  student_id: number
  student_name: string
  confidence: number
  attendance_id: number
}

export interface EmotionRequest {
  class_id: string | number
  image: File
}

export interface EmotionResponse {
  success: boolean
  emotions: Array<{
    student_id?: number
    student_name?: string
    emotion: string
    confidence: number
  }>
}

export interface ClassCreateRequest {
  class_id: string
  class_name: string
  course_id?: string
  start_time: string
  end_time?: string
  instructor?: string
  room?: string
  metadata?: Record<string, any>
}

export interface ClassCreateResponse {
  success: boolean
  message: string
  class_id: number
}

// ============================================================================
// Auth Types
// ============================================================================

export interface UserProfile {
  id: string
  email: string
  full_name: string
  role: 'teacher' | 'admin'
}

// ============================================================================
// UI Types
// ============================================================================

export interface DashboardStats {
  totalStudents: number
  activeClasses: number
  avgAttendance: number
  avgEngagement: number
}

export type EmotionType = 'happy' | 'sad' | 'angry' | 'surprise' | 'fear' | 'disgust' | 'neutral'

export interface EmotionStats {
  emotion: EmotionType
  count: number
  percentage: number
}
