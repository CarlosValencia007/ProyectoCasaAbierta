/**
 * Smart Classroom AI - Courses Service
 */

import { supabase } from './supabase'
import type { Course } from '@/types'

export const coursesService = {
  /**
   * Create a new course (Supabase)
   */
  async createCourse(data: { course_name: string; course_code: string; description?: string }): Promise<Course> {
    const { data: { user } } = await supabase.auth.getUser()
    
    const { data: course, error } = await supabase
      .from('courses')
      .insert({
        course_name: data.course_name,
        course_code: data.course_code,
        description: data.description,
        teacher_id: user?.id
      })
      .select()
      .single()

    if (error) throw error
    return course
  },

  /**
   * Get all courses for current teacher
   */
  async getMyCourses(): Promise<Course[]> {
    const { data: { user } } = await supabase.auth.getUser()
    
    const { data, error } = await supabase
      .from('courses')
      .select('*')
      .eq('teacher_id', user?.id)
      .order('created_at', { ascending: false })

    if (error) throw error
    return data || []
  },

  /**
   * Get a specific course
   */
  async getCourse(courseId: string): Promise<Course> {
    const { data, error } = await supabase
      .from('courses')
      .select('*')
      .eq('id', courseId)
      .single()

    if (error) throw error
    return data
  },

  /**
   * Update course
   */
  async updateCourse(courseId: string, updates: Partial<Course>): Promise<Course> {
    const { data, error } = await supabase
      .from('courses')
      .update(updates)
      .eq('id', courseId)
      .select()
      .single()

    if (error) throw error
    return data
  },

  /**
   * Delete course
   */
  async deleteCourse(courseId: string): Promise<void> {
    const { error } = await supabase
      .from('courses')
      .delete()
      .eq('id', courseId)

    if (error) throw error
  }
}
