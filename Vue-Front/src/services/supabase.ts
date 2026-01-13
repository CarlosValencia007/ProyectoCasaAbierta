/**
 * Smart Classroom AI - Supabase Client Configuration
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

// Database type definition
export type Database = {
  public: {
    Tables: {
      students: {
        Row: {
          id: number
          student_id: string
          name: string
          email: string
          photo_url: string | null
          embedding: number[] | null
          created_at: string
        }
        Insert: {
          student_id: string
          name: string
          email: string
          photo_url?: string | null
          embedding?: number[] | null
        }
        Update: {
          student_id?: string
          name?: string
          email?: string
          photo_url?: string | null
          embedding?: number[] | null
        }
      }
      class_sessions: {
        Row: {
          id: number
          class_name: string
          start_time: string
          end_time: string | null
          created_at: string
        }
        Insert: {
          class_name: string
          start_time?: string
        }
        Update: {
          class_name?: string
          end_time?: string | null
        }
      }
      attendance_records: {
        Row: {
          id: number
          student_id: number
          class_id: number
          timestamp: string
          confidence_score: number
        }
        Insert: {
          student_id: number
          class_id: number
          confidence_score: number
        }
      }
      emotion_logs: {
        Row: {
          id: number
          student_id: number
          class_id: number
          emotion: string
          confidence: number
          timestamp: string
        }
        Insert: {
          student_id: number
          class_id: number
          emotion: string
          confidence: number
        }
      }
    }
  }
}
